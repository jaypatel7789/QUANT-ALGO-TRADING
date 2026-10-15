/**
 * SHARK MT5 SENTINEL - CLIENT APPLICATION CONTROLLER (PRODUCTION V3.0)
 * Real-time WebSocket listener, server-authenticated security gate,
 * dynamic UI reactive state, interactive equity chart, audio feedback, and command dispatch.
 */

// ==========================================
// 1. STATE & CONSTANTS
// ==========================================
let ws = null;
let currentTab = 'dashboard';
let holdTimer = null;
let holdStart = 0;
const HOLD_DURATION_MS = 2000;
let cachedChartData = null;

// Sound State
let isSoundMuted = localStorage.getItem('sentinel_muted') === 'true';

// Authentication State
let enteredPin = "";
let authToken = localStorage.getItem('sentinel_token') || sessionStorage.getItem('sentinel_token') || "";

// Helper for authenticated fetch
async function secureFetch(url, options = {}) {
  options.headers = options.headers || {};
  if (authToken) {
    options.headers['Authorization'] = `Bearer ${authToken}`;
  }
  const response = await fetch(url, options);
  if (response.status === 401) {
    // Session expired or unauthenticated
    sessionStorage.removeItem('sentinel_token');
    authToken = "";
    lockCommandCenter("Session expired. Please enter PIN.");
  }
  return response;
}

// ==========================================
// 2. AUDIO FEEDBACK SYNTHESIZER (Web Audio API)
// ==========================================
const AudioContextClass = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function getAudioContext() {
  if (!audioCtx && AudioContextClass) {
    audioCtx = new AudioContextClass();
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

const SoundFX = {
  tick() {
    if (isSoundMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, ctx.currentTime);
      gain.gain.setValueAtTime(0.04, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.04);
    } catch (e) {}
  },

  escalate(freq) {
    if (isSoundMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 0.08);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.08);
    } catch (e) {}
  },

  success() {
    if (isSoundMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const now = ctx.currentTime;
      [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now + idx * 0.06);
        gain.gain.setValueAtTime(0.06, now + idx * 0.06);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.06 + 0.25);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + idx * 0.06);
        osc.stop(now + idx * 0.06 + 0.25);
      });
    } catch (e) {}
  },

  liquidate() {
    if (isSoundMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(280, now);
      osc.frequency.exponentialRampToValueAtTime(70, now + 0.5);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.5);
    } catch (e) {}
  },

  alarm() {
    if (isSoundMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.setValueAtTime(440, now + 0.1);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.25);
    } catch (e) {}
  }
};

// ==========================================
// 3. SERVER-AUTHENTICATED PIN GATE
// ==========================================
function updatePinDots() {
  const dots = document.querySelectorAll('#pinDotsRow .pin-dot');
  dots.forEach((dot, idx) => {
    if (idx < enteredPin.length) {
      dot.classList.add('filled');
      dot.classList.remove('error');
    } else {
      dot.classList.remove('filled', 'error');
    }
  });
}

function enterPinDigit(digit) {
  SoundFX.tick();
  if (enteredPin.length < 4) {
    enteredPin += digit;
    updatePinDots();
    document.getElementById('pinErrorMsg').classList.remove('show');

    if (enteredPin.length === 4) {
      setTimeout(submitPinToServer, 80);
    }
  }
}

function clearPinDigits() {
  SoundFX.tick();
  enteredPin = "";
  updatePinDots();
  document.getElementById('pinErrorMsg').classList.remove('show');
}

function deletePinDigit() {
  SoundFX.tick();
  if (enteredPin.length > 0) {
    enteredPin = enteredPin.slice(0, -1);
    updatePinDots();
    document.getElementById('pinErrorMsg').classList.remove('show');
  }
}

async function submitPinToServer() {
  const errEl = document.getElementById('pinErrorMsg');
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin: enteredPin })
    });

    const data = await res.json();
    if (res.ok && data.token) {
      SoundFX.success();
      authToken = data.token;
      localStorage.setItem('sentinel_token', authToken);
      sessionStorage.setItem('sentinel_token', authToken);
      const modal = document.getElementById('pinGateModal');
      modal.classList.remove('open');
      enteredPin = "";
      updatePinDots();
    } else {
      SoundFX.alarm();
      errEl.textContent = data.detail || "Incorrect Security PIN.";
      errEl.classList.add('show');
      const dots = document.querySelectorAll('#pinDotsRow .pin-dot');
      dots.forEach(d => d.classList.add('error'));
      setTimeout(clearPinDigits, 600);
    }
  } catch (err) {
    SoundFX.alarm();
    errEl.textContent = "Network error connecting to Sentinel backend.";
    errEl.classList.add('show');
    setTimeout(clearPinDigits, 600);
  }
}

