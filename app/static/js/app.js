/* ═══════════════════════════════════════════════════════════
   HealthTwin — App Logic
   SPA routing, predictions, chatbot, dashboard, watch, history
   ═══════════════════════════════════════════════════════════ */

// ── State ───────────────────────────────────────────────────
let chatHistory = [];
let currentPage = 'home';
let lastAnalysis = null; // store latest dashboard analysis
let lastDashInput = null; // store latest vitals for advisor context

// ── Navigation ──────────────────────────────────────────────
function navigate(page) {
    document.querySelectorAll('.page-section').forEach(s => {
        s.classList.remove('active');
    });

    const target = document.getElementById(`page-${page}`);
    if (target) {
        setTimeout(() => target.classList.add('active'), 50);
    }

    document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
    const activeLink = document.querySelector(`.nav-links a[data-page="${page}"]`);
    if (activeLink) activeLink.classList.add('active');

    document.getElementById('navLinks').classList.remove('open');
    currentPage = page;
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Auto-load data for certain pages
    if (page === 'watch') refreshWatch();
    if (page === 'history') loadHistory();
}

function toggleMobileMenu() {
    document.getElementById('navLinks').classList.toggle('open');
}

// ═══════════════════════════════════════════════════════════
// PREDICTION HANDLER (Diabetes, Heart, Parkinsons)
// ═══════════════════════════════════════════════════════════
async function handlePrediction(event, disease) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = parseFloat(value);
    }

    const spinner = document.getElementById(`spinner-${disease}`);
    const resultContainer = document.getElementById(`result-${disease}`);
    spinner.classList.add('show');
    resultContainer.classList.remove('show');

    try {
        const response = await fetch(`/api/predict/${disease}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Prediction failed');
        }
        const result = await response.json();
        showResult(disease, result);
    } catch (error) {
        showError(disease, error.message);
    } finally {
        spinner.classList.remove('show');
    }
    return false;
}

function showResult(disease, result) {
    const container = document.getElementById(`result-${disease}`);
    const isHighRisk = result.prediction === 1;
    const riskClass = isHighRisk ? 'high-risk' : 'low-risk';
    const icon = isHighRisk ? '⚠️' : '✅';

    let confidenceHTML = '';
    if (result.confidence !== null && result.confidence !== undefined) {
        confidenceHTML = `<div class="result-confidence">Model Confidence: <strong>${result.confidence}%</strong></div>`;
    }

    container.innerHTML = `
        <div class="result-card ${riskClass}">
            <div class="result-icon">${icon}</div>
            <div class="result-badge ${riskClass}">${result.risk_label}</div>
            <p class="result-message">${result.message}</p>
            ${confidenceHTML}
        </div>
    `;
    container.classList.add('show');
}

function showError(disease, message) {
    const container = document.getElementById(`result-${disease}`);
    container.innerHTML = `
        <div class="result-card high-risk">
            <div class="result-icon">❌</div>
            <div class="result-badge high-risk">Error</div>
            <p class="result-message">${message}</p>
        </div>
    `;
    container.classList.add('show');
}

// ═══════════════════════════════════════════════════════════
// RAG CHATBOT
// ═══════════════════════════════════════════════════════════
async function uploadDocument() {
    const fileInput = document.getElementById('documentUpload');
    const file = fileInput.files[0];
    if (!file) return;

    const statusText = document.getElementById('uploadStatus');
    statusText.textContent = "Uploading and indexing...";
    statusText.style.color = "#ffa500";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("Upload failed");

        const data = await response.json();
        statusText.textContent = "✅ " + data.message;
        statusText.style.color = "#00ff88";
        fileInput.value = ""; // clear input
    } catch (error) {
        statusText.textContent = "❌ Error uploading document.";
        statusText.style.color = "#ff4757";
        console.error(error);
    }
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    const sendBtn = document.getElementById('chatSendBtn');
    sendBtn.disabled = true;
    input.value = '';

    addChatBubble(message, 'user');
    chatHistory.push({ role: 'user', content: message });

    const typingBubble = addTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                history: chatHistory.slice(-10),
            }),
        });

        typingBubble.remove();

        if (!response.ok) throw new Error('Chat request failed');

        const data = await response.json();
        addChatBubble(data.reply, 'assistant');
        chatHistory.push({ role: 'assistant', content: data.reply });

        if (data.sources && data.sources.length > 0) {
            addSourcesBubble(data.sources);
        }
    } catch (error) {
        typingBubble.remove();
        addChatBubble('Sorry, I encountered an error. Please try again later.', 'assistant');
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

function addChatBubble(text, role, container) {
    const messages = container || document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
}

function addTypingIndicator(container) {
    const messages = container || document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble assistant typing';
    bubble.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
}

function addSourcesBubble(sources) {
    const messages = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble assistant sources-bubble';

    const header = document.createElement('div');
    header.style.cssText = 'cursor:pointer;font-size:0.85em;color:#94a3b8;margin-bottom:4px;user-select:none;';
    header.textContent = '📚 Sources ▸';

    const list = document.createElement('div');
    list.style.cssText = 'display:none;font-size:0.8em;color:#cbd5e1;margin-top:6px;';

    sources.forEach((src, i) => {
        const item = document.createElement('div');
        item.style.cssText = 'margin-bottom:6px;padding:6px 8px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:2px solid #8b5cf6;';
        const meta = src.metadata || {};
        const page = meta.page ? ` — Page ${meta.page}` : '';
        item.innerHTML = `<strong>Source ${i + 1}${page}</strong><br><span style="opacity:0.8">${src.content}…</span>`;
        list.appendChild(item);
    });

    header.onclick = () => {
        const open = list.style.display !== 'none';
        list.style.display = open ? 'none' : 'block';
        header.textContent = open ? '📚 Sources ▸' : '📚 Sources ▾';
    };

    bubble.appendChild(header);
    bubble.appendChild(list);
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
}

// ═══════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════
function getDashInput() {
    return {
        name: document.getElementById('dash-name').value || 'User',
        age: parseInt(document.getElementById('dash-age').value) || 28,
        gender: document.getElementById('dash-gender').value,
        weight: parseFloat(document.getElementById('dash-weight').value) || 72,
        height: parseFloat(document.getElementById('dash-height').value) || 175,
        steps: parseInt(document.getElementById('dash-steps').value) || 6500,
        sleep: parseFloat(document.getElementById('dash-sleep').value) || 6.5,
        water: parseFloat(document.getElementById('dash-water').value) || 2.0,
        heart_rate: parseInt(document.getElementById('dash-hr').value) || 72,
    };
}

async function analyzeDashboard() {
    const data = getDashInput();
    lastDashInput = data;

    const resultsDiv = document.getElementById('dashboardResults');
    resultsDiv.innerHTML = '<div class="dashboard-placeholder"><div class="spinner-ring" style="width:40px;height:40px;border:3px solid rgba(255,255,255,0.1);border-top-color:#667eea;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto;"></div><p style="margin-top:1rem;color:#5c6bc0;">Analyzing your vitals...</p></div>';

    try {
        const response = await fetch('/api/dashboard/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Analysis failed');
        const result = await response.json();
        lastAnalysis = result;
        renderDashboard(data, result);
        document.getElementById('advisorSection').style.display = 'block';
    } catch (error) {
        resultsDiv.innerHTML = `<div class="dashboard-placeholder"><div class="placeholder-icon">❌</div><p>${error.message}</p></div>`;
    }
}

function renderDashboard(data, r) {
    const resultsDiv = document.getElementById('dashboardResults');

    // Score color
    let scoreColor = '#00ff88';
    if (r.health_score < 60) scoreColor = '#ff4757';
    else if (r.health_score < 80) scoreColor = '#ffa500';

    resultsDiv.innerHTML = `
        <!-- Health Score Hero -->
        <div style="text-align:center; margin-bottom:2rem;">
            <div style="font-size:0.65rem; color:#5c6bc0; letter-spacing:0.15em; text-transform:uppercase;">Health Score</div>
            <div style="font-family:'Space Mono',monospace; font-size:4rem; font-weight:700; color:${scoreColor}; line-height:1;">${r.health_score}</div>
            <div style="font-size:0.72rem; color:#5c6bc0;">out of 100 · ${r.bmi_category}</div>
        </div>

        <!-- KPI Cards -->
        <div class="kpi-grid">
            <div class="metric-card">
                <div class="metric-label">BMI</div>
                <div class="metric-value" style="color:${r.bmi_color}">${r.bmi}</div>
                <div class="metric-sub">${r.bmi_category}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Steps</div>
                <div class="metric-value" style="color:#00e5ff">${data.steps.toLocaleString()}</div>
                <div class="metric-sub">Goal: 10K</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sleep</div>
                <div class="metric-value" style="color:#8b5cf6">${data.sleep}h</div>
                <div class="metric-sub">Rec: 7–9h</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Hydration</div>
                <div class="metric-value" style="color:#00ff88">${data.water}L</div>
                <div class="metric-sub">Rec: 2.5L</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Heart Rate</div>
                <div class="metric-value" style="color:#ff6b35">${data.heart_rate}</div>
                <div class="metric-sub">bpm resting</div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="charts-row">
            <div class="chart-card">
                <div class="chart-card-title">Health Score Gauge</div>
                <canvas id="gaugeCanvas" width="260" height="180"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-card-title">Score Breakdown</div>
                <canvas id="radarCanvas" width="260" height="260"></canvas>
            </div>
        </div>

        <!-- Progress Bars -->
        <div class="progress-section">
            <div class="progress-section-title">Component Scores</div>
            <div id="progressBars"></div>
        </div>

        <!-- Risk Summary -->
        <div class="progress-section-title" style="margin-top:1.5rem;">Risk Summary</div>
        <div class="risk-grid" style="margin-top:1rem;">
            <div class="risk-card">
                <div class="metric-label">Obesity Risk</div>
                <div class="risk-badge risk-${r.obesity_risk.toLowerCase()}">${r.obesity_risk}</div>
                <div class="risk-prob">${r.obesity_prob}% probability</div>
            </div>
            <div class="risk-card">
                <div class="metric-label">Fatigue Risk</div>
                <div class="risk-badge risk-${r.fatigue_risk.toLowerCase()}">${r.fatigue_risk}</div>
                <div class="risk-prob">${r.fatigue_prob}% probability</div>
            </div>
            <div class="risk-card">
                <div class="metric-label">Overall Risk</div>
                <div class="risk-badge risk-${r.health_score > 75 ? 'low' : r.health_score > 50 ? 'medium' : 'high'}">${r.health_score > 75 ? 'Low' : r.health_score > 50 ? 'Medium' : 'High'}</div>
                <div class="risk-prob">Score: ${r.health_score}/100</div>
            </div>
        </div>
    `;

    // Draw charts
    setTimeout(() => {
        drawGauge(r.health_score, scoreColor);
        drawRadar(r.breakdown);
        drawProgressBars(r.breakdown);
    }, 100);
}

// ── Canvas: Gauge Chart ──────────────────────────────────
function drawGauge(score, color) {
    const canvas = document.getElementById('gaugeCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const cx = w / 2, cy = h - 20;
    const radius = Math.min(w, h) - 40;

    ctx.clearRect(0, 0, w, h);

    // Track
    ctx.beginPath();
    ctx.arc(cx, cy, radius / 2, Math.PI, 0, false);
    ctx.lineWidth = 18;
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineCap = 'round';
    ctx.stroke();

    // Colored arc
    const angle = Math.PI + (score / 100) * Math.PI;
    ctx.beginPath();
    ctx.arc(cx, cy, radius / 2, Math.PI, angle, false);
    ctx.lineWidth = 18;

    const grad = ctx.createLinearGradient(0, cy, w, cy);
    grad.addColorStop(0, '#ff4757');
    grad.addColorStop(0.5, '#ffa500');
    grad.addColorStop(1, '#00ff88');
    ctx.strokeStyle = grad;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Score text
    ctx.font = 'bold 32px "Space Mono", monospace';
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText(score, cx, cy - 8);

    ctx.font = '11px Inter, sans-serif';
    ctx.fillStyle = '#5c6bc0';
    ctx.fillText('/100', cx, cy + 10);
}

// ── Canvas: Radar Chart ──────────────────────────────────
function drawRadar(bd) {
    const canvas = document.getElementById('radarCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const cx = w / 2, cy = h / 2;
    const maxR = Math.min(w, h) / 2 - 30;

    ctx.clearRect(0, 0, w, h);

    const labels = ['BMI', 'Sleep', 'Steps', 'Water', 'Heart'];
    const maxVals = [25, 25, 25, 15, 10];
    const vals = [bd.bmi_pts, bd.sleep_pts, bd.step_pts, bd.water_pts, bd.hr_pts];
    const n = labels.length;

    // Grid rings
    for (let ring = 1; ring <= 4; ring++) {
        ctx.beginPath();
        const r = (ring / 4) * maxR;
        for (let i = 0; i <= n; i++) {
            const angle = (Math.PI * 2 * (i % n)) / n - Math.PI / 2;
            const x = cx + r * Math.cos(angle);
            const y = cy + r * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = 'rgba(255,255,255,0.06)';
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // Axis lines
    for (let i = 0; i < n; i++) {
        const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + maxR * Math.cos(angle), cy + maxR * Math.sin(angle));
        ctx.strokeStyle = 'rgba(255,255,255,0.06)';
        ctx.stroke();
    }

    // Data polygon
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
        const idx = i % n;
        const angle = (Math.PI * 2 * idx) / n - Math.PI / 2;
        const r = (vals[idx] / maxVals[idx]) * maxR;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.fillStyle = 'rgba(0, 229, 255, 0.12)';
    ctx.fill();
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Data dots
    for (let i = 0; i < n; i++) {
        const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
        const r = (vals[i] / maxVals[i]) * maxR;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#00e5ff';
        ctx.fill();
    }

    // Labels
    ctx.font = '11px Inter, sans-serif';
    ctx.fillStyle = '#9fa8da';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (let i = 0; i < n; i++) {
        const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
        const lr = maxR + 18;
        const x = cx + lr * Math.cos(angle);
        const y = cy + lr * Math.sin(angle);
        ctx.fillText(labels[i], x, y);
    }
}

// ── Progress Bars ───────────────────────────────────────
function drawProgressBars(bd) {
    const container = document.getElementById('progressBars');
    if (!container) return;
    const items = [
        { label: 'BMI', pts: bd.bmi_pts, max: 25, color: '#667eea' },
        { label: 'Sleep', pts: bd.sleep_pts, max: 25, color: '#8b5cf6' },
        { label: 'Steps', pts: bd.step_pts, max: 25, color: '#00e5ff' },
        { label: 'Water', pts: bd.water_pts, max: 15, color: '#00ff88' },
        { label: 'Heart Rate', pts: bd.hr_pts, max: 10, color: '#ff6b35' },
    ];
    container.innerHTML = items.map(item => {
        const pct = Math.round((item.pts / item.max) * 100);
        return `
            <div class="progress-item">
                <div class="progress-header">
                    <span>${item.label}</span>
                    <span class="progress-score" style="color:${item.color}">${item.pts}/${item.max}</span>
                </div>
                <div class="progress-bar-track">
                    <div class="progress-bar-fill" style="width:${pct}%; background:linear-gradient(90deg,${item.color}88,${item.color});"></div>
                </div>
            </div>
        `;
    }).join('');
}

// ── Save Health Log ─────────────────────────────────────
async function saveHealthLog() {
    const data = getDashInput();
    try {
        const response = await fetch('/api/dashboard/save-log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Save failed');
        alert('✅ Health log saved! View it in the History tab.');
    } catch (error) {
        alert('❌ Error saving log: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// AI ADVISOR
// ═══════════════════════════════════════════════════════════
function sendAdvisorQuick(question) {
    const input = document.getElementById('advisorInput');
    input.value = question;
    sendAdvisorChat();
}

async function sendAdvisorChat() {
    const input = document.getElementById('advisorInput');
    const question = input.value.trim();
    if (!question) return;

    const messages = document.getElementById('advisorMessages');
    input.value = '';

    addChatBubble(question, 'user', messages);
    const typing = addTypingIndicator(messages);

    // Build user data context from last analysis + input
    const userData = {
        ...(lastDashInput || {}),
        ...(lastAnalysis || {}),
    };

    try {
        const response = await fetch('/api/dashboard/advisor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, user_data: userData }),
        });
        typing.remove();
        if (!response.ok) throw new Error('Advisor error');
        const data = await response.json();
        addChatBubble(data.reply, 'assistant', messages);
    } catch (error) {
        typing.remove();
        addChatBubble('Sorry, the advisor encountered an error.', 'assistant', messages);
    }
}

// ═══════════════════════════════════════════════════════════
// SMART WATCH
// ═══════════════════════════════════════════════════════════
let hrReadings = [];

async function refreshWatch() {
    const baseHR = parseInt(document.getElementById('dash-hr')?.value) || 72;
    try {
        const response = await fetch(`/api/dashboard/watch?base_hr=${baseHR}`);
        if (!response.ok) throw new Error('Watch fetch failed');
        const data = await response.json();

        // Update cards
        document.querySelector('#watch-hr .watch-value').textContent = data.heart_rate;
        document.querySelector('#watch-spo2 .watch-value').textContent = data.spo2;
        document.querySelector('#watch-stress .watch-value').textContent = data.stress;
        document.querySelector('#watch-steps .watch-value').textContent = data.live_steps.toLocaleString();
        document.querySelector('#watch-cal .watch-value').textContent = data.calories.toLocaleString();

        // Accumulate HR readings
        hrReadings.push(data.heart_rate);
        if (hrReadings.length > 30) hrReadings = hrReadings.slice(-30);

        // Pad if < 30
        while (hrReadings.length < 30) {
            hrReadings.unshift(baseHR + Math.floor(Math.random() * 20 - 10));
        }

        drawHRChart();
    } catch (error) {
        console.error('Watch error:', error);
    }
}

function drawHRChart() {
    const canvas = document.getElementById('hrChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Handle high-DPI
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = 200;

    const w = canvas.width, h = canvas.height;
    const padding = { top: 15, right: 15, bottom: 25, left: 40 };
    const chartW = w - padding.left - padding.right;
    const chartH = h - padding.top - padding.bottom;

    ctx.clearRect(0, 0, w, h);

    if (hrReadings.length < 2) return;

    const minVal = Math.min(...hrReadings) - 5;
    const maxVal = Math.max(...hrReadings) + 5;

    // Grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartH * i) / 4;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(w - padding.right, y);
        ctx.stroke();

        const val = Math.round(maxVal - ((maxVal - minVal) * i) / 4);
        ctx.font = '10px Inter, sans-serif';
        ctx.fillStyle = '#5c6bc0';
        ctx.textAlign = 'right';
        ctx.fillText(val, padding.left - 6, y + 3);
    }

    // Line
    ctx.beginPath();
    hrReadings.forEach((val, i) => {
        const x = padding.left + (chartW * i) / (hrReadings.length - 1);
        const y = padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = '#ff4757';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Fill under line
    const lastX = padding.left + chartW;
    const lastY = padding.top + chartH - ((hrReadings[hrReadings.length - 1] - minVal) / (maxVal - minVal)) * chartH;
    ctx.lineTo(lastX, padding.top + chartH);
    ctx.lineTo(padding.left, padding.top + chartH);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255, 71, 87, 0.08)';
    ctx.fill();

    // Dots
    hrReadings.forEach((val, i) => {
        const x = padding.left + (chartW * i) / (hrReadings.length - 1);
        const y = padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#ff4757';
        ctx.fill();
    });
}

// ═══════════════════════════════════════════════════════════
// HISTORY
// ═══════════════════════════════════════════════════════════
async function loadHistory() {
    const container = document.getElementById('historyContent');
    try {
        const response = await fetch('/api/dashboard/history?limit=30');
        if (!response.ok) throw new Error('Failed to load history');
        const data = await response.json();

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="dashboard-placeholder">
                    <div class="placeholder-icon">📋</div>
                    <p>No logs yet. Go to <strong>Dashboard</strong>, enter your vitals, and click <strong>Save Log</strong>.</p>
                </div>
            `;
            return;
        }

        // Build chart + table
        let html = '';

        // History chart
        html += `
            <div class="history-chart">
                <div class="chart-title">Health Score Over Time</div>
                <canvas id="historyChart" width="800" height="220"></canvas>
            </div>
        `;

        // Table
        html += `
            <div class="history-table-container">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Name</th>
                            <th>Age</th>
                            <th>BMI</th>
                            <th>Score</th>
                            <th>Steps</th>
                            <th>Sleep</th>
                            <th>Obesity</th>
                            <th>Fatigue</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        data.forEach(row => {
            html += `
                <tr>
                    <td>${row.timestamp || '—'}</td>
                    <td>${row.name || '—'}</td>
                    <td>${row.age || '—'}</td>
                    <td>${row.bmi || '—'}</td>
                    <td><strong style="color:#00e5ff;">${row.health_score || '—'}</strong></td>
                    <td>${row.steps ? row.steps.toLocaleString() : '—'}</td>
                    <td>${row.sleep || '—'}h</td>
                    <td><span class="risk-badge risk-${(row.obesity_risk || 'low').toLowerCase()}">${row.obesity_risk || '—'}</span></td>
                    <td><span class="risk-badge risk-${(row.fatigue_risk || 'low').toLowerCase()}">${row.fatigue_risk || '—'}</span></td>
                </tr>
            `;
        });
        html += '</tbody></table></div>';

        // Clear button
        html += `<div style="text-align:center; margin-top:1rem;"><button class="btn btn-danger" onclick="clearAllLogs()">🗑 Clear All Logs</button></div>`;

        container.innerHTML = html;

        // Draw history chart
        setTimeout(() => drawHistoryChart(data), 100);
    } catch (error) {
        container.innerHTML = `<div class="dashboard-placeholder"><div class="placeholder-icon">❌</div><p>Error: ${error.message}</p></div>`;
    }
}

function drawHistoryChart(data) {
    const canvas = document.getElementById('historyChart');
    if (!canvas || data.length < 2) return;
    const ctx = canvas.getContext('2d');

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = 220;

    const w = canvas.width, h = canvas.height;
    const padding = { top: 15, right: 15, bottom: 30, left: 45 };
    const chartW = w - padding.left - padding.right;
    const chartH = h - padding.top - padding.bottom;

    ctx.clearRect(0, 0, w, h);

    const scores = data.map(d => d.health_score || 0).reverse();

    // Grid
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartH * i) / 4;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(w - padding.right, y);
        ctx.stroke();

        const val = Math.round(100 - (100 * i) / 4);
        ctx.font = '10px Inter, sans-serif';
        ctx.fillStyle = '#5c6bc0';
        ctx.textAlign = 'right';
        ctx.fillText(val, padding.left - 6, y + 3);
    }

    // Line
    ctx.beginPath();
    scores.forEach((val, i) => {
        const x = padding.left + (chartW * i) / Math.max(1, scores.length - 1);
        const y = padding.top + chartH - (val / 100) * chartH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Fill
    const lastIdx = scores.length - 1;
    const lastX = padding.left + (chartW * lastIdx) / Math.max(1, lastIdx);
    ctx.lineTo(lastX, padding.top + chartH);
    ctx.lineTo(padding.left, padding.top + chartH);
    ctx.closePath();
    ctx.fillStyle = 'rgba(0, 229, 255, 0.06)';
    ctx.fill();

    // Dots
    scores.forEach((val, i) => {
        const x = padding.left + (chartW * i) / Math.max(1, scores.length - 1);
        const y = padding.top + chartH - (val / 100) * chartH;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#00e5ff';
        ctx.fill();
    });
}

async function clearAllLogs() {
    if (!confirm('Are you sure you want to clear all health logs?')) return;
    try {
        await fetch('/api/dashboard/history', { method: 'DELETE' });
        loadHistory();
    } catch (error) {
        alert('Error clearing logs: ' + error.message);
    }
}

// ── Init ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    navigate('home');
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 10) {
            navbar.style.boxShadow = 'var(--shadow-md)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    });
});
