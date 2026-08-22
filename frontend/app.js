/**
 * IITIAN AI - Voice Operating Layer Client Engine
 * Handles Web Speech Recognition, Continuous Wake Word, Web Audio Synth, and SSE Sync.
 * Built for Nivesh Kumar Meena
 */

// State variables
let isListening = false;
let isSpeaking = false;
let isWakeWordEnabled = true;
let soundOutputEnabled = true;
let recognition = null;
let speechSynth = window.speechSynthesis;
let audioCtx = null;
let currentAlarmTimer = null;

// DOM Elements
const voiceOrb = document.getElementById('voiceOrb');
const agentStateText = document.getElementById('agentStateText');
const liveTranscript = document.getElementById('liveTranscript');
const visualizer = document.getElementById('visualizer');
const micBtn = document.getElementById('micBtn');
const micBtnLabel = document.getElementById('micBtnLabel');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const wakeWordToggleBtn = document.getElementById('wakeWordToggleBtn');
const wakeWordStatusText = document.getElementById('wakeWordStatusText');
const soundToggleBtn = document.getElementById('soundToggleBtn');
const soundIcon = document.getElementById('soundIcon');
const statusIndicator = document.getElementById('statusIndicator');
const statusLabel = document.getElementById('statusLabel');

// Dynamic API Base URL (handles file:// and custom ports)
const API_BASE = (window.location.protocol === 'file:' || !window.location.port) ? 'http://127.0.0.1:8080' : '';

// --- Web Audio Synthesizer (Zero Audio Files Needed) ---
function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playWakeChime() {
  try {
    const ctx = getAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.3);
  } catch (e) {}
}

function playSuccessChime() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    [523.25, 659.25, 783.99].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.1, now + i * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.08 + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.08);
      osc.stop(now + i * 0.08 + 0.25);
    });
  } catch (e) {}
}

function playAlarmSiren() {
  try {
    const ctx = getAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(800, ctx.currentTime);
    osc.frequency.linearRampToValueAtTime(1200, ctx.currentTime + 0.2);
    osc.frequency.linearRampToValueAtTime(800, ctx.currentTime + 0.4);
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 0.5);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.5);
  } catch (e) {}
}

// --- Speech Recognition Setup ---
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("Speech recognition not supported in this browser.");
    liveTranscript.textContent = "Speech recognition unavailable in this browser. Use text input.";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-IN'; // Indian English / Hinglish friendly

  recognition.onstart = () => {
    isListening = true;
    updateOrbState('listening');
  };

  recognition.onresult = (event) => {
    let interim = '';
    let finalStr = '';

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalStr += event.results[i][0].transcript;
      } else {
        interim += event.results[i][0].transcript;
      }
    }

    const currentText = (finalStr || interim).trim();
    if (currentText) {
      liveTranscript.textContent = `"${currentText}"`;
    }

    if (finalStr) {
      handleSpeechInput(finalStr.trim());
    }
  };

  recognition.onerror = (event) => {
    console.warn("Recognition error:", event.error);
    if (event.error !== 'no-speech') {
      updateOrbState('idle');
    }
  };

  recognition.onend = () => {
    isListening = false;
    // Auto restart if wake word mode is active
    if (isWakeWordEnabled && !isSpeaking) {
      try {
        recognition.start();
      } catch (e) {}
    } else {
      updateOrbState('idle');
    }
  };

  // Start continuous wake word recognition
  if (isWakeWordEnabled) {
    try {
      recognition.start();
    } catch (e) {}
  }
}

function handleSpeechInput(rawText) {
  const lower = rawText.toLowerCase();
  const wakeWords = ["hey iitian", "iitian", "namaste iitian", "sun iitian", "hello iitian", "ok iitian"];
  
  let isWake = false;
  let command = rawText;

  for (let ww of wakeWords) {
    if (lower.includes(ww)) {
      isWake = true;
      const idx = lower.indexOf(ww);
      command = rawText.substring(idx + ww.length).trim();
      break;
    }
  }

  // If explicit button was clicked OR wake word was detected
  if (isWake || !isWakeWordEnabled) {
    playWakeChime();
    if (command && command.length > 2) {
      submitUserCommand(command);
    } else {
      setOrbPrompt("Listening for command...");
    }
  }
}