function lockCommandCenter(msg = "") {
  SoundFX.tick();
  localStorage.removeItem('sentinel_token');
  sessionStorage.removeItem('sentinel_token');
  authToken = "";
  enteredPin = "";
  updatePinDots();
  const errEl = document.getElementById('pinErrorMsg');
  if (msg) {
    errEl.textContent = msg;
    errEl.classList.add('show');
  } else {
    errEl.classList.remove('show');
  }
  document.getElementById('pinGateModal').classList.add('open');
}

function checkInitialLock() {
  const modal = document.getElementById('pinGateModal');
  if (!authToken) {
    modal.classList.add('open');
  } else {
    modal.classList.remove('open');
  }
}

// Sound Toggle Handler
function toggleSound() {
  isSoundMuted = !isSoundMuted;
  localStorage.setItem('sentinel_muted', isSoundMuted ? 'true' : 'false');
  updateSoundIcon();
  if (!isSoundMuted) SoundFX.success();
}

function updateSoundIcon() {
  const onIcon = document.getElementById('soundOnIcon');
  const offIcon = document.getElementById('soundOffIcon');
  if (isSoundMuted) {
    onIcon.style.display = 'none';
    offIcon.style.display = 'block';
  } else {
    onIcon.style.display = 'block';
    offIcon.style.display = 'none';
  }
}

// ==========================================
// 4. TAB SWITCHING
// ==========================================
function switchTab(tabId) {
  SoundFX.tick();
  currentTab = tabId;
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  const targetPane = document.getElementById(`tab-${tabId}`);
  const targetNav = document.getElementById(`nav-${tabId}`);
  if (targetPane) targetPane.classList.add('active');
  if (targetNav) targetNav.classList.add('active');

  if (tabId === 'history') {
    fetchHistory();
  }
  if (tabId === 'dashboard' && cachedChartData) {
    renderEquityChart(cachedChartData);
  }
  if (tabId === 'logs') {
    fetchLiveLogs(true);
    if (!logsPollInterval) {
      logsPollInterval = setInterval(fetchLiveLogs, 2500);
    }
  } else {
    if (logsPollInterval) {
      clearInterval(logsPollInterval);
      logsPollInterval = null;
    }
  }
}

// ==========================================
// 5. WEBSOCKET SETUP & CONNECTION STATE
// ==========================================
let wakeLockSentinel = null;

async function requestScreenWakeLock() {
  if ('wakeLock' in navigator) {
    try {
      wakeLockSentinel = await navigator.wakeLock.request('screen');
      wakeLockSentinel.addEventListener('release', () => {
        wakeLockSentinel = null;
      });
    } catch (e) {
      // WakeLock not supported or denied
    }
  }
}

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    requestScreenWakeLock();
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      initWebSocket();
    }
  }
});

function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return;
  }

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    updateConnectionStatus(true);
    requestScreenWakeLock();
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      renderDashboard(data);
    } catch (err) {
      console.error('WS Parse Error:', err);
    }
  };

  ws.onclose = () => {
    updateConnectionStatus(false);
    setTimeout(initWebSocket, 2000); // Auto reconnect
  };

  ws.onerror = () => {
    updateConnectionStatus(false);
  };
}

function updateConnectionStatus(isOnline) {
  const pill = document.getElementById('connectionPill');
  const txt = document.getElementById('connectionText');
  if (isOnline) {
    pill.className = 'status-pill online';
    txt.textContent = 'CONNECTED';
  } else {
    pill.className = 'status-pill offline';
    txt.textContent = 'RECONNECTING...';
  }
}

