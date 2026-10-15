/**
 * OmniRoute AI Gateway Starter & Health Checker
 * Spawns the OmniRoute gateway on port 20128 and monitors its health.
 */
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

// Load .env if present
const envPath = path.resolve(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const [key, ...vals] = trimmed.split('=');
      if (key && vals.length) {
        process.env[key.trim()] = vals.join('=').trim();
      }
    }
  });
}

const PORT = parseInt(process.env.OMNIROUTE_PORT || '20128', 10);
const HOST = process.env.OMNIROUTE_HOST || '127.0.0.1';
const PASSWORD = process.env.OMNIROUTE_PASSWORD || 'admin123456';

async function checkGatewayHealth() {
  return new Promise((resolve) => {
    const req = http.get({
      host: HOST,
      port: PORT,
      path: '/v1/models',
      timeout: 2000
    }, (res) => {
      resolve(res.statusCode >= 200 && res.statusCode < 500);
    });

    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function main() {
  console.log(`[OmniRoute Launcher] Checking if OmniRoute is already running on ${HOST}:${PORT}...`);
  const isHealthy = await checkGatewayHealth();

  if (isHealthy) {
    console.log(`[OmniRoute Launcher] OmniRoute is ALREADY running and healthy on http://${HOST}:${PORT}`);
    console.log(`[OmniRoute Launcher] OpenAI-compatible endpoint: http://${HOST}:${PORT}/v1`);
    console.log(`[OmniRoute Launcher] Web Management Dashboard: http://${HOST}:${PORT}`);
    return;
  }

  const isWindows = process.platform === 'win32';
  const localBin = path.resolve(__dirname, '..', 'node_modules', '.bin', isWindows ? 'omniroute.cmd' : 'omniroute');
  const hasLocal = fs.existsSync(localBin);

  console.log(`[OmniRoute Launcher] Starting OmniRoute on port ${PORT}...`);
  if (hasLocal) {
    console.log(`[OmniRoute Launcher] Using local binary: ${localBin}`);
  }

  const env = {
    ...process.env,
    PORT: PORT.toString(),
    INITIAL_PASSWORD: PASSWORD
  };

  let cmd, args;
  const omniArgs = ['--port', PORT.toString(), '--no-open'];
  if (hasLocal) {
    cmd = isWindows ? 'cmd.exe' : localBin;
    args = isWindows ? ['/c', localBin, ...omniArgs] : omniArgs;
  } else {
    cmd = isWindows ? 'cmd.exe' : 'npx';
    args = isWindows ? ['/c', 'npx', '-y', 'omniroute', ...omniArgs] : ['-y', 'omniroute', ...omniArgs];
  }

  const proc = spawn(cmd, args, {
    env,
    stdio: 'inherit',
    shell: false
  });

  proc.on('error', (err) => {
    console.error(`[OmniRoute Launcher] Failed to start process:`, err);
  });

  proc.on('exit', (code) => {
    console.log(`[OmniRoute Launcher] OmniRoute process exited with code ${code}`);
  });

  // Poll for health
  let attempts = 0;
  const interval = setInterval(async () => {
    attempts++;
    const ready = await checkGatewayHealth();
    if (ready) {
      clearInterval(interval);
      console.log(`\n======================================================`);
      console.log(`🚀 OmniRoute AI Gateway is READY and LISTENING!`);
      console.log(`📍 Endpoint: http://${HOST}:${PORT}/v1`);
      console.log(`📊 Dashboard: http://${HOST}:${PORT}`);
      console.log(`🔑 Initial Password: ${PASSWORD}`);
      console.log(`======================================================\n`);
    } else if (attempts > 30) {
      clearInterval(interval);
      console.log(`[OmniRoute Launcher] Health check timeout. Process is still running.`);
    }
  }, 1000);
}

if (require.main === module) {
  main();
}

module.exports = { checkGatewayHealth, PORT, HOST };