// --- Text to Speech (TTS) ---
function speakResponse(text) {
  if (!soundOutputEnabled || !speechSynth) return;

  speechSynth.cancel(); // Stop any previous speech
  const utterance = new SpeechSynthesisUtterance(text);
  
  // Choose voice
  const voices = speechSynth.getVoices();
  const preferredVoice = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('hi') || v.name.includes('Samantha') || v.name.includes('Rishi') || v.name.includes('Google'));
  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }
  utterance.rate = 1.05;
  utterance.pitch = 1.0;

  utterance.onstart = () => {
    isSpeaking = true;
    updateOrbState('speaking');
  };

  utterance.onend = () => {
    isSpeaking = false;
    updateOrbState('idle');
    // Resume listening if wake word is on
    if (isWakeWordEnabled && recognition) {
      try { recognition.start(); } catch (e) {}
    }
  };

  utterance.onerror = () => {
    isSpeaking = false;
    updateOrbState('idle');
  };

  speechSynth.speak(utterance);
}

// --- Orb State Manager ---
function updateOrbState(state) {
  voiceOrb.className = 'voice-orb ' + state;
  visualizer.className = 'visualizer-container ' + (state === 'listening' || state === 'speaking' ? 'active' : '');

  if (state === 'idle') {
    agentStateText.textContent = isWakeWordEnabled ? "Ready • Listening for 'Hey IITIAN'" : "Ready • Click to Talk";
    micBtn.classList.remove('active');
    micBtnLabel.textContent = "Push to Talk";
  } else if (state === 'listening') {
    agentStateText.textContent = "Listening...";
    micBtn.classList.add('active');
    micBtnLabel.textContent = "Listening...";
  } else if (state === 'thinking') {
    agentStateText.textContent = "Thinking & Planning...";
  } else if (state === 'speaking') {
    agentStateText.textContent = "Speaking...";
  }
}

function setOrbPrompt(msg) {
  liveTranscript.textContent = `"${msg}"`;
}

// --- Command Execution & API ---
async function submitUserCommand(userMessage) {
  if (!userMessage.trim()) return;

  // Append user message to Chat
  appendChatMessage('user', userMessage);
  liveTranscript.textContent = `"${userMessage}"`;
  updateOrbState('thinking');

  try {
    const resp = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        mode: 'voice',
        speak: false // We use browser speech synthesis for smoother latency
      })
    });

    if (!resp.ok) {
      throw new Error(`Server returned HTTP ${resp.status}`);
    }

    const data = await resp.json();
    playSuccessChime();

    // Mark online
    if (statusIndicator) {
      statusIndicator.className = 'status-indicator online';
      statusLabel.textContent = 'ONLINE';
    }

    // Append Assistant response to Chat
    appendChatMessage('assistant', data.spoken_response, data.executed_tools, data.plan);

    // Speak response
    if (data.spoken_response) {
      speakResponse(data.spoken_response);
    } else {
      updateOrbState('idle');
    }

    // Refresh state tabs
    loadSystemState();

    // Render planner tab if multi-step
    if (data.plan) {
      renderPlannerSteps(data.plan, data.executed_tools);
    }

  } catch (err) {
    console.error("API error:", err);
    if (statusIndicator) {
      statusIndicator.className = 'status-indicator offline';
      statusLabel.textContent = 'OFFLINE';
    }
    appendChatMessage('assistant', `⚠️ <b>Server Connection Error:</b> Backend server se connect nahi ho pa raha hai.<br><small>Terminal me <code>python3 run.py</code> run karein ya backend start karein.</small>`);
    updateOrbState('idle');
  }
}

function sendSuggestion(text) {
  textInput.value = '';
  submitUserCommand(text);
}

