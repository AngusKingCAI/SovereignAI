// SovereignAI web UI - vanilla JavaScript application

let traces = [];
let maxTraces = 1000;
let eventSource = null;
let currentTaskId = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Check auth status on page load
    await checkAuthStatus();

    // Deep-link restoration
    const hash = location.hash.slice(1) || 'orchestrator';
    showPanel(hash);

    // Setup panel navigation
    setupPanelNavigation();

    // Setup SSE connection
    setupSSE();

    // Setup chat form
    setupChatForm();

    // Setup log drawer
    setupLogDrawer();

    // Add logout button
    addLogoutButton();

    // Load initial panel content
    loadPanelContent(hash);

    // Load model selector on startup
    loadModelSelector();

    // Start Ollama status polling
    startOllamaStatusPolling();
});

async function checkAuthStatus() {
    try {
        const response = await fetch('/api/capabilities');
        if (response.status === 401) {
            const data = await response.json();
            if (data.detail && data.detail.includes('No user registered')) {
                window.location.href = '/register';
            } else {
                window.location.href = '/login';
            }
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}

function showPanel(name) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById('panel-' + name);
    if (panel) {
        panel.classList.add('active');
    }
    document.querySelectorAll('.sidebar-nav li').forEach(li => li.classList.remove('active'));
    const navItem = document.querySelector('[data-panel="' + name + '"]');
    if (navItem) {
        navItem.classList.add('active');
    }
    history.pushState(null, '', '#' + name);
    loadPanelContent(name);
}

function setupPanelNavigation() {
    document.querySelectorAll('.sidebar-nav li').forEach(li => {
        li.addEventListener('click', () => {
            const panelName = li.getAttribute('data-panel');
            showPanel(panelName);
        });
    });

    window.addEventListener('popstate', () => {
        const hash = location.hash.slice(1) || 'orchestrator';
        showPanel(hash);
    });
}

function loadPanelContent(panelName) {
    switch (panelName) {
        case 'orchestrator':
            loadModelSelector();
            break;
        case 'workers':
            loadWorkers();
            break;
        case 'tasks':
            loadTasks();
            break;
        case 'skills':
            loadSkills();
            break;
        case 'memory':
            loadMemory();
            break;
        case 'models':
            loadInstalledModels();
            break;
        case 'adapters':
            loadAdapters();
            break;
        case 'hardware':
            loadHardware();
            break;
        case 'options':
            loadOptions();
            break;
    }
}

function loadWorkers() {
    fetch('/api/workers')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            if (response.status === 500) {
                showToast('Server error — check Log drawer for details', 'error');
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            const list = document.getElementById('workers-list');
            list.innerHTML = '';
            data.forEach(worker => {
                const li = document.createElement('li');
                li.textContent = `${worker.name} (${worker.category})`;
                list.appendChild(li);
            });
        })
        .catch(error => {
            if (error.message !== 'Unauthorized' && error.message !== 'Server error') {
                console.error('Failed to fetch workers:', error);
                showNetworkError();
            }
        });
}

function loadTasks() {
    fetch('/api/tasks')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            if (response.status === 500) {
                showToast('Server error — check Log drawer for details', 'error');
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            const list = document.getElementById('tasks-list');
            list.innerHTML = '';
            data.forEach(task => {
                const li = document.createElement('li');
                li.textContent = `Task ${task.task_id}: ${task.state}`;
                list.appendChild(li);
            });
        })
        .catch(error => {
            if (error.message !== 'Unauthorized' && error.message !== 'Server error') {
                console.error('Failed to fetch tasks:', error);
                showNetworkError();
            }
        });
}

function loadSkills() {
    fetch('/api/capabilities')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            if (response.status === 500) {
                showToast('Server error — check Log drawer for details', 'error');
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            const list = document.getElementById('skills-list');
            list.innerHTML = '';
            data.filter(cap => cap.category === 'skill').forEach(skill => {
                const li = document.createElement('li');
                li.textContent = `${skill.name} - ${skill.description}`;
                list.appendChild(li);
            });
        })
        .catch(error => {
            if (error.message !== 'Unauthorized' && error.message !== 'Server error') {
                console.error('Failed to fetch skills:', error);
                showNetworkError();
            }
        });
}

function loadAdapters() {
    fetch('/api/capabilities')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            if (response.status === 500) {
                showToast('Server error — check Log drawer for details', 'error');
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            const list = document.getElementById('adapters-list');
            list.innerHTML = '';
            data.filter(cap => cap.category === 'adapter').forEach(adapter => {
                const li = document.createElement('li');
                li.textContent = `${adapter.name} - ${adapter.description}`;
                list.appendChild(li);
            });
        })
        .catch(error => {
            if (error.message !== 'Unauthorized' && error.message !== 'Server error') {
                console.error('Failed to fetch adapters:', error);
                showNetworkError();
            }
        });
}