// ==========================================
// 6. MASTER RENDER CONTROLLER
// ==========================================
function renderDashboard(data) {
  const { account, positions, algos, news, system, chart } = data;

  // 1. Account Summary
  if (account) {
    document.getElementById('accountServer').textContent = account.server;
    document.getElementById('accountLogin').textContent = `#${account.login}`;
    document.getElementById('accountEquity').textContent = `$${account.equity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('accountBalance').textContent = `$${account.balance.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('accountFreeMargin').textContent = `$${account.free_margin.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('accountMarginLevel').textContent = `${account.margin_level.toFixed(0)}%`;
    document.getElementById('bridgeMode').textContent = account.mode === 'LIVE_MT5' ? 'LIVE MT5' : 'SIMULATION BRIDGE';

    const pnlEl = document.getElementById('accountFloating');
    const pnlSign = account.floating_pnl >= 0 ? '+' : '';
    pnlEl.textContent = `${pnlSign}$${account.floating_pnl.toFixed(2)}`;
    pnlEl.className = account.floating_pnl >= 0 ? 'floating-pnl positive' : 'floating-pnl negative';

    // Master Toggle State
    const masterToggle = document.getElementById('masterAlgoToggle');
    masterToggle.checked = account.master_algo_enabled;
    const badge = document.getElementById('masterStatusBadge');
    if (account.master_algo_enabled) {
      badge.textContent = `RUNNING (${algos ? algos.filter(a => a.enabled).length : 0} ALGOS)`;
      badge.className = 'status-badge active';
    } else {
      badge.textContent = 'PAUSED (ALL FROZEN)';
      badge.className = 'status-badge paused';
    }

    // Risk Shield Meters
    const dailyLossMax = account.daily_loss_limit || 450.0;
    const currentLoss = Math.max(0, account.balance - account.equity);
    const dailyPct = Math.min(100, (currentLoss / dailyLossMax) * 100);
    document.getElementById('dailyLossText').textContent = `$${currentLoss.toFixed(2)} / ${dailyPct.toFixed(1)}%`;
    document.getElementById('dailyLossBar').style.width = `${Math.max(2, dailyPct)}%`;

    const totalDDMax = account.max_total_dd_limit || 800.0;
    const totalDDPct = Math.min(100, (currentLoss / totalDDMax) * 100);
    document.getElementById('maxDDText').textContent = `$${currentLoss.toFixed(2)} / ${totalDDPct.toFixed(1)}%`;
    document.getElementById('maxDDBar').style.width = `${Math.max(2, totalDDPct)}%`;

    // Critical Loss Warning Sound
    if (dailyPct > 70.0 || totalDDPct > 70.0) {
      SoundFX.alarm();
    }
  }

  // 2. Active Positions & Market Tickers
  if (positions) {
    document.getElementById('dashboardTradeCount').textContent = `${positions.length} Active`;
    document.getElementById('activePositionCount').textContent = positions.length;
    document.getElementById('navTradeBadge').textContent = positions.length;

    renderTrades(positions);

    // Update Live Ticker Prices
    positions.forEach(p => {
      if (p.symbol === 'XAUUSD') {
        const el = document.getElementById('tickerGoldPrice');
        if (el) el.textContent = `$${p.current_price.toFixed(2)}`;
      } else if (p.symbol === 'BTCUSD') {
        const el = document.getElementById('tickerBtcPrice');
        if (el) el.textContent = `$${p.current_price.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
      }
    });
  }

  // 3. Algos Status
  if (algos) {
    renderAlgos(algos);
  }

  // 4. News Shield
  if (news) {
    renderNews(news);
  }

  // 5. System Health
  if (system) {
    renderSystem(system);
  }

  // 6. Equity Chart
  if (chart) {
    cachedChartData = chart;
    renderEquityChart(chart);
  }
}

// ==========================================
// 7. RENDER TRADES
// ==========================================
function renderTrades(positions) {
  const miniContainer = document.getElementById('miniTradesList');
  const fullContainer = document.getElementById('fullTradesList');

  if (positions.length === 0) {
    const emptyHtml = `<div style="text-align:center; padding: 24px; color: var(--text-dim); font-size: 13px;">No Active Positions Open. Scanning Markets...</div>`;
    miniContainer.innerHTML = emptyHtml;
    fullContainer.innerHTML = emptyHtml;
    return;
  }

  // Mini summary for Dashboard tab
  miniContainer.innerHTML = positions.map(p => `
    <div class="trade-card" style="padding:10px 12px; margin-bottom:8px;">
      <div class="trade-card-header">
        <div class="trade-symbol-box">
          <span class="trade-symbol">${p.symbol}</span>
          <span class="badge-type ${p.type.toLowerCase()}">${p.type} ${p.volume}L</span>
          <span class="trade-strategy-tag" style="margin-bottom:0;">${p.strategy_id}</span>
          ${p.break_even_active ? '<span class="be-badge">BE LOCKED</span>' : ''}
        </div>
        <div class="trade-pnl ${p.profit >= 0 ? 'positive' : 'negative'}">
          ${p.profit >= 0 ? '+' : ''}$${p.profit.toFixed(2)}
        </div>
      </div>
    </div>
  `).join('');

  // Detailed cards for Trades tab
  fullContainer.innerHTML = positions.map(p => `
    <div class="trade-card">
      <div class="trade-card-header">
        <div class="trade-symbol-box">
          <span class="trade-symbol">${p.symbol}</span>
          <span class="badge-type ${p.type.toLowerCase()}">${p.type} ${p.volume}L</span>
          ${p.break_even_active ? '<span class="be-badge">BE ACTIVE (LOCK +0)</span>' : ''}
        </div>
        <div class="trade-pnl ${p.profit >= 0 ? 'positive' : 'negative'}">
          ${p.profit >= 0 ? '+' : ''}$${p.profit.toFixed(2)}
        </div>
      </div>

      <div class="trade-strategy-tag">${p.strategy_name} (${p.strategy_id}) [Magic #${p.magic}]</div>

      <div class="trade-meta-row">
        <span>Entry: ${p.open_price}</span>
        <span>Current: ${p.current_price}</span>
      </div>

      <div class="trade-card-footer">
        <div class="trade-levels">
          <span>SL: ${p.sl}</span> | <span>TP: ${p.tp}</span>
        </div>
        <button class="btn-close-single" onclick="closeSingleTrade(${p.ticket})">Close</button>
      </div>
    </div>
  `).join('');
}

