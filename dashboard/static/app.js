// Multi-Agent Platform - Client Application
// Full-Featured Live Command & Control Dashboard

let ws = null;
let messageCount = 0;
let activeTaskId = null;
let taskStartTime = null;
let timerInterval = null;
let currentStreamFilter = 'all';
let currentPreviewContent = '';
let allLoadedSkills = [];

// DOM Elements - Status & Header
const wsStatus = document.getElementById('ws-status');
const omnirouteStatus = document.getElementById('omniroute-status');
const chipOmniroute = document.getElementById('chip-omniroute');
const sysMetrics = document.getElementById('sys-metrics');
const chipTests = document.getElementById('chip-tests');

// DOM Elements - Mission Status Bar
const taskIdBadge = document.getElementById('task-id-badge');
const currentTaskText = document.getElementById('current-task-text');
const timerDisplay = document.getElementById('timer-display');
const taskStatusPill = document.getElementById('task-status-pill');
const btnCancelMission = document.getElementById('btn-cancel-mission');

// DOM Elements - Dialogue & Filters
const dialogueFeed = document.getElementById('dialogue-feed');
const emptyState = document.getElementById('empty-state');
const msgCountEl = document.getElementById('msg-count');
const btnClearChat = document.getElementById('btn-clear-chat');
const filterChips = document.querySelectorAll('.filter-chip');

// DOM Elements - Terminal & Deck Tabs
const terminalScreen = document.getElementById('terminal-screen');
const manualCmdInput = document.getElementById('manual-cmd');
const btnRunCmd = document.getElementById('btn-run-cmd');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// DOM Elements - Workspace Explorer
const workspaceFileList = document.getElementById('workspace-file-list');
const btnRefreshFiles = document.getElementById('btn-refresh-files');
const previewFilename = document.getElementById('preview-filename');
const fileCodePreview = document.getElementById('file-code-preview');
const btnCopyPreview = document.getElementById('btn-copy-preview');

// DOM Elements - Durable Tasks Store
const tasksListContainer = document.getElementById('tasks-list-container');
const btnRefreshTasks = document.getElementById('btn-refresh-tasks');
const tasksCountBadge = document.getElementById('tasks-count-badge');
const taskSearchInput = document.getElementById('task-search');
const btnClearHistory = document.getElementById('btn-clear-history');
let allDurableTasks = [];

// DOM Elements - QA Verification Gate
const qaStatusCard = document.getElementById('qa-status-card');
const qaSummaryText = document.getElementById('qa-summary-text');
const qaTestsPassed = document.getElementById('qa-tests-passed');
const qaArtifactsCount = document.getElementById('qa-artifacts-count');
const qaBloatScore = document.getElementById('qa-bloat-score');
const qaLogText = document.getElementById('qa-log-text');

// DOM Elements - Skills Catalog
const skillSearchInput = document.getElementById('skill-search');
const skillsCatalogList = document.getElementById('skills-catalog-list');

// DOM Elements - Task Dispatcher
const taskInput = document.getElementById('task-input');
const maxRoundsInput = document.getElementById('max-rounds');
const btnDispatch = document.getElementById('btn-dispatch');
const quickChips = document.querySelectorAll('.chip-btn');

// ============================================================================
// 1. WebSocket Live Event Bus & Reconnect
// ============================================================================
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    if (wsStatus) {
      wsStatus.textContent = 'Active';
      wsStatus.style.color = '#10b981';
    }
  };

  ws.onclose = () => {
    if (wsStatus) {
      wsStatus.textContent = 'Reconnecting...';
      wsStatus.style.color = '#f59e0b';
    }
    setTimeout(initWebSocket, 2500);
  };

  ws.onerror = () => {
    if (wsStatus) {
      wsStatus.textContent = 'Error';
      wsStatus.style.color = '#f43f5e';
    }
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleIncomingEvent(data);
    } catch (err) {
      console.error('Failed to parse WebSocket event:', err);
    }
  };
}

// ============================================================================
// 2. Mission Timer & Status Pill Management
// ============================================================================
function startMissionTimer() {
  stopMissionTimer();
  taskStartTime = Date.now();
  timerInterval = setInterval(() => {
    if (!taskStartTime) return;
    const elapsedSeconds = Math.floor((Date.now() - taskStartTime) / 1000);
    const mins = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
    const secs = String(elapsedSeconds % 60).padStart(2, '0');
    if (timerDisplay) timerDisplay.textContent = `${mins}:${secs}`;
  }, 1000);
}

function stopMissionTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  taskStartTime = null;
}

function setTaskStatus(statusText, variant) {
  if (!taskStatusPill) return;
  taskStatusPill.textContent = statusText.toUpperCase();
  taskStatusPill.className = `status-pill status-${variant}`;
}

// ============================================================================
// 3. Pipeline Step Tracker
// ============================================================================
function setPipelineStep(stepNum) {
  for (let i = 1; i <= 5; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    const connEl = document.getElementById(`conn-${i}`);
    if (!stepEl) continue;
    if (i < stepNum) {
      stepEl.className = 'pipeline-step step-complete';
      if (connEl) connEl.className = 'step-connector active';
    } else if (i === stepNum) {
      stepEl.className = 'pipeline-step step-active';
      if (connEl) connEl.className = 'step-connector';
    } else {
      stepEl.className = 'pipeline-step';
      if (connEl) connEl.className = 'step-connector';
    }
  }
}