// --- Chat Rendering ---
function appendChatMessage(role, text, tools = [], plan = null) {
  const bubble = document.createElement('div');
  bubble.className = `msg-bubble ${role}`;

  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  let toolsHtml = '';
  if (tools && tools.length > 0) {
    toolsHtml = `<div style="margin-top:8px; display:flex; flex-wrap:wrap; gap:5px;">` +
      tools.map(t => `<span class="badge" style="font-size:0.7rem;">⚡ ${t.tool}</span>`).join('') +
      `</div>`;
  }

  bubble.innerHTML = `
    <div class="msg-author">${role === 'user' ? '👤 YOU' : '🤖 IITIAN'}</div>
    <div class="msg-text">${formatMessageText(text)}</div>
    ${toolsHtml}
    <div class="msg-time">${now}</div>
  `;

  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessageText(txt) {
  return txt.replace(/\n/g, '<br>');
}

// --- Load Full System State ---
async function loadSystemState() {
  try {
    const res = await fetch(`${API_BASE}/api/state`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const state = await res.json();

    if (statusIndicator) {
      statusIndicator.className = 'status-indicator online';
      statusLabel.textContent = 'ONLINE';
    }

    renderAlarms(state.alarms || []);
    renderTimers(state.timers || []);
    renderReminders(state.reminders || []);
    renderCalendar(state.events || []);
    renderContacts(state.contacts || []);
    renderSystemHub(state.battery || {});
    renderMemories(state.memories || []);
    renderMonitoring(state.monitoring || {}, state.recent_traces || []);

  } catch (e) {
    console.warn("Could not load state:", e);
    if (statusIndicator) {
      statusIndicator.className = 'status-indicator offline';
      statusLabel.textContent = 'OFFLINE';
    }
  }
}

function renderAlarms(alarms) {
  const container = document.getElementById('alarmsList');
  if (!alarms.length) {
    container.innerHTML = `<div class="empty-state">No active alarms. Say "Kal subah 7 baje ka alarm laga do".</div>`;
    return;
  }
  container.innerHTML = alarms.map(a => `
    <div class="item-card">
      <div>
        <div class="item-title">⏰ ${a.time_str}</div>
        <div class="item-sub">${a.label} (${a.repeat_days || 'Once'})</div>
      </div>
      <button class="danger-btn" onclick="deleteAlarm('${a.id}')">Cancel</button>
    </div>
  `).join('');
}

function renderTimers(timers) {
  const container = document.getElementById('timersList');
  if (!timers.length) {
    container.innerHTML = `<div class="empty-state">No timers running. Say "Set a 5 minute timer".</div>`;
    return;
  }
  container.innerHTML = timers.map(t => `
    <div class="item-card">
      <div>
        <div class="item-title">⏱️ ${formatSeconds(t.remaining_seconds)}</div>
        <div class="item-sub">${t.label}</div>
      </div>
      <button class="danger-btn" onclick="stopTimer('${t.id}')">Stop</button>
    </div>
  `).join('');
}

function renderReminders(reminders) {
  const container = document.getElementById('remindersList');
  if (!reminders.length) {
    container.innerHTML = `<div class="empty-state">No reminders pending.</div>`;
    return;
  }
  container.innerHTML = reminders.map(r => `
    <div class="item-card">
      <div>
        <div class="item-title">${r.text}</div>
        <div class="item-sub">📅 ${r.remind_at} | Priority: <b>${r.priority.toUpperCase()}</b></div>
      </div>
      <button class="small-btn" onclick="completeReminder('${r.id}')">✓ Done</button>
    </div>
  `).join('');
}

function renderCalendar(events) {
  const container = document.getElementById('calendarList');
  if (!events.length) {
    container.innerHTML = `<div class="empty-state">No upcoming meetings.</div>`;
    return;
  }
  container.innerHTML = events.map(e => `
    <div class="item-card">
      <div>
        <div class="item-title">📅 ${e.title}</div>
        <div class="item-sub">${e.start_time} ${e.location ? '• ' + e.location : ''}</div>
      </div>
      <button class="danger-btn" onclick="deleteEvent('${e.id}')">Remove</button>
    </div>
  `).join('');
}

function renderContacts(contacts) {
  const container = document.getElementById('contactsGrid');
  if (!contacts.length) {
    container.innerHTML = `<div class="empty-state">No contacts stored.</div>`;
    return;
  }
  container.innerHTML = contacts.map(c => `
    <div class="contact-card">
      <div class="contact-name">${c.name}</div>
      <div class="contact-rel">${c.relation || 'Contact'} • ${c.phone}</div>
      <div class="contact-actions">
        <button class="call-btn" onclick="initiateCall('${c.name}', '${c.phone}')">📞 Call</button>
        <button class="wa-btn" onclick="openWhatsApp('${c.phone}', 'Hello ${c.name}!')">💬 WhatsApp</button>
      </div>
    </div>
  `).join('');
}

function renderSystemHub(battery) {
  const batVal = document.getElementById('sysBatteryVal');
  const batDesc = document.getElementById('sysBatteryDesc');
  const topBat = document.getElementById('topBatteryText');

  if (battery && battery.percentage) {
    batVal.textContent = battery.percentage;
    batDesc.textContent = battery.status || "On Battery";
    topBat.textContent = battery.percentage;
  }
}

function renderMemories(memories) {
  const tbody = document.getElementById('memoriesBody');
  if (!memories.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="empty-state">No memories recorded yet.</td></tr>`;
    return;
  }
  tbody.innerHTML = memories.map(m => `
    <tr>
      <td><b>${m.key}</b></td>
      <td>${m.value}</td>
      <td><span class="badge">${m.category}</span></td>
      <td><button class="danger-btn" onclick="deleteMemory('${m.key}')">Forget</button></td>
    </tr>
  `).join('');
}

let langsmithCloudUrl = "https://smith.langchain.com/";

function renderMonitoring(monitoring, traces) {
  // Frontend LangSmith tab and chip removed per user request.
  // Backend observability continues silently to Nivesh's cloud account.
}

function renderPlannerSteps(plan, executed = []) {
  const container = document.getElementById('plannerSteps');
  const badge = document.getElementById('planBadge');

  if (!plan || !plan.steps) return;
  badge.textContent = `${plan.total_steps} Steps Planned`;

  container.innerHTML = plan.steps.map(s => `
    <div class="step-card">
      <div class="step-num">${s.step}</div>
      <div class="step-details">
        <h4>${s.sub_goal}</h4>
        <div class="step-meta">
          Tool: <b>${s.tool || 'Direct Reasoning'}</b> | Intent: ${s.intent}
        </div>
      </div>
    </div>
  `).join('');
}

// --- Action API Callbacks ---
async function deleteAlarm(id) {
  await fetch(`${API_BASE}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'delete_alarm', id })
  });
  loadSystemState();
}

