const form = document.getElementById('agentForm');
const promptInput = document.getElementById('promptInput');
const submitBtn = document.getElementById('submitBtn');
const feedContainer = document.getElementById('feedContainer');

const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');

// Continuous Memory: Store all past messages here
let conversationHistory = [];

// Modal Logic
const helpBtn = document.getElementById('helpBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const manualModal = document.getElementById('manualModal');

helpBtn.addEventListener('click', () => manualModal.style.display = 'flex');
closeModalBtn.addEventListener('click', () => manualModal.style.display = 'none');
window.addEventListener('click', (e) => {
    if (e.target === manualModal) manualModal.style.display = 'none';
});

// Handle File Upload
uploadBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', async (e) => {
    if (!e.target.files.length) return;
    const file = e.target.files[0];
    
    const formData = new FormData();
    formData.append('file', file);
    
    uploadStatus.style.display = 'block';
    uploadStatus.innerHTML = `Uploading ${file.name}...`;
    uploadBtn.style.opacity = '0.5';
    
    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        if (res.ok) {
            uploadStatus.innerHTML = `✓ ${file.name} uploaded successfully. The agent can now read it!`;
            promptInput.value = `Read the file '${file.name}' and summarize it.`;
        } else {
            throw new Error('Upload failed');
        }
    } catch (err) {
        uploadStatus.innerHTML = `❌ Failed to upload ${file.name}`;
        uploadStatus.style.color = 'var(--neon-red)';
    } finally {
        uploadBtn.style.opacity = '1';
        fileInput.value = '';
    }
});

async function startAgentStream() {
    try {
        const response = await fetch('/api/stream_agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ messages: conversationHistory })
        });

        if (!response.body) throw new Error('ReadableStream not supported');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            const parts = buffer.split('\n\n');
            buffer = parts.pop(); 

            for (const part of parts) {
                if (part.startsWith('data: ')) {
                    const jsonStr = part.substring(6);
                    try {
                        const event = JSON.parse(jsonStr);
                        
                        // If it needs approval, update memory and show UI
                        if (event.type === 'require_approval') {
                            conversationHistory = event.messages;
                            renderEvent(event);
                            return; // Halt stream!
                        }

                        // Update our local conversation history with the agent's new state
                        if (event.type === 'final_answer' && event.messages) {
                            conversationHistory = event.messages;
                        }
                        
                        // Render it if it's not the initial 'init' event
                        if (event.type !== 'init') {
                            renderEvent(event);
                        }
                    } catch (err) {
                        console.error("JSON parse error:", err, jsonStr);
                    }
                }
            }
        }
    } catch (error) {
        console.error("Stream error:", error);
        renderEvent({ type: "error", content: "Agent connection failed. Check server." });
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="btn-text">EXECUTE</span>';
    }
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    // UI Reset
    promptInput.value = '';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loader-dot">.</span><span class="loader-dot">.</span><span class="loader-dot">.</span>';
    uploadStatus.style.display = 'none';
    
    // Add the new user prompt to history
    conversationHistory.push({ role: 'user', content: prompt });
    
    // Clear feed if this is the first real message
    if (conversationHistory.length === 1) {
        feedContainer.innerHTML = '';
    }

    renderEvent({ type: 'init', content: `Task: ${prompt}` });
    await startAgentStream();
});

// Expose globally for the onclick handlers
document.addEventListener('click', async (e) => {
    if (e.target.matches('.approve-btn') || e.target.matches('.reject-btn')) {
        const button = e.target;
        const action = button.dataset.action;
        const tool = button.dataset.tool;
        const tool_call_id = button.dataset.call;
        const args = JSON.parse(button.dataset.args);
        
        // Disable buttons
        button.parentElement.innerHTML = `<div style="text-align: center; color: var(--text-muted);">Action ${action}...</div>`;
        
        if (action === 'APPROVE') {
            try {
                // Hit backend to execute tool
                const res = await fetch('/api/execute_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ tool_name: tool, args: args })
                });
                const data = await res.json();
                
                // Append observation to memory
                conversationHistory.push({
                    role: "tool",
                    tool_call_id: tool_call_id,
                    name: tool,
                    content: JSON.stringify(data.result)
                });
                
                renderEvent({ type: 'observation', content: data.result });
                
            } catch (err) {
                console.error(err);
            }
        } else {
            // REJECT
            conversationHistory.push({
                role: "tool",
                tool_call_id: tool_call_id,
                name: tool,
                content: JSON.stringify({ error: "User REJECTED this action. Do not proceed with this tool." })
            });
            renderEvent({ type: 'error', content: "Action Rejected by User." });
        }
        
        // Resume agent stream!
        await startAgentStream();
    }
});