// ============================================================================
// 4. Central Event Dispatcher & Handlers
// ============================================================================
function handleIncomingEvent(event) {
  if (event.type === 'agent_message') {
    renderAgentMessage(event);
    highlightAgentCard(event.sender);

    // Track active pipeline step based on speaker role
    const lower = (event.sender || '').toLowerCase();
    if (lower.includes('brain')) {
      setPipelineStep(1);
    } else if (lower.includes('architect')) {
      setPipelineStep(2);
    } else if (lower.includes('nemotron') || lower.includes('reasoner') || lower.includes('engineer') || lower.includes('quant') || lower.includes('fullstack')) {
      setPipelineStep(3);
    } else if (lower.includes('reviewer')) {
      setPipelineStep(5);
      setTaskStatus('REVIEWING', 'reviewing');
    }
  } else if (event.type === 'command_start') {
    setPipelineStep(4);
    appendTerminalLine(`PS> [RUNNING] ${event.command}`, 'prompt-line');
  } else if (event.type === 'command_finish') {
    const statusText = event.success ? `[EXIT ${event.exit_code}] (${event.duration}s)` : `[FAILED ${event.exit_code}]`;
    const cssClass = event.success ? 'cmd-output' : 'cmd-error';
    appendTerminalLine(`${statusText}\n${event.output || '[No output]'}`, cssClass);
  } else if (event.type === 'task_started') {
    activeTaskId = event.task_id || event.id || `task-${Date.now().toString(36)}`;
    
    // Mission Status Bar
    if (taskIdBadge) taskIdBadge.textContent = `ID: ${activeTaskId.slice(0, 14)}`;
    if (currentTaskText) currentTaskText.textContent = event.task || 'Active Mission';
    setTaskStatus('RUNNING', 'running');
    
    if (btnCancelMission) {
      btnCancelMission.classList.remove('hidden');
      btnCancelMission.disabled = false;
      btnCancelMission.innerHTML = '<span>■ Stop Mission</span>';
    }

    // Launch Timer
    startMissionTimer();

    // Disable Dispatch Button
    if (btnDispatch) {
      btnDispatch.disabled = true;
      btnDispatch.innerHTML = '<span class="btn-icon">⏳</span><span>Agent Team Working...</span>';
    }

    setPipelineStep(1);
    appendTerminalLine(`\n=== MULTI-AGENT MISSION INITIATED: "${event.task}" ===`, 'prompt-line');

  } else if (event.type === 'task_finished' || event.type === 'task_completed') {
    stopMissionTimer();

    const isSuccess = event.status === 'succeeded' || event.success !== false;
    const isCancelled = event.status === 'cancelled';

    if (isCancelled) {
      setTaskStatus('CANCELLED', 'cancelled');
    } else if (isSuccess) {
      setTaskStatus('SUCCEEDED', 'succeeded');
    } else {
      setTaskStatus('FAILED', 'failed');
    }

    if (btnCancelMission) {
      btnCancelMission.classList.add('hidden');
    }

    if (btnDispatch) {
      btnDispatch.disabled = false;
      btnDispatch.innerHTML = '<span class="btn-icon">⚡</span><span>Dispatch Mission</span>';
    }

    clearAgentHighlights();
    setPipelineStep(6); // marks all 5 complete

    if (currentTaskText) {
      currentTaskText.textContent = `Completed (${event.duration || 0}s, ${event.message_count || messageCount} messages)`;
    }

    appendTerminalLine(`=== MISSION FINISHED (${event.duration || 0}s, status: ${event.status || (isSuccess ? 'succeeded' : 'failed')}) ===\n`, 'prompt-line');

    // Update QA Verification if present
    if (event.verification || event.test_results) {
      updateQADashboard(event.verification || event);
    }

    // Auto-refresh file explorer and task store
    loadWorkspaceFiles();
    loadTasksList();
  } else if (event.type === 'task_cancelled') {
    stopMissionTimer();
    setTaskStatus('CANCELLED', 'cancelled');
    if (btnCancelMission) btnCancelMission.classList.add('hidden');
    if (btnDispatch) {
      btnDispatch.disabled = false;
      btnDispatch.innerHTML = '<span class="btn-icon">⚡</span><span>Dispatch Mission</span>';
    }
    clearAgentHighlights();
    appendTerminalLine(`=== MISSION CANCELLED BY USER ===\n`, 'cmd-error');
  }
}

// ============================================================================
// 5. Render Agent Dialogue with Filters & Formatting
// ============================================================================
function renderAgentMessage(event) {
  if (emptyState) {
    emptyState.style.display = 'none';
  }

  messageCount++;
  if (msgCountEl) {
    msgCountEl.textContent = `${messageCount} event${messageCount === 1 ? '' : 's'}`;
  }

  const bubble = document.createElement('div');
  const senderName = event.sender || 'Agent';
  const senderClass = senderName.toLowerCase().replace(/[^a-z0-9]/g, '');
  bubble.className = `msg-bubble from-${senderClass}`;

  // Categorize for filtering
  const lowerSender = senderName.toLowerCase();
  let category = 'agents';
  if (lowerSender.includes('reviewer') || lowerSender.includes('gatekeeper') || lowerSender.includes('qa')) {
    category = 'qa';
  } else if (lowerSender.includes('system') || lowerSender.includes('executor') || lowerSender.includes('boundary')) {
    category = 'commands';
  }
  bubble.setAttribute('data-category', category);

  // Apply current filter visibility
  if (currentStreamFilter !== 'all' && currentStreamFilter !== category) {
    bubble.style.display = 'none';
  }

  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const safeContent = formatMarkdown(event.content || '');

  bubble.innerHTML = `
    <div class="msg-header">
      <span class="msg-sender">${escapeHtml(senderName)}</span>
      <span class="msg-time">${timeStr}</span>
    </div>
    <div class="msg-content">${safeContent}</div>
  `;

  dialogueFeed.appendChild(bubble);
  dialogueFeed.scrollTop = dialogueFeed.scrollHeight;
}

