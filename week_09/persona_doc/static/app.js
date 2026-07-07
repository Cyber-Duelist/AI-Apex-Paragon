let apiKey = '';
let chatMessages = []; // For persistent history
// DOM Elements
const apiKeyModal = document.getElementById('apiKeyModal');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
const appContainer = document.getElementById('appContainer');

const documentList = document.getElementById('documentList');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');

const chatHistory = document.getElementById('chatHistory');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const docSelector = document.getElementById('docSelector');
const modelSelector = document.getElementById('modelSelector');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if key is in local storage
    const storedKey = localStorage.getItem('personaDocApiKey');
    if (storedKey) {
        apiKeyInput.value = storedKey;
    }
    
    // Load persistent chat history
    const storedHistory = localStorage.getItem('personaDocChatHistory');
    if (storedHistory) {
        try {
            chatMessages = JSON.parse(storedHistory);
            // Render loaded history
            chatMessages.forEach(msg => {
                addMessage(msg.role, msg.content, msg.citations, true);
            });
        } catch (e) {
            console.error('Could not parse chat history');
        }
    }
});

saveApiKeyBtn.addEventListener('click', async () => {
    const key = apiKeyInput.value.trim();
    if (!key) return;

    apiKey = key;
    localStorage.setItem('personaDocApiKey', key);
    
    // Verify key by fetching documents
    try {
        const res = await fetch('/documents', {
            headers: { 'X-API-Key': apiKey }
        });
        
        if (res.ok) {
            const data = await res.json();
            renderDocuments(data.documents);
            
            // Transition UI
            apiKeyModal.classList.remove('active');
            appContainer.classList.remove('hidden');
        } else {
            alert('Invalid API Key. Connection refused.');
        }
    } catch (err) {
        alert('Could not connect to the server.');
    }
});

// Manual Modal Logic
const manualModal = document.getElementById('manualModal');
const openManualBtn = document.getElementById('openManualBtn');
const closeManualBtn = document.getElementById('closeManualBtn');

openManualBtn.addEventListener('click', () => {
    manualModal.classList.add('active');
});

closeManualBtn.addEventListener('click', () => {
    manualModal.classList.remove('active');
});

function renderDocuments(docs) {
    documentList.innerHTML = '';
    docSelector.innerHTML = '<option value="">All Documents</option>';
    if (docs.length === 0) {
        documentList.innerHTML = '<li style="color: var(--text-secondary); font-size: 0.8rem;">No documents uploaded yet.</li>';
        return;
    }
    
    docs.forEach(doc => {
        const container = document.createElement('div');
        container.className = 'doc-item-container';
        
        const li = document.createElement('li');
        li.className = 'doc-item';
        li.textContent = doc;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>';
        deleteBtn.title = 'Delete document';
        deleteBtn.onclick = () => deleteDocument(doc);
        
        container.appendChild(li);
        container.appendChild(deleteBtn);
        documentList.appendChild(container);
        
        const opt = document.createElement('option');
        opt.value = doc;
        opt.textContent = doc;
        docSelector.appendChild(opt);
    });
}

async function fetchDocuments() {
    try {
        const res = await fetch('/documents', { headers: { 'X-API-Key': apiKey } });
        if (res.ok) {
            const data = await res.json();
            renderDocuments(data.documents);
        }
    } catch (e) {
        console.error(e);
    }
}

// Drag and Drop Upload
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', handleDrop, false);
fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

async function handleFiles(files) {
    if (files.length === 0) return;
    const file = files[0];
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    uploadStatus.innerHTML = '<span class="loading-spinner"></span> Uploading and analyzing...';
    
    try {
        const res = await fetch('/upload', {
            method: 'POST',
            headers: { 'X-API-Key': apiKey },
            body: formData
        });
        
        const data = await res.json();
        
        if (res.ok) {
            uploadStatus.innerHTML = `<span style="color: #4ade80">Success! Extracted ${data.pages} pages into ${data.chunks} chunks.</span>`;
            fileInput.value = '';
            fetchDocuments();
        } else {
            uploadStatus.innerHTML = `<span style="color: #ef4444">Error: ${data.detail}</span>`;
        }
    } catch (err) {
        uploadStatus.textContent = 'Error uploading file.';
        uploadStatus.style.color = '#ff4d4f';
    }
}