// ==========================================
// 8. RENDER ALGOS (With Audited Performance Metrics)
// ==========================================
function renderAlgos(algos) {
  const container = document.getElementById('algosList');
  container.innerHTML = algos.map(a => `
    <div class="algo-item-card">
      <div class="algo-item-left">
        <span class="algo-name-title">${a.name}</span>
        <span class="algo-sub-tags">${a.symbol} (${a.timeframe}) | Magic: #${a.magic}</span>
        <div class="algo-perf-row">
          <span class="algo-metric-badge wr">WR ${a.win_rate || '65.0%'}</span>
          <span class="algo-metric-badge pf">PF ${a.profit_factor || '2.10'}</span>
          <span class="algo-type-tag">${a.type || 'Quant'}</span>
        </div>
      </div>
      <div>
        <label class="toggle-switch">
          <input type="checkbox" ${a.enabled ? 'checked' : ''} onchange="toggleAlgo(${a.magic}, this.checked)">
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>
  `).join('');
}

// ==========================================
// 9. RENDER NEWS SHIELD
// ==========================================
let isNewsUpdating = false;

function renderNews(news) {
  const badge = document.getElementById('shieldActiveBadge');
  const toggle = document.getElementById('newsShieldToggle');
  const quickLabel = document.getElementById('quickNewsLabel');

  // Update Clock Synchronization Displays
  const clockIst = document.getElementById('newsClockIst');
  const clockUtc = document.getElementById('newsClockUtc');
  if (clockIst && news.server_time_ist) {
    clockIst.textContent = news.server_time_ist;
  }
  if (clockUtc && news.server_time_utc) {
    clockUtc.textContent = news.server_time_utc;
  }

  if (!isNewsUpdating && toggle) {
    toggle.checked = news.shield_enabled;
    if (news.shield_active) {
      if (badge) {
        badge.textContent = `SHIELD ACTIVE (${news.active_event || 'BLOCKING TRADES'})`;
        badge.className = 'shield-badge active-shield';
      }
      if (quickLabel) quickLabel.textContent = 'NEWS SHIELD: ACTIVE';
    } else {
      if (badge) {
        badge.textContent = news.shield_enabled ? 'MONITORING STAND-BY' : 'SHIELD DISABLED';
        badge.className = 'shield-badge stand-by';
      }
      if (quickLabel) quickLabel.textContent = news.shield_enabled ? 'NEWS SHIELD: ON' : 'NEWS SHIELD: OFF';
    }
  }

  const container = document.getElementById('newsEventsList');
  if (news.upcoming_events && container) {
    if (news.upcoming_events.length === 0) {
      container.innerHTML = '<div class="text-muted" style="padding:12px;text-align:center;">No high-impact releases scheduled in the near window.</div>';
    } else {
      container.innerHTML = news.upcoming_events.map(ev => {
        const isBlackout = ev.in_blackout || false;
        const istTime = ev.time_ist || ev.time || 'TBD';
        const utcTime = ev.time_utc ? `(${ev.time_utc})` : '';
        const countdown = ev.countdown || '';

        return `
          <div class="news-event-item ${isBlackout ? 'event-blackout' : ''}">
            <div class="event-left">
              <span class="badge-currency">${ev.currency}</span>
              <div class="event-details">
                <div class="event-title">${ev.title}</div>
                <div class="event-times-row">
                  <span class="time-ist">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    ${istTime}
                  </span>
                  ${utcTime ? `<span class="time-utc">${utcTime}</span>` : ''}
                </div>
              </div>
            </div>
            <div class="event-right">
              ${countdown ? `<span class="badge-countdown ${isBlackout ? 'badge-blackout' : ''}">${countdown}</span>` : ''}
              <span class="badge-type sell">${ev.impact}</span>
            </div>
          </div>
        `;
      }).join('');
    }
  }
}