// Stream Filtering
filterChips.forEach(chip => {
  chip.addEventListener('click', () => {
    filterChips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    currentStreamFilter = chip.getAttribute('data-filter') || 'all';
    applyStreamFilter();
  });
});

function applyStreamFilter() {
  const bubbles = dialogueFeed.querySelectorAll('.msg-bubble');
  bubbles.forEach(b => {
    const cat = b.getAttribute('data-category') || 'agents';
    if (currentStreamFilter === 'all' || currentStreamFilter === cat) {
      b.style.display = '';
    } else {
      b.style.display = 'none';
    }
  });
}

// Clear Dialogue Feed
if (btnClearChat) {
  btnClearChat.addEventListener('click', () => {
    dialogueFeed.innerHTML = '';
    messageCount = 0;
    if (msgCountEl) msgCountEl.textContent = '0 events';
  });
}

// Highlight Agent Cards
function highlightAgentCard(agentName) {
  clearAgentHighlights();
  const lower = (agentName || '').toLowerCase();
  let cardId = null;
  if (lower.includes('architect')) cardId = 'card-architect';
  else if (lower.includes('nemotron') || lower.includes('reasoner')) cardId = 'card-nemotron';
  else if (lower.includes('engineer')) cardId = 'card-engineer';
  else if (lower.includes('quant')) cardId = 'card-quant';
  else if (lower.includes('fullstack')) cardId = 'card-fullstack';
  else if (lower.includes('reviewer')) cardId = 'card-reviewer';
  else if (lower.includes('system') || lower.includes('executor') || lower.includes('boundary')) cardId = 'card-executor';

  if (cardId) {
    const card = document.getElementById(cardId);
    if (card) card.classList.add('active');
  }
}

function clearAgentHighlights() {
  document.querySelectorAll('.agent-card').forEach(card => card.classList.remove('active'));
}

// ============================================================================
// 6. Terminal Console & Manual Command
// ============================================================================
function appendTerminalLine(text, className = '') {
  if (!terminalScreen) return;
  const line = document.createElement('div');
  line.className = `term-line ${className}`;
  line.textContent = text;
  terminalScreen.appendChild(line);
  terminalScreen.scrollTop = terminalScreen.scrollHeight;
}

async function runManualCommand() {
  if (!manualCmdInput) return;
  const command = manualCmdInput.value.trim();
  if (!command) return;

  appendTerminalLine(`PS> ${command}`, 'prompt-line');
  manualCmdInput.value = '';

  try {
    const res = await fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, shell: 'powershell' })
    });
    const result = await res.json();
    const statusText = result.success ? `[EXIT 0] (${result.duration}s)` : `[FAILED ${result.exit_code}]`;
    const css = result.success ? 'cmd-output' : 'cmd-error';
    appendTerminalLine(`${statusText}\n${result.output || '[Done]'}`, css);
  } catch (err) {
    appendTerminalLine(`Error executing: ${err.message}`, 'cmd-error');
  }
}

if (btnRunCmd) btnRunCmd.addEventListener('click', runManualCommand);
if (manualCmdInput) {
  manualCmdInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') runManualCommand();
  });
}