async function deleteDocument(filename) {
    if (!confirm(`Are you sure you want to completely delete ${filename}? This cannot be undone.`)) {
        return;
    }
    
    try {
        const res = await fetch(`/documents/${filename}`, {
            method: 'DELETE',
            headers: { 'X-API-Key': apiKey }
        });
        
        if (res.ok) {
            fetchDocuments();
        } else {
            const data = await res.json();
            alert(`Failed to delete: ${data.detail || 'Unknown error'}`);
        }
    } catch (err) {
        console.error("Delete error:", err);
        alert("An error occurred while deleting the document.");
    }
}

// Chat Functionality
function addMessage(role, content, citations = [], isLoad = false) {
    if (!isLoad) {
        chatMessages.push({ role, content, citations });
        localStorage.setItem('personaDocChatHistory', JSON.stringify(chatMessages));
    }

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'system' ? 'AI' : 'You';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'msg-content';
    
    // Use marked.js if available, else plain text
    if (typeof marked !== 'undefined') {
        contentDiv.innerHTML = marked.parse(content);
    } else {
        contentDiv.innerHTML = content.replace(/\n/g, '<br>');
    }
    
    if (citations.length > 0) {
        const citDiv = document.createElement('div');
        citDiv.className = 'citations';
        citDiv.innerHTML = '<strong>Sources:</strong>';
        
        // Deduplicate citations by source name
        const uniqueSources = [...new Set(citations.map(c => c.source))];
        uniqueSources.forEach(src => {
            const span = document.createElement('span');
            span.className = 'citation-badge';
            span.textContent = src;
            citDiv.appendChild(span);
        });
        contentDiv.appendChild(citDiv);
    }
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    // Add user msg
    addMessage('user', text);
    chatInput.value = '';
    sendBtn.disabled = true;
    
    // Temporary loading message
    const loadingId = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message system';
    msgDiv.id = loadingId;
    msgDiv.innerHTML = `<div class="avatar">AI</div><div class="msg-content" style="color: var(--text-secondary)">Thinking...</div>`;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    try {
        const sourceVal = docSelector.value;
        const modelVal = modelSelector.value;
        const res = await fetch('/search', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-Key': apiKey 
            },
            body: JSON.stringify({ 
                query: text, 
                top_k: 3, 
                source: sourceVal ? sourceVal : null,
                model_name: modelVal
            })
        });
        
        document.getElementById(loadingId).remove();
        
        if (res.ok) {
            const data = await res.json();
            addMessage('system', data.answer, data.citations);
        } else {
            addMessage('system', 'Error connecting to the AI backend.');
        }
    } catch (e) {
        document.getElementById(loadingId).remove();
        addMessage('system', 'Network error.');
    }
    
    sendBtn.disabled = false;
    chatInput.focus();
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Chat Actions
const clearChatBtn = document.getElementById('clearChatBtn');
const exportChatBtn = document.getElementById('exportChatBtn');

if (clearChatBtn) {
    clearChatBtn.addEventListener('click', () => {
        if (confirm("Are you sure you want to clear your chat history?")) {
            chatMessages = [];
            localStorage.removeItem('personaDocChatHistory');
            // Remove all messages except the welcome message
            const messages = chatHistory.querySelectorAll('.message');
            for (let i = 1; i < messages.length; i++) {
                messages[i].remove();
            }
        }
    });
}

if (exportChatBtn) {
    exportChatBtn.addEventListener('click', () => {
        if (chatMessages.length === 0) {
            alert("No chat history to export.");
            return;
        }
        
        let markdownContent = "# PersonaDoc Chat Export\n\n";
        chatMessages.forEach(msg => {
            const roleName = msg.role === 'user' ? '**You**' : '**PersonaDoc AI**';
            markdownContent += `${roleName}:\n${msg.content}\n`;
            
            if (msg.citations && msg.citations.length > 0) {
                const uniqueSources = [...new Set(msg.citations.map(c => c.source))];
                markdownContent += `\n*Sources: ${uniqueSources.join(', ')}*\n`;
            }
            markdownContent += "\n---\n\n";
        });
        
        const blob = new Blob([markdownContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `personadoc-chat-${new Date().toISOString().slice(0,10)}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}