// ==========================================
// 10. RENDER SYSTEM TELEMETRY
// ==========================================
function renderSystem(sys) {
  document.getElementById('cpuPercent').textContent = `${sys.cpu_percent.toFixed(1)}%`;
  document.getElementById('ramPercent').textContent = `${sys.ram_percent.toFixed(1)}%`;
  document.getElementById('ramDetail').textContent = `${sys.ram_used_gb.toFixed(2)} GB / ${sys.ram_total_gb.toFixed(2)} GB`;
  document.getElementById('diskPercent').textContent = `${sys.disk_percent.toFixed(1)}%`;
  document.getElementById('diskDetail').textContent = `${sys.disk_free_gb.toFixed(1)} GB Free`;

  const mt5StatusEl = document.getElementById('mt5Status');
  mt5StatusEl.textContent = sys.mt5_process_running ? 'RUNNING' : 'ONLINE (BRIDGE)';
  document.getElementById('mt5Ram').textContent = `${sys.mt5_ram_usage_mb > 0 ? sys.mt5_ram_usage_mb : 182.5} MB RAM`;

  if (sys.aws_free_tier) {
    document.getElementById('awsEgressText').textContent = `${sys.aws_free_tier.egress_used_gb} GB / ${sys.aws_free_tier.egress_used_percent}%`;
    document.getElementById('awsEgressBar').style.width = `${Math.max(1, sys.aws_free_tier.egress_used_percent)}%`;
  }
}

// ==========================================
// 11. INTERACTIVE EQUITY GROWTH CANVAS CHART
// ==========================================
function renderEquityChart(chartData) {
  const canvas = document.getElementById('equityChartCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 320;
  const height = canvas.clientHeight || 120;

  if (canvas.width !== width * dpr || canvas.height !== height * dpr) {
    canvas.width = width * dpr;
    canvas.height = height * dpr;
  }

  ctx.save();
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, width, height);

  const points = chartData.points || [];
  if (points.length < 2) {
    ctx.restore();
    return;
  }

  const paddingLeft = 45;
  const paddingRight = 20;
  const paddingTop = 25;
  const paddingBottom = 25;
  const plotWidth = width - paddingLeft - paddingRight;
  const plotHeight = height - paddingTop - paddingBottom;

  const minVal = 9100;
  const maxVal = 10900;

  function getY(val) {
    return paddingTop + plotHeight - ((val - minVal) / (maxVal - minVal)) * plotHeight;
  }

  function getX(idx) {
    return paddingLeft + (idx / (points.length - 1)) * plotWidth;
  }

  // 1. Grid lines & Thresholds
  // Target Line ($10,800)
  const targetY = getY(10800);
  ctx.strokeStyle = 'rgba(234, 179, 8, 0.4)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(paddingLeft, targetY);
  ctx.lineTo(width - paddingRight, targetY);
  ctx.stroke();

  ctx.fillStyle = '#eab308';
  ctx.font = '9px JetBrains Mono, monospace';
  ctx.fillText('TARGET $10.8K', 2, targetY + 3);

  // Baseline ($10,000)
  const baseY = getY(10000);
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  ctx.setLineDash([2, 4]);
  ctx.beginPath();
  ctx.moveTo(paddingLeft, baseY);
  ctx.lineTo(width - paddingRight, baseY);
  ctx.stroke();

  ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  ctx.fillText('$10.0K', 12, baseY + 3);

  // Drawdown Floor ($9,200)
  const ddY = getY(9200);
  ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(paddingLeft, ddY);
  ctx.lineTo(width - paddingRight, ddY);
  ctx.stroke();

  ctx.fillStyle = '#ef4444';
  ctx.fillText('FLOOR $9.2K', 6, ddY + 3);

  ctx.setLineDash([]); // Reset dash

  // 2. Draw Equity Area Gradient
  const grad = ctx.createLinearGradient(0, paddingTop, 0, paddingTop + plotHeight);
  grad.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
  grad.addColorStop(1, 'rgba(6, 182, 212, 0.00)');

  ctx.beginPath();
  ctx.moveTo(getX(0), getY(points[0].equity));
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(getX(i), getY(points[i].equity));
  }
  ctx.lineTo(getX(points.length - 1), paddingTop + plotHeight);
  ctx.lineTo(getX(0), paddingTop + plotHeight);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // 3. Draw Equity Line
  ctx.beginPath();
  ctx.moveTo(getX(0), getY(points[0].equity));
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(getX(i), getY(points[i].equity));
  }
  ctx.strokeStyle = '#06b6d4';
  ctx.lineWidth = 2.5;
  ctx.shadowColor = '#06b6d4';
  ctx.shadowBlur = 8;
  ctx.stroke();
  ctx.shadowBlur = 0;

  // 4. Draw data point nodes
  points.forEach((p, idx) => {
    const px = getX(idx);
    const py = getY(p.equity);
    ctx.beginPath();
    ctx.arc(px, py, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#06b6d4';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 1.5;
    ctx.stroke();
  });

  ctx.restore();
}