async function stopTimer(id) {
  await fetch(`${API_BASE}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'stop_timer', id })
  });
  loadSystemState();
}

async function completeReminder(id) {
  await fetch(`${API_BASE}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'complete_reminder', id })
  });
  loadSystemState();
}

async function deleteEvent(id) {
  await fetch(`${API_BASE}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'delete_event', id })
  });
  loadSystemState();
}

async function deleteMemory(key) {
  await fetch(`${API_BASE}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'delete_memory', key })
  });
  loadSystemState();
}

function adjustVolume(val) {
  document.getElementById('volumeValText').textContent = val;
  fetch(`${API_BASE}/api/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'execute_tool', tool: 'set_volume', args: { level: parseInt(val) } })
  });
}

function initiateCall(name, phone) {
  appendChatMessage('assistant', `Initiating call to ${name} (${phone})...`);
  speakResponse(`Calling ${name} now.`);
  window.open(`tel:${phone.replace(/\s+/g, '')}`, '_self');
}

function openWhatsApp(phone, text) {
  const cleanPhone = phone.replace(/[^0-9]/g, '');
  const url = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

// --- User Prompts for New Items ---
function openNewAlarmPrompt() {
  const timeStr = prompt("Enter Alarm Time (e.g., '07:00' or '7:30 AM'):", "07:00");
  if (timeStr) {
    submitUserCommand(`Set an alarm for ${timeStr}`);
  }
}

function openNewReminderPrompt() {
  const task = prompt("Enter Reminder Task:", "Email professor");
  if (task) {
    submitUserCommand(`Remind me to ${task} tomorrow at 10 AM`);
  }
}

function openNewContactPrompt() {
  const name = prompt("Contact Name:");
  if (!name) return;
  const phone = prompt("Phone Number (+91...):", "+91 ");
  const relation = prompt("Relation (e.g. Friend, Colleague):", "Friend");
  if (phone) {
    fetch(`${API_BASE}/api/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_contact', name, phone, relation })
    }).then(() => loadSystemState());
  }
}

