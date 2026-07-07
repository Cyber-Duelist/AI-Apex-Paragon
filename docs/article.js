
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const articleId = urlParams.get('id');
    const contentDiv = document.getElementById('article-content');

    if (!articleId) {
        contentDiv.innerHTML = '<h1>Error 404</h1><p>Article ID not specified in URL.</p>';
        return;
    }

    try {
        // Fetch the markdown file from the articles folder
        const response = await fetch(`articles/${articleId}.md`);
        
        if (!response.ok) {
            throw new Error(`Failed to load article: ${response.status} ${response.statusText}`);
        }

        const markdownText = await response.text();
        
        // Ensure marked.js is loaded
        if (typeof marked === 'undefined') {
            throw new Error('Markdown parser (marked.js) not loaded.');
        }

        // Render Markdown to HTML
        const htmlContent = marked.parse(markdownText);
        contentDiv.innerHTML = htmlContent;

    } catch (error) {
        console.error('Error loading article:', error);
        contentDiv.innerHTML = `<h1>System Error</h1><p>Could not load the requested document. Connection to the databank failed.</p><p style="font-family: monospace; color: #ff3366;">${error.message}</p>`;
    }
});