// ============================================================================
// 7. Workspace Files Explorer & Code Previewer
// ============================================================================
function getFileIcon(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  switch (ext) {
    case 'py': return '🐍';
    case 'js':
    case 'ts': return '⚡';
    case 'html': return '🌐';
    case 'css': return '🎨';
    case 'json': return '📋';
    case 'md': return '📝';
    case 'csv': return '📊';
    case 'txt': return '📄';
    default: return '📁';
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function loadWorkspaceFiles() {
  if (!workspaceFileList) return;
  try {
    const res = await fetch('/api/workspace/files');
    const data = await res.json();
    const files = data.files || [];

    workspaceFileList.innerHTML = '';
    if (files.length === 0) {
      workspaceFileList.innerHTML = '<li class="file-item empty">No files generated yet in workspace/</li>';
      return;
    }

    files.forEach((file, idx) => {
      const li = document.createElement('li');
      li.className = 'file-item';
      li.innerHTML = `
        <span class="file-icon">${getFileIcon(file.name)}</span>
        <div class="file-info">
          <span class="file-name">${escapeHtml(file.name)}</span>
          <span class="file-size">${formatBytes(file.size_bytes)}</span>
        </div>
      `;

      li.addEventListener('click', () => {
        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
        li.classList.add('selected');
        previewWorkspaceFile(file.rel_path, file.name);
      });

      workspaceFileList.appendChild(li);

      // Auto-preview first file if nothing selected
      if (idx === 0 && (!previewFilename || previewFilename.textContent.includes('Select'))) {
        li.classList.add('selected');
        previewWorkspaceFile(file.rel_path, file.name);
      }
    });
  } catch (err) {
    workspaceFileList.innerHTML = `<li class="file-item empty error">Failed to load files: ${escapeHtml(err.message)}</li>`;
  }
}

async function previewWorkspaceFile(relPath, filename) {
  if (previewFilename) previewFilename.textContent = `Loading ${filename}...`;
  if (fileCodePreview) fileCodePreview.innerHTML = '<code>Loading file content...</code>';

  try {
    const res = await fetch(`/api/workspace/file?path=${encodeURIComponent(relPath)}`);
    const data = await res.json();
    if (data.success) {
      currentPreviewContent = data.content || '';
      if (previewFilename) previewFilename.textContent = `${filename} (${formatBytes(currentPreviewContent.length)})`;
      if (fileCodePreview) {
        fileCodePreview.innerHTML = `<code>${escapeHtml(currentPreviewContent)}</code>`;
      }
    } else {
      if (previewFilename) previewFilename.textContent = filename;
      if (fileCodePreview) {
        fileCodePreview.innerHTML = `<code class="error">Error reading file: ${escapeHtml(data.error || 'Unknown error')}</code>`;
      }
    }
  } catch (err) {
    if (fileCodePreview) {
      fileCodePreview.innerHTML = `<code class="error">Fetch failed: ${escapeHtml(err.message)}</code>`;
    }
  }
}

if (btnRefreshFiles) btnRefreshFiles.addEventListener('click', loadWorkspaceFiles);

if (btnCopyPreview) {
  btnCopyPreview.addEventListener('click', () => {
    if (!currentPreviewContent) return;
    navigator.clipboard.writeText(currentPreviewContent).then(() => {
      btnCopyPreview.textContent = '✓ Copied!';
      setTimeout(() => { btnCopyPreview.textContent = 'Copy'; }, 2000);
    }).catch(err => {
      console.warn('Clipboard copy failed:', err);
    });
  });
}

// ============================================================================
// 8. Durable Tasks Store (SQLite WAL Viewer & Rehydration)
// ============================================================================
async function loadTasksList() {
  if (!tasksListContainer) return;
  try {
    const res = await fetch('/api/tasks?limit=50');
    const tasks = await res.json();

    if (!Array.isArray(tasks)) {
      tasksListContainer.innerHTML = '<div class="empty-state-small error">Unexpected response from server.</div>';
      return;
    }

    allDurableTasks = tasks;
    if (tasksCountBadge) {
      tasksCountBadge.textContent = `${tasks.length} task${tasks.length === 1 ? '' : 's'}`;
    }

    renderTasksList(allDurableTasks);
  } catch (err) {
    tasksListContainer.innerHTML = `<div class="empty-state-small error">Error loading tasks: ${escapeHtml(err.message)}</div>`;
  }
}

function renderTasksList(tasks) {
  if (!tasksListContainer) return;

  if (tasks.length === 0) {
    tasksListContainer.innerHTML = '<div class="empty-state-small">No tasks match your filter.</div>';
    return;
  }

  tasksListContainer.innerHTML = '';
  tasks.forEach(t => {
    const card = document.createElement('div');
    card.className = 'task-row-card';

    const status = (t.status || 'unknown').toLowerCase();
    let statusClass = 'status-standby';
    if (status === 'succeeded') statusClass = 'status-succeeded';
    else if (status === 'running') statusClass = 'status-running';
    else if (status === 'failed') statusClass = 'status-failed';
    else if (status === 'cancelled') statusClass = 'status-cancelled';

    const promptSnippet = t.prompt || t.task || 'No prompt';
    const taskId = t.id || t.task_id || 'task-unknown';
    const createdStr = t.created_at ? new Date(t.created_at * 1000).toLocaleString() : '--:--';
    const durationStr = (t.completed_at && t.started_at) ? `${(t.completed_at - t.started_at).toFixed(1)}s` : '';

    card.innerHTML = `
      <div class="task-row-header">
        <span class="task-row-id">${escapeHtml(taskId)}</span>
        <span class="status-pill ${statusClass}">${escapeHtml(status.toUpperCase())}</span>
      </div>
      <div class="task-row-prompt" title="${escapeHtml(promptSnippet)}">${escapeHtml(promptSnippet)}</div>
      <div class="task-row-footer">
        <div>
          <span>${createdStr}</span>
          ${durationStr ? `<span> • ${durationStr}</span>` : ''}
        </div>
        <div class="task-actions-row">
          <button class="btn-task-action btn-replay-action" title="Replay dialogue in left stream">👁️ Replay</button>
          <button class="btn-task-action btn-use-prompt-action" title="Copy to prompt box">📋 Use</button>
        </div>
      </div>
    `;

    // Action: Replay Dialogue into Dialogue Feed
    const btnReplay = card.querySelector('.btn-replay-action');
    if (btnReplay) {
      btnReplay.addEventListener('click', (e) => {
        e.stopPropagation();
        rehydrateTaskDialogue(taskId, promptSnippet);
      });
    }

    // Action: Use Prompt in input
    const btnUse = card.querySelector('.btn-use-prompt-action');
    if (btnUse) {
      btnUse.addEventListener('click', (e) => {
        e.stopPropagation();
        if (taskInput) {
          taskInput.value = promptSnippet;
          taskInput.focus();
        }
      });
    }

    // Card click: Also replay dialogue
    card.addEventListener('click', () => {
      rehydrateTaskDialogue(taskId, promptSnippet);
    });

    tasksListContainer.appendChild(card);
  });
}

// Rehydrate and display a task's full conversation into the Dialogue Feed
async function rehydrateTaskDialogue(taskId, taskPrompt) {
  if (!dialogueFeed) return;

  try {
    const res = await fetch(`/api/tasks/${taskId}/events?limit=300`);
    const data = await res.json();
    const events = data.events || data || [];

    if (!Array.isArray(events) || events.length === 0) {
      console.warn(`No events found for task ${taskId}`);
      return;
    }

    // Clear feed and prepare header
    dialogueFeed.innerHTML = '';
    messageCount = 0;

    if (emptyState) emptyState.style.display = 'none';
    if (taskIdBadge) taskIdBadge.textContent = taskId.slice(0, 14);
    if (currentTaskText) currentTaskText.textContent = taskPrompt || taskId;

    // Filter and replay events in chronological order
    events.forEach(evt => {
      if (evt.type === 'agent_message') {
        renderAgentMessage(evt);
      } else if (evt.type === 'command_start') {
        appendTerminalLine(`PS> [EXEC] ${evt.content || (evt.data && evt.data.command) || ''}`, 'prompt-line');
      } else if (evt.type === 'command_finish') {
        const exit = evt.data ? evt.data.exit_code : 0;
        const dur = evt.data ? evt.data.duration : 0;
        const cssClass = exit === 0 ? 'cmd-output' : 'cmd-error';
        appendTerminalLine(`[EXIT ${exit}] (${dur}s)\n${evt.content || ''}`, cssClass);
      } else if (evt.type === 'task_finished') {
        const status = evt.data ? evt.data.status : 'completed';
        appendTerminalLine(`=== TASK FINISHED (Status: ${status}) ===\n`, 'prompt-line');
      }
    });

    if (msgCountEl) {
      msgCountEl.textContent = `${messageCount} event${messageCount === 1 ? '' : 's'}`;
    }

    // Highlight dialogue stream briefly to indicate rehydration
    dialogueFeed.scrollTop = dialogueFeed.scrollHeight;
  } catch (err) {
    console.error(`Failed to rehydrate dialogue for task ${taskId}:`, err);
  }
}

// Automatically rehydrate the latest task on boot so page refresh doesn't show blank
async function rehydrateLatestDialogue() {
  try {
    const res = await fetch('/api/tasks?limit=1');
    const tasks = await res.json();
    if (Array.isArray(tasks) && tasks.length > 0) {
      const latest = tasks[0];
      await rehydrateTaskDialogue(latest.id, latest.prompt);
    }
  } catch (err) {
    console.warn('Auto-rehydration of latest dialogue skipped:', err);
  }
}

// Filter tasks list in real time
if (taskSearchInput) {
  taskSearchInput.addEventListener('input', () => {
    const query = taskSearchInput.value.toLowerCase().trim();
    if (!query) {
      renderTasksList(allDurableTasks);
      return;
    }
    const filtered = allDurableTasks.filter(t => {
      const p = (t.prompt || '').toLowerCase();
      const id = (t.id || '').toLowerCase();
      const s = (t.status || '').toLowerCase();
      const r = (t.assigned_role || '').toLowerCase();
      return p.includes(query) || id.includes(query) || s.includes(query) || r.includes(query);
    });
    renderTasksList(filtered);
  });
}

// Clear all history
if (btnClearHistory) {
  btnClearHistory.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to permanently clear all task history and logs?')) {
      return;
    }
    try {
      const res = await fetch('/api/history', { method: 'DELETE' });
      const data = await res.json();
      if (res.ok) {
        allDurableTasks = [];
        renderTasksList([]);
        if (tasksCountBadge) tasksCountBadge.textContent = '0 tasks';
        if (dialogueFeed) {
          dialogueFeed.innerHTML = '';
          if (emptyState) emptyState.style.display = 'flex';
        }
        if (terminalScreen) {
          terminalScreen.innerHTML = '<div class="term-line prompt-line"><span class="term-text">History cleared. Standing by for new commands.</span></div>';
        }
      } else {
        alert(data.error || 'Failed to clear history');
      }
    } catch (err) {
      alert(`Error clearing history: ${err.message}`);
    }
  });
}