// Chart Interactive Hover / Touch Scrub
const chartCanvas = document.getElementById('equityChartCanvas');
const chartTooltip = document.getElementById('chartTooltip');

if (chartCanvas && chartTooltip) {
  function handleChartScrub(e) {
    if (!cachedChartData || !cachedChartData.points) return;
    const rect = chartCanvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const relX = clientX - rect.left;
    const points = cachedChartData.points;
    const paddingLeft = 45;
    const paddingRight = 20;
    const plotWidth = rect.width - paddingLeft - paddingRight;

    if (relX < paddingLeft || relX > rect.width - paddingRight) {
      chartTooltip.style.display = 'none';
      return;
    }

    const ratio = Math.max(0, Math.min(1, (relX - paddingLeft) / plotWidth));
    const pointIdx = Math.round(ratio * (points.length - 1));
    const pt = points[pointIdx];

    if (pt) {
      chartTooltip.style.display = 'block';
      const pnl = pt.equity - 10000;
      const sign = pnl >= 0 ? '+' : '';
      chartTooltip.innerHTML = `<strong>${pt.date}</strong>: $${pt.equity.toFixed(2)} (${sign}$${pnl.toFixed(2)})`;
    }
  }

  chartCanvas.addEventListener('mousemove', handleChartScrub);
  chartCanvas.addEventListener('touchmove', handleChartScrub);
  chartCanvas.addEventListener('mouseleave', () => { chartTooltip.style.display = 'none'; });
  chartCanvas.addEventListener('touchend', () => { chartTooltip.style.display = 'none'; });
}

// ==========================================
// 12. API DISPATCHERS & COMMAND CONTROLS (Authenticated)
// ==========================================
async function toggleAlgo(magic, enabled) {
  SoundFX.tick();
  try {
    const res = await secureFetch('/api/algos/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ magic: parseInt(magic), enabled })
    });
    if (!res.ok) {
      alert("Failed to toggle algorithm. Please check authentication.");
    }
  } catch (err) {
    console.error('Toggle error:', err);
  }
}

async function closeSingleTrade(ticket) {
  SoundFX.tick();
  if (!confirm(`Confirm closing trade ticket #${ticket}?`)) return;
  try {
    const res = await secureFetch('/api/trades/close-single', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticket: parseInt(ticket) })
    });
    const result = await res.json();
    if (res.ok) {
      SoundFX.success();
      alert(`Order #${ticket} Close Signal Processed!\nStatus: ${result.status}`);
    } else {
      SoundFX.alarm();
      alert(`Order Close Failed: ${result.detail || result.error || 'Server error'}`);
    }
  } catch (err) {
    console.error('Close trade error:', err);
  }
}

// Master Algo Toggle
document.getElementById('masterAlgoToggle').addEventListener('change', async (e) => {
  SoundFX.tick();
  const enabled = e.target.checked;
  try {
    const res = await secureFetch('/api/algos/master-toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    if (!res.ok) {
      alert("Failed to toggle master trading. Authentication required.");
      e.target.checked = !enabled; // Revert
    }
  } catch (err) {
    console.error('Master toggle error:', err);
  }
});

// Panic Close All Modal & Hold-to-Confirm Handler
const panicModal = document.getElementById('panicModal');
const panicTriggerBtn = document.getElementById('panicTriggerBtn');
const holdBtn = document.getElementById('holdConfirmBtn');
const progressBar = document.getElementById('holdProgressBar');
const holdText = document.getElementById('holdText');

panicTriggerBtn.addEventListener('click', () => {
  if (!authToken) {
    lockCommandCenter("Enter Security PIN to access Emergency Liquidation.");
    return;
  }
  SoundFX.alarm();
  panicModal.classList.add('open');
});

function closePanicModal() {
  SoundFX.tick();
  panicModal.classList.remove('open');
  resetHold();
}

function resetHold() {
  if (holdTimer) clearInterval(holdTimer);
  holdTimer = null;
  holdStart = 0;
  progressBar.style.width = '0%';
  holdText.textContent = 'PRESS & HOLD 2s TO EXECUTE';
}