function loadHardware() {
    fetch('/api/hardware')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            if (response.status === 500) {
                showToast('Server error — check Log drawer for details', 'error');
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            const info = document.getElementById('hardware-info');
            info.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;

            // Update Education section
            document.getElementById('gpu-status').textContent = data.has_nvidia_gpu ? 'Available' : 'Not available';
            document.getElementById('vram-info').textContent = data.vram_mb ? `${data.vram_mb} MB` : 'N/A';
            document.getElementById('teacher-status').textContent = data.teacher_available ? 'Ready' : 'Unavailable';
        })
        .catch(error => {
            if (error.message !== 'Unauthorized' && error.message !== 'Server error') {
                console.error('Failed to fetch hardware info:', error);
                showNetworkError();
            }
        });

    // Setup Education department buttons
    setupEducationButtons();
}

function setupEducationButtons() {
    const curateBtn = document.getElementById('curate-dataset-btn');
    const finetuneBtn = document.getElementById('finetune-btn');

    if (curateBtn) {
        curateBtn.addEventListener('click', () => {
            showToast('Dataset curation requires explicit consent — see API documentation', 'info');
        });
    }

    if (finetuneBtn) {
        finetuneBtn.addEventListener('click', () => {
            showToast('Fine-tuning requires GPU and QLoRA dependencies — see API documentation', 'info');
        });
    }
}

async function setupSSE() {
    // Check auth before opening SSE connection
    try {
        const authResponse = await fetch('/api/capabilities');
        if (authResponse.status === 401) {
            const data = await authResponse.json();
            if (data.detail && data.detail.includes('No user registered')) {
                window.location.href = '/register';
            } else {
                window.location.href = '/login';
            }
            return;
        }
    } catch (error) {
        console.error('Auth check failed before SSE:', error);
        return;
    }

    eventSource = new EventSource('/api/traces/stream');
    const logContent = document.getElementById('log-content');

    eventSource.addEventListener('open', () => {
        console.log('SSE connection opened');
    });

    eventSource.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        traces.push(data);
        if (traces.length > maxTraces) {
            traces.shift();
        }
        renderTraces();
        // Update thinking display when new traces arrive
        if (currentTaskId) {
            renderThinkingTraces();
        }
    });

    eventSource.addEventListener('gap', (event) => {
        const data = JSON.parse(event.data);
        const gapTrace = {
            timestamp: new Date().toISOString(),
            level: 'WARN',
            component: 'SSE',
            message: `--- GAP: ${data.dropped} events dropped ---`
        };
        traces.push(gapTrace);
        if (traces.length > maxTraces) {
            traces.shift();
        }
        renderTraces();
    });

    eventSource.addEventListener('task_state', (event) => {
        const data = JSON.parse(event.data);
        const taskTrace = {
            timestamp: new Date().toISOString(),
            level: 'INFO',
            component: 'TaskStateMachine',
            message: `Task ${data.task_id}: ${data.old_state} -> ${data.new_state}`
        };
        traces.push(taskTrace);
        if (traces.length > maxTraces) {
            traces.shift();
        }
        renderTraces();
        updateChatTaskState(data);
    });

    eventSource.addEventListener('error', () => {
        console.error('SSE connection error');
        eventSource.close();
        // Reconnect after 3 seconds
        setTimeout(() => {
            console.log('SSE reconnecting...');
            setupSSE();
        }, 3000);
    });
}

function setupChatForm() {
    const form = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;

        const userMessage = document.createElement('div');
        userMessage.className = 'chat-message user';
        userMessage.textContent = message;
        chatMessages.appendChild(userMessage);
        input.value = '';

        try {
            const response = await fetch('/api/dispatch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message, model: selectedModel })
            });

            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }

            if (response.status === 500) {
                showToast('Server error — check Log drawer for details', 'error');
                const errorMessage = document.createElement('div');
                errorMessage.className = 'chat-message error';
                errorMessage.textContent = 'Server error — check Log drawer for details';
                chatMessages.appendChild(errorMessage);
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            const assistantMessage = document.createElement('div');
            assistantMessage.className = 'chat-message assistant';
            assistantMessage.textContent = result.response || 'Task submitted';
            chatMessages.appendChild(assistantMessage);

            // Show thinking display for this task
            if (result.task_id) {
                showThinking(result.task_id);
                pollTaskCompletion(result.task_id);
            }
        } catch (error) {
            console.error('Failed to dispatch message:', error);
            showNetworkError();
            const errorMessage = document.createElement('div');
            errorMessage.className = 'chat-message error';
            errorMessage.textContent = 'Connection error — retrying...';
            chatMessages.appendChild(errorMessage);
        }
    });
}