if (btnRefreshTasks) btnRefreshTasks.addEventListener('click', loadTasksList);


// ============================================================================
// 9. Verification & QA Evidence Gate Dashboard
// ============================================================================
function updateQADashboard(verification) {
  if (!verification) return;

  const passedTests = verification.passed_tests || (verification.test_results && verification.test_results.passed) || 0;
  const totalTests = verification.total_tests || (verification.test_results && verification.test_results.total) || passedTests;
  const artifactsCount = verification.artifacts_count || (verification.verified_artifacts && verification.verified_artifacts.length) || 0;
  const bloatScore = verification.bloat_score || (verification.bloat_advisory && verification.bloat_advisory.score) || 0;
  const isPassed = verification.verified === true || verification.status === 'passed';

  if (qaTestsPassed) qaTestsPassed.textContent = `${passedTests} / ${totalTests}`;
  if (qaArtifactsCount) qaArtifactsCount.textContent = `${artifactsCount}`;
  if (qaBloatScore) qaBloatScore.textContent = `${bloatScore} / 100`;

  if (qaStatusCard) {
    if (isPassed) {
      qaStatusCard.innerHTML = `
        <div class="qa-badge-large status-ok">✓ Evidence Verification: PASSED</div>
        <p id="qa-summary-text">All acceptance criteria satisfied. Non-empty artifacts confirmed and zero-test guard enforced.</p>
      `;
    } else {
      qaStatusCard.innerHTML = `
        <div class="qa-badge-large status-failed">⚠️ Evidence Verification: FAILED</div>
        <p id="qa-summary-text">${escapeHtml(verification.reason || 'Acceptance criteria or test requirements were not met.')}</p>
      `;
    }
  }

  if (qaLogText) {
    qaLogText.textContent = JSON.stringify(verification, null, 2);
  }
}

