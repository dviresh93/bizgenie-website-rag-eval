document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = '/api/v1';

    // Elements
    const indexSection = document.getElementById('indexing-section');
    const indexForm = document.getElementById('indexForm');
    const urlInput = document.getElementById('urlInput');
    const indexBtn = document.getElementById('indexBtn');
    const indexStatus = document.getElementById('indexStatus');

    const querySection = document.getElementById('query-section');
    const queryForm = document.getElementById('queryForm');
    const questionInput = document.getElementById('questionInput');
    const queryBtn = document.getElementById('queryBtn');
    const queryResponseDiv = document.getElementById('queryResponse');

    // Helper: Set Status
    function setStatus(element, message, type) {
        element.className = `status-bar ${type}`;
        element.innerHTML = message;
    }

    // Helper: API Fetch
    async function fetchApi(endpoint, method = 'GET', body = null) {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error ${response.status}`);
        }
        return await response.json();
    }

    // --- Indexing Logic ---
    indexForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        if (!url) return;

        // UI State: Loading
        indexBtn.disabled = true;
        indexBtn.textContent = 'Indexing...';
        setStatus(indexStatus, '⏳ Fetching and processing content. This may take a moment...', 'loading');
        
        // Disable query section while indexing new content
        querySection.classList.add('disabled');
        questionInput.disabled = true;
        queryBtn.disabled = true;
        questionInput.placeholder = "Indexing in progress...";
        queryResponseDiv.classList.remove('visible');

        try {
            const data = await fetchApi('/index', 'POST', { url });
            
            // UI State: Success
            setStatus(indexStatus, `✅ Success! Indexed ${data.documents_processed} page(s) into collection '${data.collection_name}'.`, 'success');
            
            // Enable Query Section
            querySection.classList.remove('disabled');
            questionInput.disabled = false;
            queryBtn.disabled = false;
            questionInput.placeholder = "Ask a question about the website...";
            questionInput.focus();

        } catch (error) {
            // UI State: Error
            setStatus(indexStatus, `❌ Indexing failed: ${error.message}`, 'error');
        } finally {
            indexBtn.disabled = false;
            indexBtn.textContent = 'Index';
        }
    });

    // --- Query Logic ---
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;

        // UI State: Loading
        queryBtn.disabled = true;
        queryBtn.textContent = 'Thinking...';
        queryResponseDiv.classList.add('visible');
        queryResponseDiv.innerHTML = '<p>🤔 Analyzing content and generating answer...</p>';

        try {
            const data = await fetchApi('/query', 'POST', { question });
            
            // Format Sources
            const sourcesList = data.sources.map(s => `<li>${s}</li>`).join('');
            
            // Render Answer
            queryResponseDiv.innerHTML = `
                <div style="font-size: 1.1em; line-height: 1.6;">${data.answer}</div>
                <div class="meta-info">
                    <p><strong>Model:</strong> ${data.model_used} | <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(0)}%</p>
                    <details>
                        <summary style="cursor: pointer;">View Sources</summary>
                        <ul style="margin-top: 5px; padding-left: 20px;">${sourcesList}</ul>
                    </details>
                </div>
            `;

        } catch (error) {
            queryResponseDiv.innerHTML = `<p style="color: #c0392b;"><strong>Error:</strong> ${error.message}</p>`;
        } finally {
            queryBtn.disabled = false;
            queryBtn.textContent = 'Ask';
        }
    });
});