function addLogoutButton() {
    const sidebar = document.getElementById('sidebar');
    const logoutButton = document.createElement('button');
    logoutButton.id = 'logout-button';
    logoutButton.textContent = 'Logout';
    logoutButton.addEventListener('click', () => {
        if (typeof Auth !== 'undefined' && Auth.logout) {
            Auth.logout();
        } else {
            fetch('/api/auth/logout', { method: 'POST' })
                .then(() => window.location.href = '/login')
                .catch(err => console.error('Logout failed:', err));
        }
    });
    sidebar.appendChild(logoutButton);
}

function showNetworkError() {
    const overlay = document.getElementById('network-error-overlay');
    overlay.classList.add('show');
}

function hideNetworkError() {
    const overlay = document.getElementById('network-error-overlay');
    overlay.classList.remove('show');
}

function showToast(message, type = 'error') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function updateChatTaskState(data) {
    const chatMessages = document.getElementById('chat-messages');
    const stateMessage = document.createElement('div');
    stateMessage.className = 'chat-message system';
    stateMessage.textContent = `Task ${data.task_id} is now ${data.new_state}`;
    chatMessages.appendChild(stateMessage);
}

function showThinking(taskId) {
    currentTaskId = taskId;
    document.getElementById('orchestrator-thinking').style.display = 'block';
    document.getElementById('thinking-status').textContent = 'Working...';
    document.getElementById('thinking-content').style.display = 'none';
}

function hideThinking() {
    document.getElementById('orchestrator-thinking').style.display = 'none';
    currentTaskId = null;
}

function toggleThinking() {
    const content = document.getElementById('thinking-content');
    const arrow = document.getElementById('thinking-arrow');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        arrow.textContent = '▲';
        renderThinkingTraces();
    } else {
        content.style.display = 'none';
        arrow.textContent = '▼';
    }
}

function renderThinkingTraces() {
    if (!currentTaskId) return;
    const content = document.getElementById('thinking-content');
    // Filter traces by this task's ID (correlation_id or task_id)
    const taskTraces = traces.filter(t =>
        t.task_id === currentTaskId || t.trace_id === currentTaskId
    );
    content.innerHTML = '';
    taskTraces.forEach(trace => {
        const entry = document.createElement('div');
        entry.className = `trace-entry trace-${trace.level}`;
        entry.textContent = `[${trace.level.toUpperCase()}] [${trace.component}] ${trace.message}`;
        content.appendChild(entry);
    });
    content.scrollTop = content.scrollHeight;
}

async function pollTaskCompletion(taskId) {
    const maxPolls = 150; // 5 minutes at 2s intervals
    for (let i = 0; i < maxPolls; i++) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        try {
            const response = await fetch(`/api/tasks/${taskId}`, { credentials: 'same-origin' });
            if (!response.ok) continue;
            const task = await response.json();
            if (task.state === 'complete' || task.state === 'failed') {
                hideThinking();
                displayTaskResult(task);
                return;
            }
            // Update thinking status with current state
            document.getElementById('thinking-status').textContent =
                `Working... (${task.state})`;
        } catch (error) {
            console.error('Task poll failed:', error);
        }
    }
    hideThinking();
    displayTaskResult({ state: 'timeout', error: 'Task did not complete within 5 minutes' });
}