function renderEvent(event) {
    const card = document.createElement('div');
    card.className = `event-wrapper event-${getEventClass(event.type)}`;
    
    let innerHTML = '';
    
    switch (event.type) {
        case 'init':
            innerHTML = `
                <div class="event-card" style="border-color: var(--neon-green)">
                    <div class="event-header" style="background: rgba(0, 255, 157, 0.2); color: var(--neon-green);">➔ NEW OBJECTIVE RECEIVED</div>
                    <div class="event-body" style="color: #fff">${escapeHTML(event.content)}</div>
                </div>
            `;
            break;
        case 'think':
            innerHTML = `
                <div class="event-card">
                    <div class="event-header">⚡ GENERATING THOUGHT PROCESS</div>
                    <div class="event-body">${event.content}</div>
                </div>
            `;
            break;
        case 'tool_call':
            innerHTML = `
                <div class="event-card">
                    <div class="event-header">⚙️ EXECUTING TOOL: ${event.tool}</div>
                    <div class="event-body">
                        <pre>${JSON.stringify(event.args, null, 2)}</pre>
                    </div>
                </div>
            `;
            break;
        case 'require_approval':
            // Serialize args for the dataset attribute
            const argsStr = escapeHTML(JSON.stringify(event.args));
            innerHTML = `
                <div class="event-card">
                    <div class="event-header">⚠️ REQUIRES HUMAN APPROVAL</div>
                    <div class="event-body">
                        <p style="color: var(--text-main); margin-bottom: 12px;">The agent requested a dangerous action: <strong>${event.tool}</strong></p>
                        <pre>${JSON.stringify(event.args, null, 2)}</pre>
                        <div class="approval-actions">
                            <button class="approve-btn" data-action="APPROVE" data-tool="${event.tool}" data-call="${event.tool_call_id}" data-args="${argsStr}">APPROVE</button>
                            <button class="reject-btn" data-action="REJECT" data-tool="${event.tool}" data-call="${event.tool_call_id}" data-args="${argsStr}">REJECT</button>
                        </div>
                    </div>
                </div>
            `;
            break;
        case 'observation':
            innerHTML = `
                <div class="event-card">
                    <div class="event-header">👁️ OBSERVATION RETURNED</div>
                    <div class="event-body">
                        <pre>${JSON.stringify(event.content, null, 2)}</pre>
                    </div>
                </div>
            `;
            break;
        case 'final_answer':
            const parsedHTML = window.marked ? window.marked.parse(event.content) : event.content.replace(/\\n/g, '<br>');
            innerHTML = `
                <div class="event-card">
                    <div class="event-header">✓ TASK COMPLETE // FINAL OUTPUT</div>
                    <div class="event-body">${parsedHTML}</div>
                </div>
            `;
            break;
        case 'error':
            innerHTML = `
                <div class="event-card" style="border-color: var(--neon-red)">
                    <div class="event-header" style="background: rgba(255,0,85,0.1); color: var(--neon-red);">❌ CRITICAL ERROR</div>
                    <div class="event-body" style="color: var(--neon-red);">${event.content}</div>
                </div>
            `;
            break;
    }
    
    card.innerHTML = innerHTML;
    feedContainer.appendChild(card);
    feedContainer.scrollTop = feedContainer.scrollHeight;
}

function getEventClass(type) {
    if (type === 'init') return 'init';
    if (type === 'think') return 'think';
    if (type === 'tool_call') return 'tool';
    if (type === 'require_approval') return 'approval';
    if (type === 'observation') return 'obs';
    if (type === 'final_answer') return 'final';
    return 'default';
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
