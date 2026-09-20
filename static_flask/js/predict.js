/* predict.js — Shared prediction form handler */

async function handlePredict(event, type) {
    event.preventDefault();
    const form = event.target;
    const data = {};
    new FormData(form).forEach((v, k) => { data[k] = v; });

    const resultEl = document.getElementById(`result-${type}`);
    resultEl.innerHTML = '<div style="text-align:center;padding:1rem;color:#64748b;">⏳ Analyzing...</div>';

    try {
        const res = await fetch(`/api/predict/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const d = await res.json();
        if (d.error) {
            resultEl.innerHTML = `<div class="result-box" style="border-color:#ff4757;background:rgba(255,71,87,0.08)"><div class="result-title" style="color:#ff4757;">Error</div><div class="result-conf">${d.error}</div></div>`;
            return;
        }

        const isPositive = d.risk_level === 'High';
        const color = isPositive ? '#ff4757' : '#00ff88';
        const bg = isPositive ? 'rgba(255,71,87,0.08)' : 'rgba(0,255,136,0.08)';
        const icon = isPositive ? '⚠️' : '✅';

        resultEl.innerHTML = `
            <div class="result-box ${isPositive ? 'positive' : 'negative'}">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">${icon}</div>
                <div class="result-title" style="color:${color}">${d.prediction}</div>
                <div class="result-conf" style="margin-top:0.5rem;">
                    Confidence: <strong style="color:${color}">${d.confidence}%</strong>
                </div>
                <div class="result-conf" style="margin-top:0.3rem;font-style:italic;color:#64748b;">
                    This is for educational purposes only. Consult a medical professional.
                </div>
            </div>`;
    } catch (e) {
        resultEl.innerHTML = `<div class="result-box" style="border-color:#ff4757;background:rgba(255,71,87,0.08)"><div class="result-title" style="color:#ff4757;">Connection Error</div><div class="result-conf">Could not reach the server. Please try again.</div></div>`;
    }
    return false;
}
