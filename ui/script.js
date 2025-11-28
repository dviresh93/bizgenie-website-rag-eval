document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = '/api/v1';

    // Elements - Setup
    const setupSection = document.getElementById('setup-section');
    const setupForm = document.getElementById('setupForm');
    const retrievalSelect = document.getElementById('retrievalSelect');
    const llmSelect = document.getElementById('llmSelect');
    const targetUrlInput = document.getElementById('targetUrl');
    const startSessionBtn = document.getElementById('startSessionBtn');

    // Elements - Chat
    const chatSection = document.getElementById('chat-section');
    const activeUrlSpan = document.getElementById('activeUrl');
    const activeConfigSpan = document.getElementById('activeConfig');
    const queryForm = document.getElementById('queryForm');
    const questionInput = document.getElementById('questionInput');
    const queryBtn = document.getElementById('queryBtn');
    const statusIndicator = document.getElementById('statusIndicator');
    const chatContainer = document.getElementById('queryResponse'); // Reusing this container for history
    const newSessionBtn = document.getElementById('newSessionBtn');

    // State
    let sessionState = {
        mcpTool: '',
        llmModel: '',
        targetUrl: '',
        sessionId: ''
    };

    let availableComponents = {};

    // --- Helpers ---
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    async function fetchApi(endpoint, method = 'GET', body = null) {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) options.body = JSON.stringify(body);
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error ${response.status}`);
        }
        return await response.json();
    }

    function setStatus(message, type) {
        if (!message) {
            statusIndicator.style.display = 'none';
            return;
        }
        statusIndicator.className = `status-bar ${type}`;
        statusIndicator.innerHTML = message;
        statusIndicator.style.display = 'block';
    }

    function appendMessage(role, content, meta = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.style.marginBottom = '20px';
        msgDiv.style.padding = '20px';
        msgDiv.style.borderRadius = '12px';
        msgDiv.style.backgroundColor = role === 'user' ? '#e3f2fd' : '#f8f9fa';
        msgDiv.style.borderLeft = role === 'user' ? '5px solid #3498db' : '5px solid #34495e';

        let html = `<div style="margin-bottom: 10px;"><strong>${role === 'user' ? 'You' : 'AI Expert'}</strong></div>`;
        html += `<div style="line-height: 1.6;">${content}</div>`;

        if (meta) {
            // Format Sources
            const sourcesList = meta.sources.map(s => `<li><a href="${s}" target="_blank">${s}</a></li>`).join('');
            html += `
                <div class="meta-info">
                    <details>
                        <summary style="cursor: pointer; font-weight: 600;">Reference Sources (${meta.sources.length})</summary>
                        <ul style="margin-top: 10px; padding-left: 20px; word-break: break-all;">${sourcesList}</ul>
                    </details>
                    <p style="margin-top: 10px; font-size: 0.85em; color: #95a5a6;">Processing Time: ${(meta.metrics.total_time).toFixed(2)}s</p>
                </div>
            `;
        }

        msgDiv.innerHTML = html;
        chatContainer.appendChild(msgDiv);
        chatContainer.classList.add('visible'); // Ensure container is visible
        
        // Scroll to bottom
        // window.scrollTo(0, document.body.scrollHeight);
    }

    // --- Init ---
    async function loadComponents() {
        try {
            const data = await fetchApi('/components');
            availableComponents = data;

            // Populate Retrieval Select
            retrievalSelect.innerHTML = '';
            data.mcp_tools.forEach(tool => {
                const option = document.createElement('option');
                option.value = tool.id;
                option.textContent = tool.name;
                if (tool.id === 'tavily') option.selected = true;
                retrievalSelect.appendChild(option);
            });

            // Populate LLM Select
            llmSelect.innerHTML = '';
            data.llm_models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.name;
                if (model.id === 'claude') option.selected = true;
                llmSelect.appendChild(option);
            });

        } catch (e) {
            console.error("Error loading components:", e);
            retrievalSelect.innerHTML = '<option>Error loading options</option>';
        }
    }

    // --- Event Handlers ---

    // 1. Start Session
    setupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const url = targetUrlInput.value.trim();
        if (!url) return;

        // Save State
        sessionState.mcpTool = retrievalSelect.value;
        sessionState.llmModel = llmSelect.value;
        sessionState.targetUrl = url;
        sessionState.sessionId = generateUUID(); // New Session ID

        // Update UI
        try {
            activeUrlSpan.textContent = new URL(url).hostname;
        } catch {
            activeUrlSpan.textContent = url;
        }
        activeConfigSpan.textContent = `${availableComponents.mcp_tools.find(t => t.id === sessionState.mcpTool).name} + ${availableComponents.llm_models.find(m => m.id === sessionState.llmModel).name}`;
        
        setupSection.classList.add('hidden');
        chatSection.classList.remove('hidden');
        
        // Clear previous chat if any (though reload handles this, pure JS state might not)
        chatContainer.innerHTML = ''; 
        
        questionInput.focus();
    });

    // 2. Ask Question
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;

        // Add User Message to UI immediately
        appendMessage('user', question);
        questionInput.value = ''; // Clear input

        // UI State: Loading
        queryBtn.disabled = true;
        queryBtn.textContent = 'Analyzing...';
        questionInput.disabled = true;
        setStatus('🤔 Investigating website and generating expert answer...', 'loading');

        try {
            const data = await fetchApi('/query', 'POST', { 
                question: question,
                mcp_tool: sessionState.mcpTool,
                llm_model: sessionState.llmModel,
                target_url: sessionState.targetUrl,
                session_id: sessionState.sessionId
            });
            
            setStatus('', ''); // Clear status

            // Add AI Message to UI
            appendMessage('assistant', data.answer, { sources: data.sources, metrics: data.metrics });

        } catch (error) {
            setStatus(`❌ Error: ${error.message}`, 'error');
        } finally {
            queryBtn.disabled = false;
            queryBtn.textContent = 'Ask Question';
            questionInput.disabled = false;
            questionInput.focus();
        }
    });

    // 3. New Session
    newSessionBtn.addEventListener('click', () => {
        if (confirm("Start a new session? Current conversation history will be cleared.")) {
            window.location.reload();
        }
    });

    // Start
    loadComponents();
});