function displayTaskResult(task) {
    const chatMessages = document.getElementById('chat-messages');
    const entry = document.createElement('div');
    entry.className = `chat-message chat-${task.state === 'complete' ? 'response' : 'error'}`;
    if (task.state === 'complete') {
        entry.textContent = task.result || 'Task completed successfully.';
    } else {
        entry.textContent = `Task failed: ${task.error || 'Unknown error'}`;
    }
    chatMessages.appendChild(entry);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setupLogDrawer() {
    const toggleButton = document.getElementById('log-toggle');
    const logDrawer = document.getElementById('log-drawer');
    const closeButton = document.getElementById('log-drawer-close');
    const reopenButton = document.getElementById('log-drawer-reopen');
    const dragHandle = document.getElementById('log-drawer-handle');

    // Restore open/closed state from localStorage
    const savedState = localStorage.getItem('logDrawerState');
    if (savedState === 'collapsed') {
        logDrawer.classList.remove('open');
        logDrawer.classList.add('collapsed');
    }

    // Restore height from localStorage
    const savedHeight = localStorage.getItem('logDrawerHeight');
    if (savedHeight && logDrawer.classList.contains('open')) {
        logDrawer.style.height = savedHeight;
    }

    toggleButton.addEventListener('click', () => {
        logDrawer.classList.toggle('open');
        logDrawer.classList.remove('collapsed');
        localStorage.setItem('logDrawerState', 'open');
    });

    closeButton.addEventListener('click', () => {
        logDrawer.classList.remove('open');
        logDrawer.classList.add('collapsed');
        localStorage.setItem('logDrawerState', 'collapsed');
    });

    reopenButton.addEventListener('click', () => {
        logDrawer.classList.remove('collapsed');
        logDrawer.classList.add('open');
        const savedHeight = localStorage.getItem('logDrawerHeight');
        if (savedHeight) {
            logDrawer.style.height = savedHeight;
        }
        localStorage.setItem('logDrawerState', 'open');
    });

    // Drag-to-resize functionality
    let isDragging = false;
    let startY = 0;
    let startHeight = 0;

    dragHandle.addEventListener('mousedown', (e) => {
        if (!logDrawer.classList.contains('open')) return;
        isDragging = true;
        startY = e.clientY;
        startHeight = logDrawer.offsetHeight;
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const deltaY = startY - e.clientY;
        const newHeight = Math.max(80, Math.min(window.innerHeight * 0.6, startHeight + deltaY));
        logDrawer.style.height = newHeight + 'px';
        localStorage.setItem('logDrawerHeight', newHeight + 'px');
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            document.body.style.userSelect = '';
        }
    });

    const levelCheckboxes = document.querySelectorAll('#log-controls input[type="checkbox"][data-level]');
    levelCheckboxes.forEach(cb => {
        cb.addEventListener('change', renderTraces);
    });

    const searchInput = document.getElementById('log-search');
    searchInput.addEventListener('input', renderTraces);

    const clearButton = document.getElementById('log-clear');
    clearButton.addEventListener('click', () => {
        traces = [];
        renderTraces();
    });
}

function updateComponentFilters() {
    const components = [...new Set(traces.map(t => t.component))].sort();
    const container = document.getElementById('log-components');
    if (!container) return;

    // Only add checkboxes for components not already present
    const existing = new Set(Array.from(container.querySelectorAll('input[type="checkbox"][data-component]'))
        .map(cb => cb.getAttribute('data-component')));

    components.forEach(comp => {
        if (!existing.has(comp)) {
            const label = document.createElement('label');
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.checked = true;
            cb.setAttribute('data-component', comp);
            cb.addEventListener('change', renderTraces);
            label.appendChild(cb);
            label.appendChild(document.createTextNode(' ' + comp));
            container.appendChild(label);
        }
    });
}

function renderTraces() {
    const logContent = document.getElementById('log-content');
    const filters = {
        levels: Array.from(document.querySelectorAll('#log-controls input[type="checkbox"][data-level]:checked'))
            .map(cb => cb.getAttribute('data-level')),
        components: Array.from(document.querySelectorAll('#log-components input[type="checkbox"][data-component]:checked'))
            .map(cb => cb.getAttribute('data-component')),
        search: document.getElementById('log-search').value.toLowerCase()
    };

    // Update component filters (add new components seen in traces)
    updateComponentFilters();

    const filteredTraces = filterTraces(traces, filters);

    logContent.innerHTML = '';
    filteredTraces.forEach(trace => {
        const entry = document.createElement('div');
        entry.className = `trace-entry trace-${trace.level.toLowerCase()}`;
        entry.textContent = `[${trace.timestamp}] [${trace.level}] [${trace.component}] ${trace.message}`;
        logContent.appendChild(entry);
    });

    const isAtBottom = logContent.scrollHeight - logContent.scrollTop === logContent.clientHeight;
    if (isAtBottom) {
        logContent.scrollTop = logContent.scrollHeight;
    }
}

// Models panel functions
let currentModelsTab = 'installed';
let hfOffset = 0;
const HF_PAGE_SIZE = 50;

