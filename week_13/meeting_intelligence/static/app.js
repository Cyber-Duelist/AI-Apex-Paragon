// Theme Toggle Logic
const themeToggleBtn = document.getElementById('themeToggleBtn');
const moonIcon = document.getElementById('moonIcon');
const sunIcon = document.getElementById('sunIcon');

function setTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        moonIcon.classList.add('hidden');
        sunIcon.classList.remove('hidden');
        localStorage.setItem('meetingIntelTheme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
        moonIcon.classList.remove('hidden');
        sunIcon.classList.add('hidden');
        localStorage.setItem('meetingIntelTheme', 'light');
    }
}

// Check saved theme
const savedTheme = localStorage.getItem('meetingIntelTheme') || 'light';
setTheme(savedTheme);

themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    setTheme(currentTheme === 'dark' ? 'light' : 'dark');
});

document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const transcriptInput = document.getElementById('transcriptInput');
    const includeEmailCheckbox = document.getElementById('includeEmail');
    const resultsSection = document.getElementById('resultsSection');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // DOM Elements for Results
    const summaryText = document.getElementById('summaryText');
    const tagsContainer = document.getElementById('tagsContainer');
    const actionItemsBody = document.getElementById('actionItemsBody');
    const decisionsList = document.getElementById('decisionsList');
    const emailCard = document.getElementById('emailCard');
    const emailSubject = document.getElementById('emailSubject');
    const emailBody = document.getElementById('emailBody');
    const copyEmailBtn = document.getElementById('copyEmailBtn');

    analyzeBtn.addEventListener('click', async () => {
        const transcript = transcriptInput.value.trim();
        if (!transcript) {
            alert('Please paste a meeting transcript first.');
            return;
        }

        // Show loading state
        loadingOverlay.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    transcript: transcript,
                    include_email: includeEmailCheckbox.checked
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Failed to analyze transcript');
            }

            const data = await response.json();
            renderResults(data);
            
            // Hide loading, show results
            loadingOverlay.classList.add('hidden');
            resultsSection.classList.remove('hidden');

            // Scroll to results smoothly if on smaller screen
            if (window.innerWidth <= 1024) {
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
            loadingOverlay.classList.add('hidden');
        }
    });

    function renderResults(data) {
        // 1. Summary & Tags
        summaryText.textContent = data.summary;
        
        tagsContainer.innerHTML = '';
        if (data.meeting_type) {
            const typeTag = document.createElement('span');
            typeTag.className = 'tag';
            typeTag.textContent = `${data.meeting_type} Meeting`;
            tagsContainer.appendChild(typeTag);
        }
        
        if (data.participants && data.participants.length > 0) {
            const paxTag = document.createElement('span');
            paxTag.className = 'tag';
            paxTag.textContent = `${data.participants.length} Participants`;
            tagsContainer.appendChild(paxTag);
        }

        // 2. Action Items
        actionItemsBody.innerHTML = '';
        if (data.action_items && data.action_items.length > 0) {
            data.action_items.forEach(item => {
                const person = item.person || item.assignee || item.owner || 'Unassigned';
                const task = item.task || item.action || item.description || '-';
                const deadline = item.deadline || item.due_date || item.due || item.timeframe || 'ASAP';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="avatar-badge">${person}</span></td>
                    <td>${task}</td>
                    <td><span class="deadline-badge">${deadline}</span></td>
                `;
                actionItemsBody.appendChild(tr);
            });
        } else {
            actionItemsBody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:var(--text-muted);">No action items extracted.</td></tr>';
        }

        // 3. Decisions
        decisionsList.innerHTML = '';
        if (data.decisions && data.decisions.length > 0) {
            data.decisions.forEach(decision => {
                const li = document.createElement('li');
                li.textContent = decision;
                decisionsList.appendChild(li);
            });
        } else {
            decisionsList.innerHTML = '<li style="color:var(--text-muted); padding-left:0;">No key decisions extracted.</li>';
        }

        // 4. Email Draft
        if (includeEmailCheckbox.checked && data.email_subject) {
            emailCard.style.display = 'flex';
            emailSubject.value = data.email_subject;
            emailBody.value = data.email_body;
        } else {
            emailCard.style.display = 'none';
        }
    }

    // Copy Email functionality
    copyEmailBtn.addEventListener('click', () => {
        if (!emailBody.value) return;
        
        const fullText = `Subject: ${emailSubject.value}\n\n${emailBody.value}`;
        navigator.clipboard.writeText(fullText).then(() => {
            const originalText = copyEmailBtn.innerHTML;
            copyEmailBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!`;
            setTimeout(() => {
                copyEmailBtn.innerHTML = originalText;
            }, 2000);
        });
    });
});