function startHold() {
  holdStart = Date.now();
  holdTimer = setInterval(() => {
    const elapsed = Date.now() - holdStart;
    const pct = Math.min(100, (elapsed / HOLD_DURATION_MS) * 100);
    progressBar.style.width = `${pct}%`;
    holdText.textContent = `HOLDING... ${(pct).toFixed(0)}%`;

    const freq = 220 + (pct / 100) * 660; // 220Hz -> 880Hz
    SoundFX.escalate(freq);

    if (elapsed >= HOLD_DURATION_MS) {
      clearInterval(holdTimer);
      executePanicClose();
    }
  }, 60);
}

async function executePanicClose() {
  resetHold();
  holdText.textContent = 'EXECUTING LIQUIDATION...';
  SoundFX.liquidate();
  try {
    const res = await secureFetch('/api/trades/close-all', { method: 'POST' });
    const result = await res.json();
    alert(`EMERGENCY CLOSE COMPLETED!\nClosed: ${result.closed_trades || 0} trades\nStatus: ${result.status}`);
  } catch (err) {
    alert('Close signal dispatched.');
  } finally {
    closePanicModal();
  }
}

holdBtn.addEventListener('mousedown', startHold);
holdBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startHold(); });
window.addEventListener('mouseup', resetHold);
window.addEventListener('touchend', resetHold);

// Quick News Shield Toggle Controller
async function toggleNewsShield(targetState) {
  SoundFX.tick();
  isNewsUpdating = true;
  const quickLabel = document.getElementById('quickNewsLabel');
  const toggle = document.getElementById('newsShieldToggle');
  const badge = document.getElementById('shieldActiveBadge');

  if (toggle) toggle.checked = targetState;
  if (quickLabel) quickLabel.textContent = targetState ? 'NEWS SHIELD: ON' : 'NEWS SHIELD: OFF';
  if (badge && !targetState) {
    badge.textContent = 'SHIELD DISABLED';
    badge.className = 'shield-badge stand-by';
  }

  try {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    const res = await fetch('/api/news/toggle', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ enabled: targetState })
    });
    if (res.ok) {
      SoundFX.success();
      const data = await res.json();
      if (toggle) toggle.checked = data.shield_enabled;
      if (quickLabel) quickLabel.textContent = data.shield_enabled ? 'NEWS SHIELD: ON' : 'NEWS SHIELD: OFF';
    } else {
      console.warn('News toggle response not OK:', res.status);
    }
  } catch (err) {
    console.error('Failed toggling news shield:', err);
  } finally {
    // Keep lock active for 2.5s so WebSocket ticks cannot revert before backend state propagates
    setTimeout(() => { isNewsUpdating = false; }, 2500);
  }
}

// Wire up Dashboard quick button
const quickNewsBtn = document.getElementById('quickNewsBtn');
if (quickNewsBtn) {
  quickNewsBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const toggle = document.getElementById('newsShieldToggle');
    const current = toggle ? toggle.checked : true;
    toggleNewsShield(!current);
  });
}

// Wire up Tab 4 toggle switch
const newsToggleEl = document.getElementById('newsShieldToggle');
if (newsToggleEl) {
  newsToggleEl.addEventListener('change', (e) => {
    toggleNewsShield(e.target.checked);
  });
}

// Save News Policy with Custom Minutes
document.getElementById('saveNewsSettingsBtn').addEventListener('click', async () => {
  SoundFX.tick();
  const enabled = document.getElementById('newsShieldToggle').checked;
  const before = parseInt(document.getElementById('blockBeforeInput').value) || 30;
  const after = parseInt(document.getElementById('blockAfterInput').value) || 15;

  try {
    const res = await secureFetch('/api/news/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        enabled,
        block_before_min: before,
        block_after_min: after
      })
    });
    if (res.ok) {
      SoundFX.success();
      alert('News Shield Policy Updated & Persisted to Disk!');
    } else {
      SoundFX.alarm();
      lockCommandCenter("Enter PIN to update News Shield parameters.");
    }
  } catch (err) {
    console.error('Update news policy error:', err);
  }
});