function switchModelsTab(tab) {
    currentModelsTab = tab;
    document.querySelectorAll('.models-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.models-tab[onclick*="${tab}"]`).classList.add('active');
    document.querySelectorAll('.models-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`models-${tab}`).classList.add('active');
    if (tab === 'installed') loadInstalledModels();
    if (tab === 'huggingface') loadHFCatalog();
}

function loadInstalledModels() {
    fetch('/api/models/installed')
        .then(r => r.json())
        .then(models => {
            const list = document.getElementById('installed-models-list');
            list.innerHTML = '';
            if (models.length === 0) {
                list.innerHTML = '<p>No models installed. Pull a model from the HuggingFace tab or run <code>ollama pull llama3.2</code>.</p>';
                return;
            }
            models.forEach(m => {
                const entry = document.createElement('div');
                entry.className = 'model-entry installed';
                const size = m.size ? `${(m.size / 1e9).toFixed(1)}GB` : '';
                entry.innerHTML = `<span class="model-name">${m.id}</span> <span class="model-size">${size}</span>`;
                list.appendChild(entry);
            });
        });
}

function loadHFCatalog(reset) {
    if (reset === undefined) reset = true;
    if (reset) {
        hfOffset = 0;
        document.getElementById('hf-models-list').innerHTML = '';
    }
    const search = document.getElementById('hf-search').value;
    let url = `/api/models/catalog?limit=${HF_PAGE_SIZE}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (hfOffset > 0) url += `&offset=${hfOffset}`;

    fetch(url)
        .then(r => r.json())
        .then(data => {
            const models = data.models || [];
            const hardware = data.hardware || {};
            const list = document.getElementById('hf-models-list');
            if (reset && models.length === 0) {
                list.innerHTML = '<p>No models found. Try a different search.</p>';
                return;
            }

            // Remove existing Load More button
            const existingBtn = document.getElementById('load-more-btn');
            if (existingBtn) existingBtn.remove();

            // Group by family
            const byFamily = {};
            models.forEach(m => {
                const fam = m.family || 'Other';
                if (!byFamily[fam]) byFamily[fam] = [];
                byFamily[fam].push(m);
            });

            // Sort families by total downloads
            const sortedFamilies = Object.entries(byFamily)
                .sort((a, b) => {
                    const aTotal = a[1].reduce((s, m) => s + (m.downloads || 0), 0);
                    const bTotal = b[1].reduce((s, m) => s + (m.downloads || 0), 0);
                    return bTotal - aTotal;
                });

            for (const [family, familyModels] of sortedFamilies) {
                // Find existing family section or create new
                let section = document.querySelector(`[data-family="${family}"]`);
                if (!section) {
                    section = document.createElement('div');
                    section.className = 'model-family-section collapsed';
                    section.setAttribute('data-family', family);
                    const totalDl = familyModels.reduce((s, m) => s + (m.downloads || 0), 0);
                    const dlStr = totalDl > 1000 ? `${(totalDl / 1000).toFixed(0)}K` : totalDl;
                    section.innerHTML = `<h3 onclick="this.parentElement.classList.toggle('collapsed')">${family} (${familyModels.length} models, ⬇${dlStr}) ▶</h3>`;
                    const modelList = document.createElement('div');
                    modelList.className = 'family-models';
                    section.appendChild(modelList);
                    list.appendChild(section);
                }

                const modelList = section.querySelector('.family-models');
                familyModels.forEach(m => {
                    const entry = document.createElement('div');
                    entry.className = 'model-entry catalog';
                    const dl = m.downloads > 1000 ? `${(m.downloads / 1000).toFixed(0)}K` : (m.downloads || 0);

                    // Compute VRAM badge
                    const vramBadge = computeVRAMBadge(m.size_mb || 0, hardware.gpu_vram_mb, hardware.ram_total_mb);

                    entry.innerHTML = `
                        <span class="model-publisher">${m.publisher || ''}</span>
                        <span class="model-name">${m.name}</span>
                        <span class="model-downloads">⬇ ${dl}</span>
                        ${vramBadge}
                        <button class="pull-btn" onclick="showPullDialog('${m.id}')">Pull</button>
                    `;
                    modelList.appendChild(entry);
                });

                // Add load-all button if not already present
                if (!section.querySelector('.load-all-btn')) {
                    const loadAllBtn = document.createElement('button');
                    loadAllBtn.className = 'load-all-btn';
                    loadAllBtn.textContent = `Load all ${family} models`;
                    loadAllBtn.onclick = function() { loadAllFromFamily(family); };
                    section.appendChild(loadAllBtn);
                }
            }

            // Add Load More button if full page returned
            if (models.length === HF_PAGE_SIZE) {
                hfOffset += HF_PAGE_SIZE;
                const btn = document.createElement('button');
                btn.id = 'load-more-btn';
                btn.className = 'load-more-btn';
                btn.textContent = 'Load More Models';
                btn.onclick = function() { loadHFCatalog(false); };
                list.appendChild(btn);
            }
        });
}

function loadAllFromFamily(family) {
    // Search HuggingFace for the family name to get all models from that publisher/family
    const searchTerms = family.split(' / ').pop().toLowerCase(); // e.g., "Meta / Llama" -> "llama"
    const list = document.querySelector(`[data-family="${family}"] .family-models`);
    if (!list) return;

    // Show loading indicator
    const loading = document.createElement('p');
    loading.textContent = 'Loading all models...';
    loading.className = 'loading-text';
    list.appendChild(loading);

    // Fetch all models matching this family name (up to 200)
    fetch(`/api/models/catalog?search=${encodeURIComponent(searchTerms)}&limit=200`)
        .then(r => r.json())
        .then(models => {
            loading.remove();
            // Filter to only models matching this family
            const familyModels = models.filter(m => m.family === family);
            familyModels.forEach(m => {
                // Check if already in list
                const existing = list.querySelector(`[data-model-id="${m.id}"]`);
                if (existing) return;
                const entry = document.createElement('div');
                entry.className = 'model-entry catalog';
                entry.setAttribute('data-model-id', m.id);
                const dl = m.downloads > 1000 ? `${(m.downloads / 1000).toFixed(0)}K` : (m.downloads || 0);
                entry.innerHTML = `
                    <span class="model-publisher">${m.publisher || ''}</span>
                    <span class="model-name">${m.name}</span>
                    <span class="model-downloads">⬇ ${dl}</span>
                    <button class="pull-btn" onclick="showPullDialog('${m.id}')">Pull</button>
                `;
                list.appendChild(entry);
            });
        });
}

function showPullDialog(modelId) {
    // Fetch available quants first
    fetch(`/api/models/catalog/${encodeURIComponent(modelId)}`)
        .then(r => r.json())
        .then(data => {
            const files = data.files || [];
            const quants = files.map(f => f.quant).filter(Boolean);
            const defaultQuant = quants.includes('Q4_K_M') ? 'Q4_K_M' : quants[0] || '';

            const quantSelect = quants.length > 0
                ? `<select id="pull-quant">${quants.map(q => `<option value="${q}" ${q===defaultQuant?'selected':''}>${q}</option>`).join('')}</select>`
                : '<input type="text" id="pull-quant" placeholder="quant (e.g., Q4_K_M)" />';

            const dialog = document.createElement('div');
            dialog.className = 'pull-dialog';
            dialog.innerHTML = `
                <h3>Pull ${modelId}</h3>
                <label>Quantization: ${quantSelect}</label>
                <button onclick="confirmPull('${modelId}')">Pull</button>
                <button onclick="this.closest('.pull-dialog').remove()">Cancel</button>
            `;
            document.body.appendChild(dialog);
        });
}

function confirmPull(modelId) {
    const quant = document.getElementById('pull-quant').value;
    const btn = document.querySelector('.pull-dialog button');
    btn.textContent = 'Starting pull...';
    btn.disabled = true;

    fetch('/api/models/pull', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model: modelId, quant: quant}),
        credentials: 'same-origin',
    })
    .then(r => r.json())
    .then(result => {
        document.querySelector('.pull-dialog').remove();
        // Open log drawer so user sees progress
        document.getElementById('log-drawer').classList.add('open');
        // Poll for status
        pollPullStatus(modelId);
    })
    .catch(err => {
        alert('Failed to start pull: ' + err);
        document.querySelector('.pull-dialog').remove();
    });
}

function pollPullStatus(modelId) {
    const interval = setInterval(() => {
        fetch(`/api/models/pull-status/${encodeURIComponent(modelId)}`)
            .then(r => r.json())
            .then(status => {
                if (status.status === 'done') {
                    clearInterval(interval);
                    const locationMsg = status.ollama_path
                        ? `Model ${modelId} pulled successfully!\n\nStored at: ${status.ollama_path}`
                        : `Model ${modelId} pulled successfully!`;
                    alert(locationMsg);
                    // Refresh installed models
                    loadInstalledModels();
                    loadModelSelector();
                } else if (status.status === 'error') {
                    clearInterval(interval);
                    alert(`Pull failed: ${status.message}`);
                } else if (status.download_path) {
                    // Update message to show download path during download
                    const traceMsg = `Downloading to: ${status.download_path}`;
                    // Add to traces if not already there
                    const logContent = document.getElementById('log-content');
                    const existingMsg = Array.from(logContent.children).find(
                        el => el.textContent.includes('Downloading to:')
                    );
                    if (!existingMsg) {
                        const entry = document.createElement('div');
                        entry.className = 'trace-entry trace-info';
                        entry.textContent = traceMsg;
                        logContent.appendChild(entry);
                        logContent.scrollTop = logContent.scrollHeight;
                    }
                }
                // Status updates are in the log drawer via traces
            })
            .catch(() => {});
    }, 5000); // Poll every 5 seconds
}

// Orchestrator model selector
let selectedModel = null;

function computeVRAMBadge(modelSizeMb, gpuVramMb, ramTotalMb) {
    // Compute VRAM badge based on model size vs available hardware
    // Returns HTML string for badge or empty string if no GPU detected

    if (!gpuVramMb) {
        // No GPU detected, show RAM-based badge
        if (!ramTotalMb) return '';
        const ramGb = (ramTotalMb / 1024).toFixed(0);
        const modelGb = (modelSizeMb / 1024).toFixed(1);
        const ratio = modelSizeMb / ramTotalMb;

        if (ratio > 0.8) {
            return `<span class="vram-badge vram-warning" title="Requires ${modelGb}GB RAM, you have ${ramGb}GB">⚠ RAM</span>`;
        } else if (ratio > 0.5) {
            return `<span class="vram-badge vram-caution" title="Requires ${modelGb}GB RAM, you have ${ramGb}GB">RAM</span>`;
        }
        return '';
    }

    // GPU detected
    const gpuVramGb = (gpuVramMb / 1024).toFixed(0);
    const modelGb = (modelSizeMb / 1024).toFixed(1);
    const ratio = modelSizeMb / gpuVramMb;

    if (ratio > 1.2) {
        // Model significantly larger than GPU VRAM
        return `<span class="vram-badge vram-error" title="Requires ${modelGb}GB VRAM, GPU has ${gpuVramGb}GB">✗ ${modelGb}GB</span>`;
    } else if (ratio > 0.9) {
        // Model close to GPU VRAM limit
        return `<span class="vram-badge vram-warning" title="Requires ${modelGb}GB VRAM, GPU has ${gpuVramGb}GB">⚠ ${modelGb}GB</span>`;
    } else if (ratio > 0.5) {
        // Model uses significant portion of VRAM
        return `<span class="vram-badge vram-caution" title="Requires ${modelGb}GB VRAM, GPU has ${gpuVramGb}GB">${modelGb}GB</span>`;
    } else {
        // Model fits comfortably
        return `<span class="vram-badge vram-ok" title="Requires ${modelGb}GB VRAM, GPU has ${gpuVramGb}GB">${modelGb}GB</span>`;
    }
}

function loadModelSelector() {
    fetch('/api/models/installed')
        .then(r => r.json())
        .then(models => {
            const selector = document.getElementById('model-selector');
            const current = selector.value;
            selector.innerHTML = '<option value="">Select a model...</option>';
            models.forEach(m => {
                const option = document.createElement('option');
                option.value = m.id;
                option.textContent = m.id;
                if (m.id === current) option.selected = true;
                selector.appendChild(option);
            });
            if (models.length === 0) {
                selector.innerHTML = '<option value="">No models installed — pull one first</option>';
            }
        });
}

function selectModel(modelId) {
    selectedModel = modelId;
}

function loadMemory() {
    fetch('/api/memory/backends')
        .then(r => r.json())
        .then(backends => {
            const list = document.getElementById('memory-backends');
            list.innerHTML = '';
            backends.forEach(b => {
                const entry = document.createElement('div');
                entry.className = 'memory-backend-entry';
                const status = b.registered ? '✅' : '❌';
                entry.innerHTML = `
                    <h3>${b.type} ${status}</h3>
                    <p>Engine: ${b.engine}</p>
                    <p>Storage: ${b.storage}</p>
                    <p>Records: ${b.records}</p>
                `;
                list.appendChild(entry);
            });
        });
}

function loadOptions() {
    fetch('/api/options/config')
        .then(r => r.json())
        .then(config => {
            const list = document.getElementById('api-keys-list');
            list.innerHTML = '';
            for (const [provider, maskedKey] of Object.entries(config.api_keys)) {
                const entry = document.createElement('div');
                entry.className = 'api-key-entry';
                entry.innerHTML = `
                    <span>${provider}: ${maskedKey}</span>
                    <button onclick="deleteApiKey('${provider}')">Delete</button>
                `;
                list.appendChild(entry);
            }
            document.getElementById('ollama-host-display').textContent = config.ollama_host;
        });

    // Load storage paths
    fetch('/api/storage/paths')
        .then(r => r.json())
        .then(paths => {
            document.getElementById('cache-dir-display').textContent = paths.cache_dir;
            document.getElementById('ollama-models-dir-display').textContent = paths.ollama_models_dir;
        });
}

function saveApiKey() {
    const provider = document.getElementById('api-key-provider').value;
    const key = document.getElementById('api-key-value').value;
    if (!provider || !key) {
        alert('Provider and key are required');
        return;
    }
    fetch('/api/options/api-keys', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({provider, key}),
        credentials: 'same-origin',
    })
    .then(r => r.json())
    .then(result => {
        document.getElementById('api-key-provider').value = '';
        document.getElementById('api-key-value').value = '';
        loadOptions();
    });
}

function deleteApiKey(provider) {
    if (!confirm(`Delete API key for ${provider}?`)) return;
    fetch(`/api/options/api-keys/${provider}`, {
        method: 'DELETE',
        credentials: 'same-origin',
    })
    .then(() => loadOptions());
}

function startOllamaStatusPolling() {
    updateOllamaStatus();
    setInterval(updateOllamaStatus, 10000); // Poll every 10 seconds
}

async function updateOllamaStatus() {
    try {
        const response = await fetch('/api/ollama/status');
        const data = await response.json();
        const dot = document.getElementById('ollama-status-dot');
        const text = document.getElementById('ollama-status-text');
        const startBtn = document.getElementById('ollama-start-btn');

        if (data.status === 'running') {
            dot.className = 'status-dot running';
            text.textContent = `Running (v${data.version})`;
            startBtn.style.display = 'none';
        } else {
            dot.className = 'status-dot not-running';
            text.textContent = 'Not running';
            startBtn.style.display = 'inline-block';
        }
    } catch (error) {
        console.error('Failed to check Ollama status:', error);
        const dot = document.getElementById('ollama-status-dot');
        const text = document.getElementById('ollama-status-text');
        const startBtn = document.getElementById('ollama-start-btn');
        dot.className = 'status-dot not-running';
        text.textContent = 'Not running';
        startBtn.style.display = 'inline-block';
    }
}

async function startOllamaServe() {
    const startBtn = document.getElementById('ollama-start-btn');
    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';

    try {
        const response = await fetch('/api/ollama/start', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'starting') {
            // Poll for up to 10 seconds to check if it started successfully
            let attempts = 0;
            const maxAttempts = 10;
            const checkInterval = setInterval(async () => {
                attempts++;
                try {
                    const statusResponse = await fetch('/api/ollama/status');
                    const statusData = await statusResponse.json();
                    if (statusData.status === 'running') {
                        clearInterval(checkInterval);
                        updateOllamaStatus();
                    } else if (attempts >= maxAttempts) {
                        clearInterval(checkInterval);
                        startBtn.disabled = false;
                        startBtn.textContent = 'Start ollama serve';
                        alert('Ollama failed to start within 10 seconds. Check if it is installed.');
                    }
                } catch (error) {
                    if (attempts >= maxAttempts) {
                        clearInterval(checkInterval);
                        startBtn.disabled = false;
                        startBtn.textContent = 'Start ollama serve';
                        alert('Failed to check Ollama status after starting.');
                    }
                }
            }, 1000);
        }
    } catch (error) {
        startBtn.disabled = false;
        startBtn.textContent = 'Start ollama serve';
        alert('Failed to start Ollama: ' + error.message);
    }
}

// Add event listener for Start button
document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('ollama-start-btn');
    if (startBtn) {
        startBtn.addEventListener('click', startOllamaServe);
    }

    // Add event listeners for reveal buttons
    const revealCacheBtn = document.getElementById('reveal-cache-btn');
    if (revealCacheBtn) {
        revealCacheBtn.addEventListener('click', () => {
            const cacheDir = document.getElementById('cache-dir-display').textContent;
            if (cacheDir && cacheDir !== 'Loading...') {
                // On Windows, use explorer to open the directory
                window.open(`file:///${cacheDir.replace(/\\/g, '/')}`);
            }
        });
    }

    const revealOllamaBtn = document.getElementById('reveal-ollama-btn');
    if (revealOllamaBtn) {
        revealOllamaBtn.addEventListener('click', () => {
            const ollamaDir = document.getElementById('ollama-models-dir-display').textContent;
            if (ollamaDir && ollamaDir !== 'Loading...') {
                // On Windows, use explorer to open the directory
                window.open(`file:///${ollamaDir.replace(/\\/g, '/')}`);
            }
        });
    }
});