// ============================================================================
// 10. Skills & Personas Catalog (639 Modular Assets)
// ============================================================================
async function loadSkillsCatalog() {
  if (!skillsCatalogList) return;
  try {
    const res = await fetch('/api/brain/skills');
    const skills = await res.json();
    allLoadedSkills = Array.isArray(skills) ? skills : [];
    renderSkillsList(allLoadedSkills);
  } catch (err) {
    skillsCatalogList.innerHTML = `<div class="empty-state-small error">Failed to load skills: ${escapeHtml(err.message)}</div>`;
  }
}

function renderSkillsList(skillsToRender) {
  if (!skillsCatalogList) return;
  skillsCatalogList.innerHTML = '';

  const displayList = skillsToRender.slice(0, 50); // render top 50 matches for high performance
  if (displayList.length === 0) {
    skillsCatalogList.innerHTML = '<div class="empty-state-small">No matching skills or personas found.</div>';
    return;
  }

  displayList.forEach(skill => {
    const item = document.createElement('div');
    item.className = 'skill-catalog-item';
    const source = skill.source || 'core';
    item.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h5>${escapeHtml(skill.name)}</h5>
        <span class="role-badge" style="font-size:0.65rem;">${escapeHtml(source)}</span>
      </div>
      <p>${escapeHtml(skill.summary || `Modular skill: ${skill.name}`)}</p>
    `;

    item.addEventListener('click', () => {
      if (taskInput) {
        const prefix = taskInput.value.trim() ? `${taskInput.value.trim()}\n` : '';
        taskInput.value = `${prefix}Using skill '${skill.name}', `;
        taskInput.focus();
      }
    });

    skillsCatalogList.appendChild(item);
  });
}

if (skillSearchInput) {
  skillSearchInput.addEventListener('input', () => {
    const query = skillSearchInput.value.toLowerCase().trim();
    if (!query) {
      renderSkillsList(allLoadedSkills);
      return;
    }
    const filtered = allLoadedSkills.filter(s =>
      (s.name && s.name.toLowerCase().includes(query)) ||
      (s.source && s.source.toLowerCase().includes(query)) ||
      (s.summary && s.summary.toLowerCase().includes(query))
    );
    renderSkillsList(filtered);
  });
}

// ============================================================================
// 11. Mission Dispatch & Cancellation Controls
// ============================================================================
async function dispatchMission() {
  const prompt = taskInput ? taskInput.value.trim() : '';
  if (!prompt) {
    if (taskInput) {
      taskInput.focus();
      taskInput.classList.add('input-attention');
      taskInput.placeholder = '⚠️ Please enter a mission directive or select a quick directive above!';
      setTimeout(() => {
        taskInput.classList.remove('input-attention');
        taskInput.placeholder = "Instruct the multi-agent team (e.g. 'Build a REST microservice for user auth, write unit tests, and verify completion')...";
      }, 2500);
    }
    return;
  }

  const maxRounds = parseInt(maxRoundsInput.value, 10) || 20;

  // Immediate UI feedback
  if (btnDispatch) {
    btnDispatch.disabled = true;
    btnDispatch.innerHTML = '<span class="btn-icon">⏳</span><span>Agent Team Working...</span>';
  }
  setTaskStatus('RUNNING', 'running');
  startMissionTimer();
  if (btnCancelMission) btnCancelMission.classList.remove('hidden');
  if (currentTaskText) currentTaskText.textContent = prompt;

  try {
    const res = await fetch('/api/dispatch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, max_rounds: maxRounds })
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.error || 'Failed to dispatch mission');
      if (btnDispatch) {
        btnDispatch.disabled = false;
        btnDispatch.innerHTML = '<span class="btn-icon">⚡</span><span>Dispatch Mission</span>';
      }
      setTaskStatus('STANDBY', 'standby');
      stopMissionTimer();
      if (btnCancelMission) btnCancelMission.classList.add('hidden');
    } else {
      activeTaskId = data.task_id || activeTaskId || `task-${Date.now().toString(36)}`;
      if (taskIdBadge) taskIdBadge.textContent = `ID: ${(activeTaskId || '').slice(0, 14)}`;
      taskInput.value = '';
    }
  } catch (err) {
    alert(`Dispatch error: ${err.message}`);
    if (btnDispatch) {
      btnDispatch.disabled = false;
      btnDispatch.innerHTML = '<span class="btn-icon">⚡</span><span>Dispatch Mission</span>';
    }
    setTaskStatus('STANDBY', 'standby');
    stopMissionTimer();
  }
}

if (btnDispatch) btnDispatch.addEventListener('click', dispatchMission);
if (taskInput) {
  taskInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      dispatchMission();
    }
  });
}

if (btnCancelMission) {
  btnCancelMission.addEventListener('click', async () => {
    if (!activeTaskId) return;

    btnCancelMission.disabled = true;
    btnCancelMission.innerHTML = '<span>⏳ Stopping...</span>';

    try {
      const res = await fetch(`/api/tasks/${encodeURIComponent(activeTaskId)}/cancel`, {
        method: 'POST'
      });
      const data = await res.json();
      appendTerminalLine(`[CANCEL] Mission ${activeTaskId} stop signal sent. Subprocess trees killed.`, 'cmd-error');
      setTaskStatus('CANCELLED', 'cancelled');
      stopMissionTimer();
      btnCancelMission.classList.add('hidden');
      if (btnDispatch) {
        btnDispatch.disabled = false;
        btnDispatch.innerHTML = '<span class="btn-icon">⚡</span><span>Dispatch Mission</span>';
      }
    } catch (err) {
      alert(`Error cancelling mission: ${err.message}`);
      btnCancelMission.disabled = false;
      btnCancelMission.innerHTML = '<span>■ Stop Mission</span>';
    }
  });
}

// Quick Prompt Chips
quickChips.forEach(btn => {
  btn.addEventListener('click', () => {
    if (taskInput) {
      taskInput.value = btn.getAttribute('data-prompt') || '';
      taskInput.focus();
    }
  });
});

// ============================================================================
// 10. Quantitative Research & Master Backtest Matrix Deck
// ============================================================================
async function loadQuantLab() {
  try {
    const res = await fetch('/api/quant/overview');
    if (!res.ok) return;
    const data = await res.json();

    const totalRunsEl = document.getElementById('quant-total-runs');
    const topScoreEl = document.getElementById('quant-top-score');
    const matrixCountEl = document.getElementById('quant-matrix-count');
    const activeCandEl = document.getElementById('quant-active-candidate');

    const ledgerRows = data.ledger_rows || [];
    const candidates = data.candidates || [];

    if (totalRunsEl) totalRunsEl.textContent = ledgerRows.length;
    if (matrixCountEl) matrixCountEl.textContent = `${ledgerRows.length} executions`;

    let maxScore = 0;
    ledgerRows.forEach(r => {
      const s = parseFloat(r['Funded Account Score (0-100)'] || r.funded_score || 0);
      if (s > maxScore) maxScore = s;
    });
    if (topScoreEl) topScoreEl.textContent = `${maxScore}/100`;

    const active = candidates.find(c => (c.status || '').toUpperCase() === 'ACTIVE');
    if (active && activeCandEl) {
      activeCandEl.textContent = active.candidate_id || 'BTC-001';
    }

    const tbodyCand = document.getElementById('tbody-candidates');
    if (tbodyCand) {
      tbodyCand.innerHTML = '';
      if (candidates.length === 0) {
        tbodyCand.innerHTML = '<tr><td colspan="6" style="padding:0.75rem; text-align:center; color:#64748b;">No candidates registered</td></tr>';
      } else {
        candidates.forEach(c => {
          const tr = document.createElement('tr');
          tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
          const st = (c.status || 'QUEUED').toUpperCase();
          const badgeClass = st === 'ACTIVE' ? 'color:#10b981;' : (st === 'STAGING' ? 'color:#38bdf8;' : 'color:#94a3b8;');
          tr.innerHTML = `
            <td style="padding:0.4rem; font-weight:600; color:#f8fafc;">${escapeHtml(c.candidate_id)}</td>
            <td style="padding:0.4rem;">${escapeHtml(c.strategy_name)}</td>
            <td style="padding:0.4rem; color:#94a3b8;">${escapeHtml(c.primary_mechanism)}</td>
            <td style="padding:0.4rem; font-weight:600; ${badgeClass}">${escapeHtml(st)}</td>
            <td style="padding:0.4rem;">${escapeHtml(c.funded_score || '--')}</td>
            <td style="padding:0.4rem;"><span class="status-pill status-standby" style="font-size:0.65rem;">${escapeHtml(c.decision || 'PENDING')}</span></td>
          `;
          tbodyCand.appendChild(tr);
        });
      }
    }

    const tbodyMatrix = document.getElementById('tbody-backtest-matrix');
    if (tbodyMatrix) {
      tbodyMatrix.innerHTML = '';
      if (ledgerRows.length === 0) {
        tbodyMatrix.innerHTML = '<tr><td colspan="11" style="padding:0.75rem; text-align:center; color:#64748b;">No backtests executed yet</td></tr>';
      } else {
        [...ledgerRows].reverse().forEach(row => {
          const tr = document.createElement('tr');
          tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';

          const ret = parseFloat(row['Return (%)'] ?? row.total_return ?? 0);
          const maxDd = parseFloat(row['Max Drawdown (%)'] ?? row.max_drawdown ?? 0);
          const winRate = parseFloat(row['Win Rate (%)'] ?? row.win_rate ?? 0);
          const trades = row['Total Trades'] ?? row.total_trades ?? 0;
          const pf = parseFloat(row['Profit Factor'] ?? row.profit_factor ?? 0);
          const score = row['Funded Account Score (0-100)'] ?? row.funded_score ?? 0;
          const verdict = row['Funded Account Verdict'] ?? row.funded_verdict ?? '';

          const retColor = ret >= 0 ? '#10b981' : '#ef4444';
          const ddColor = maxDd <= 8.0 ? '#10b981' : (maxDd <= 10.0 ? '#f59e0b' : '#ef4444');
          const verdictColor = verdict.includes('PRIME') ? '#10b981' : (verdict.includes('VIABLE') ? '#f59e0b' : '#ef4444');

          tr.innerHTML = `
            <td style="padding:0.4rem; font-weight:600; color:#cbd5e1;">${escapeHtml(String(row['Candidate ID'] || ''))}</td>
            <td style="padding:0.4rem; color:#94a3b8;">${escapeHtml(String(row['Engine'] || ''))}</td>
            <td style="padding:0.4rem; font-weight:600; color:#38bdf8;">${escapeHtml(String(row['Timeframe'] || ''))}</td>
            <td style="padding:0.4rem; color:#cbd5e1; font-size:0.75rem;">${escapeHtml(String(row['Setting Variant'] || ''))}</td>
            <td style="padding:0.4rem; text-align:right; font-weight:600; color:${retColor};">${ret.toFixed(2)}%</td>
            <td style="padding:0.4rem; text-align:right; color:${ddColor};">${maxDd.toFixed(2)}%</td>
            <td style="padding:0.4rem; text-align:right;">${winRate.toFixed(1)}%</td>
            <td style="padding:0.4rem; text-align:right;">${trades}</td>
            <td style="padding:0.4rem; text-align:right; font-weight:600;">${pf.toFixed(2)}</td>
            <td style="padding:0.4rem; text-align:center; font-weight:700; color:#38bdf8;">${score}</td>
            <td style="padding:0.4rem; font-size:0.72rem; color:${verdictColor}; font-weight:500;">${escapeHtml(verdict)}</td>
          `;
          tbodyMatrix.appendChild(tr);
        });
      }
    }
  } catch (err) {
    console.warn('Failed to load quant lab data:', err);
  }
}

const btnRefreshQuant = document.getElementById('btn-refresh-quant');
if (btnRefreshQuant) btnRefreshQuant.addEventListener('click', loadQuantLab);

// Tab Switching
tabButtons.forEach(tab => {
  tab.addEventListener('click', () => {
    tabButtons.forEach(b => b.classList.remove('active'));
    tabContents.forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    const targetId = tab.getAttribute('data-tab');
    const content = document.getElementById(targetId);
    if (content) content.classList.add('active');

    // Trigger tab-specific data load
    if (targetId === 'tab-files') loadWorkspaceFiles();
    else if (targetId === 'tab-history') loadTasksList();
    else if (targetId === 'tab-skills' && allLoadedSkills.length === 0) loadSkillsCatalog();
    else if (targetId === 'tab-quant') loadQuantLab();
  });
});

// ============================================================================
// 12. Polling Telemetry & OmniRoute Gateway Health
// ============================================================================
async function updateTelemetry() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    // OmniRoute Gateway Health
    if (data.omniroute && data.omniroute.is_healthy) {
      if (omnirouteStatus) {
        omnirouteStatus.textContent = 'Active (:20128)';
        omnirouteStatus.style.color = '#10b981';
      }
      if (chipOmniroute) chipOmniroute.classList.remove('offline');
    } else {
      if (omnirouteStatus) {
        omnirouteStatus.textContent = 'Standby / Local';
        omnirouteStatus.style.color = '#f59e0b';
      }
      if (chipOmniroute) chipOmniroute.classList.add('offline');
    }

    // Host CPU & Memory Telemetry
    if (data.system && sysMetrics) {
      sysMetrics.textContent = `CPU: ${data.system.cpu_percent}% | RAM: ${data.system.ram_percent}%`;
    }

    // Task button state sync
    if (data.is_task_running) {
      if (btnDispatch && !btnDispatch.disabled) {
        btnDispatch.disabled = true;
        btnDispatch.innerHTML = '<span class="btn-icon">⏳</span><span>Agent Team Working...</span>';
        setTaskStatus('RUNNING', 'running');
        if (btnCancelMission) btnCancelMission.classList.remove('hidden');
      }
    } else {
      if (btnDispatch && btnDispatch.disabled) {
        btnDispatch.disabled = false;
        btnDispatch.innerHTML = '<span class="btn-icon">⚡</span><span>Dispatch Mission</span>';
        if (taskStatusPill && taskStatusPill.textContent === 'RUNNING') {
          setTaskStatus('STANDBY', 'standby');
        }
        if (btnCancelMission) btnCancelMission.classList.add('hidden');
        stopMissionTimer();
      }
    }
  } catch (err) {
    console.warn('Telemetry poll failed:', err);
  }
}

// Markdown formatting helper with escaped HTML
function formatMarkdown(text) {
  let esc = escapeHtml(text);
  // Multi-line code blocks
  esc = esc.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code class="lang-${lang}">${code}</code></pre>`;
  });
  // Inline code
  esc = esc.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold text
  esc = esc.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  return esc;
}

function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ============================================================================
// 13. Initial Boot & Hydration
// ============================================================================
initWebSocket();
updateTelemetry();
loadWorkspaceFiles();
loadTasksList();
loadSkillsCatalog();
rehydrateLatestDialogue();
loadQuantLab();
setInterval(updateTelemetry, 3000);