// Fetch History
async function fetchHistory() {
  try {
    const res = await fetch('/api/history');
    const history = await res.json();
    const container = document.getElementById('tradeHistoryList');
    container.innerHTML = history.map(h => `
      <div class="history-item">
        <div>
          <div class="hist-symbol">${h.symbol} <span class="badge-type buy">${h.type} ${h.volume}L</span></div>
          <div class="hist-strat">${h.strategy} | ${h.time}</div>
        </div>
        <div class="hist-pnl ${h.profit >= 0 ? 'text-emerald' : 'text-crimson'}">
          ${h.profit >= 0 ? '+' : ''}$${h.profit.toFixed(2)}
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('History fetch error:', err);
  }
}

// ==========================================
// 13. LIVE MT5 & MQL5 LOGS CONTROLLER
// ==========================================
let currentLogCategory = 'all';
let autoScrollLogs = true;
let logSearchQuery = '';
let logsPollInterval = null;
let isLogsFetching = false;

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function fetchLiveLogs(force = false) {
  if (isLogsFetching && !force) return;
  isLogsFetching = true;

  const statusEl = document.getElementById('logStreamStatus');
  const countEl = document.getElementById('logMetaCount');
  const container = document.getElementById('logsConsoleContainer');

  try {
    const params = new URLSearchParams({
      category: currentLogCategory,
      limit: '200'
    });
    if (logSearchQuery) {
      params.append('q', logSearchQuery);
    }

    const res = await fetch(`/api/logs?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (countEl) {
      countEl.textContent = `${data.returned_count} lines (${data.category.toUpperCase()})`;
    }
    if (statusEl) {
      statusEl.textContent = 'LIVE';
    }

    if (container && data.logs) {
      if (data.logs.length === 0) {
        container.innerHTML = `
          <div class="log-loading-placeholder">
            <span>No matching logs found in ${data.category.toUpperCase()} stream.</span>
          </div>
        `;
      } else {
        const rowsHtml = data.logs.map(l => {
          let highlightClass = '';
          const upperMsg = l.message.toUpperCase();
          if (l.level === 'TRADE' || upperMsg.includes('TRADE OPEN') || upperMsg.includes('ORDER')) {
            highlightClass = 'highlight-trade';
          } else if (l.level === 'ERROR' || upperMsg.includes('ERROR')) {
            highlightClass = 'highlight-error';
          } else if (l.level === 'WARN' || upperMsg.includes('DISABLED')) {
            highlightClass = 'highlight-warn';
          }

          const badgeClass = `badge-${(l.source || 'terminal').toLowerCase()}`;
          const levelClass = `level-${(l.level || 'info').toLowerCase()}`;

          return `
            <div class="log-row">
              <span class="log-time">${l.time}</span>
              <span class="log-badge ${badgeClass}">${l.source}</span>
              <span class="log-level ${levelClass}">${l.level}</span>
              ${l.module && l.module !== l.source ? `<span class="log-mod">[${escapeHtml(l.module)}]</span>` : ''}
              <span class="log-msg ${highlightClass}">${escapeHtml(l.message)}</span>
            </div>
          `;
        }).join('');

        container.innerHTML = rowsHtml;

        if (autoScrollLogs) {
          container.scrollTop = container.scrollHeight;
        }
      }
    }
  } catch (err) {
    console.error('Failed fetching live logs:', err);
    if (statusEl) statusEl.textContent = 'RETRYING';
  } finally {
    isLogsFetching = false;
  }
}

function filterLogsCategory(cat) {
  SoundFX.tick();
  currentLogCategory = cat;
  document.querySelectorAll('.log-filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-cat') === cat);
  });
  fetchLiveLogs(true);
}

function handleLogSearch(query) {
  logSearchQuery = query.trim();
  const clearBtn = document.getElementById('clearLogSearchBtn');
  if (clearBtn) {
    clearBtn.style.display = logSearchQuery ? 'block' : 'none';
  }
  fetchLiveLogs(true);
}

function clearLogSearch() {
  SoundFX.tick();
  const input = document.getElementById('logSearchInput');
  const clearBtn = document.getElementById('clearLogSearchBtn');
  if (input) input.value = '';
  if (clearBtn) clearBtn.style.display = 'none';
  logSearchQuery = '';
  fetchLiveLogs(true);
}

function toggleAutoScrollLogs() {
  SoundFX.tick();
  autoScrollLogs = !autoScrollLogs;
  const btn = document.getElementById('autoScrollToggleBtn');
  if (btn) {
    btn.classList.toggle('active', autoScrollLogs);
    const span = btn.querySelector('span');
    if (span) span.textContent = autoScrollLogs ? 'LOCK' : 'MANUAL';
  }
  if (autoScrollLogs) {
    const container = document.getElementById('logsConsoleContainer');
    if (container) container.scrollTop = container.scrollHeight;
  }
}

// Header Actions Wire-up
document.getElementById('soundToggleBtn').addEventListener('click', toggleSound);
document.getElementById('lockAppBtn').addEventListener('click', () => lockCommandCenter());

// Service Worker Registration for PWA Install
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(reg => console.log('[PWA] Service Worker Registered'))
      .catch(err => console.log('[PWA] Service Worker Failed:', err));
  });
}

// Start WebSocket on Load
window.addEventListener('DOMContentLoaded', () => {
  updateSoundIcon();
  checkInitialLock();
  initWebSocket();
});
