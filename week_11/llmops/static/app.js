const runEvalBtn = document.getElementById('runEvalBtn');
const progressText = document.getElementById('progressText');
const evalTableBody = document.getElementById('evalTableBody');

// Metrics DOM elements
const passRateMetric = document.getElementById('passRateMetric');
const costMetric = document.getElementById('costMetric');
const latencyMetric = document.getElementById('latencyMetric');

runEvalBtn.addEventListener('click', async () => {
    // Reset UI
    evalTableBody.innerHTML = '';
    passRateMetric.innerText = '--%';
    costMetric.innerText = '$0.000000';
    latencyMetric.innerText = '--ms';
    runEvalBtn.disabled = true;
    progressText.innerText = 'Initializing Evaluation Suite...';

    let dataset = [];
    try {
        const datasetInput = document.getElementById('datasetInput').value;
        dataset = JSON.parse(datasetInput);
        if (!Array.isArray(dataset)) throw new Error("Dataset must be a JSON array.");
    } catch (e) {
        alert("Invalid JSON dataset: " + e.message);
        runEvalBtn.disabled = false;
        progressText.innerText = 'Evaluation Failed. Bad JSON.';
        return;
    }

    try {
        const response = await fetch('/api/run_eval', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ dataset: dataset })
        });

        if (!response.body) {
            throw new Error('ReadableStream not supported by browser.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            let lines = buffer.split('\n');
            
            // Keep the last partial line in the buffer
            buffer = lines.pop();

            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.replace('data: ', '').trim();
                    if (!dataStr) continue;

                    const event = JSON.parse(dataStr);
                    handleEvalEvent(event);
                }
            }
        }
        
        progressText.innerText = 'Evaluation Complete.';
        progressText.style.color = 'var(--neon-green)';

    } catch (err) {
        console.error(err);
        progressText.innerText = 'Evaluation Failed. Check console.';
        progressText.style.color = 'var(--neon-red)';
    } finally {
        runEvalBtn.disabled = false;
    }
});

function handleEvalEvent(event) {
    if (event.type === 'eval_result') {
        progressText.innerText = `Evaluating question ${event.index} of ${event.total}...`;
        
        const tr = document.createElement('tr');
        
        const badgeClass = event.verdict === 'PASS' ? 'badge-pass' : 'badge-fail';
        
        tr.innerHTML = `
            <td>${event.index}</td>
            <td>
                <strong>${escapeHTML(event.question)}</strong>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Reasoning: ${escapeHTML(event.reasoning)}</div>
            </td>
            <td style="font-size: 1.1rem; font-weight: 600; color: ${event.score >= 4 ? 'var(--neon-green)' : 'var(--neon-red)'}">${event.score}/5</td>
            <td><span class="badge ${badgeClass}">${event.verdict}</span></td>
            <td style="color: #ffaa00">${event.latency}ms</td>
            <td>${event.tokens}</td>
            <td style="color: var(--neon-blue)">$${event.cost.toFixed(6)}</td>
        `;
        
        evalTableBody.appendChild(tr);
        // Auto-scroll
        evalTableBody.parentElement.scrollTop = evalTableBody.parentElement.scrollHeight;
        
    } else if (event.type === 'summary') {
        // Update global metrics header
        passRateMetric.innerText = `${event.pass_rate.toFixed(1)}%`;
        costMetric.innerText = `$${event.total_cost.toFixed(6)}`;
        latencyMetric.innerText = event.avg_latency;
    }
}

function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