function openNewMemoryPrompt() {
  const key = prompt("Memory Key (e.g. 'favorite_language'):", "favorite_language");
  if (!key) return;
  const value = prompt("Value to remember:", "Python");
  if (value) {
    fetch(`${API_BASE}/api/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'save_memory', key, value, category: 'user_fact' })
    }).then(() => loadSystemState());
  }
}

// --- SSE Real-Time Stream & Alarm Ringing ---
let currentRingingTimerId = null;
const dismissedTimerIds = new Set();

function setupEventStream() {
  try {
    const evtSource = new EventSource(`${API_BASE}/api/events`);
    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.timers) {
          renderTimers(data.timers);
        }
        if (data.finished_timers && data.finished_timers.length > 0) {
          const unhandled = data.finished_timers.find(t => !dismissedTimerIds.has(t.id));
          if (unhandled) {
            currentRingingTimerId = unhandled.id;
            triggerAlarmModal(unhandled.label || "Timer Finished!");
          }
        }
      } catch (err) {}
    };
  } catch (e) {}
}

function triggerAlarmModal(label) {
  const modal = document.getElementById('alarmModal');
  document.getElementById('alarmModalLabel').textContent = label;
  modal.classList.add('active');
  playAlarmSiren();
}

async function dismissAlarmModal() {
  const modal = document.getElementById('alarmModal');
  modal.classList.remove('active');

  const idToDismiss = currentRingingTimerId;
  if (idToDismiss) {
    dismissedTimerIds.add(idToDismiss);
  }

  try {
    await fetch(`${API_BASE}/api/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'dismiss_timer', id: idToDismiss || '' })
    });
  } catch (err) {}

  currentRingingTimerId = null;
  loadSystemState();
}

async function snoozeAlarmModal() {
  await dismissAlarmModal();
  submitUserCommand("Set a 5 minute timer for Snooze");
}

function formatSeconds(secs) {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
  // Tabs Navigation
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const targetPane = document.getElementById(`pane-${btn.dataset.tab}`);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Mic Button Click
  micBtn.addEventListener('click', () => {
    getAudioContext();
    if (!recognition) {
      initSpeechRecognition();
    }
    if (isListening) {
      try { recognition.stop(); } catch (e) {}
      updateOrbState('idle');
    } else {
      try { recognition.start(); } catch (e) {}
      updateOrbState('listening');
    }
  });

  // Voice Orb Click
  voiceOrb.addEventListener('click', () => {
    micBtn.click();
  });

  // Spacebar to talk
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && e.target === document.body) {
      e.preventDefault();
      micBtn.click();
    }
  });

  // Text input submission
  sendBtn.addEventListener('click', () => {
    const val = textInput.value.trim();
    if (val) {
      textInput.value = '';
      submitUserCommand(val);
    }
  });

  textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendBtn.click();
    }
  });

  // Toggle Wake Word
  wakeWordToggleBtn.addEventListener('click', () => {
    isWakeWordEnabled = !isWakeWordEnabled;
    wakeWordStatusText.textContent = isWakeWordEnabled ? "ON" : "OFF";
    wakeWordToggleBtn.style.color = isWakeWordEnabled ? "var(--accent-cyan)" : "var(--text-muted)";
    if (isWakeWordEnabled && recognition) {
      try { recognition.start(); } catch (e) {}
    }
  });

  // Toggle Sound Output
  soundToggleBtn.addEventListener('click', () => {
    soundOutputEnabled = !soundOutputEnabled;
    soundIcon.textContent = soundOutputEnabled ? "🔊" : "🔇";
  });

  // Initialize
  initSpeechRecognition();
  loadSystemState();
  setupEventStream();
});
