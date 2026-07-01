// SovereignAI web UI - vanilla JavaScript application

let traces = [];
let maxTraces = 1000;
let eventSource = null;

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
        case 'workers':
            loadWorkers();
            break;
        case 'tasks':
            loadTasks();
            break;
        case 'skills':
            loadSkills();
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
        case 'logs':
            loadLogsPanel();
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

function loadOptions() {
    fetch('/api/databases')
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
            const list = document.getElementById('databases-list');
            list.innerHTML = '';
            data.forEach(db => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${db.name}</strong> (${db.status})<br>Models: ${db.models.length > 0 ? db.models.join(', ') : 'None'}`;
                list.appendChild(li);
            });
        })
        .catch(error => {
            if (error.message !== 'Unauthorized' && error.message !== 'Server error') {
                console.error('Failed to fetch databases:', error);
                showNetworkError();
            }
        });

    fetch('/api/services')
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
            const list = document.getElementById('services-list');
            list.innerHTML = '';
            data.forEach(svc => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${svc.name}</strong> (${svc.status})<br>PID: ${svc.pid || 'N/A'} | Port: ${svc.port || 'N/A'}`;
                list.appendChild(li);
            });
        })
        .catch(error => {
            if (error.message !== 'Unauthorized' && error.message !== 'Server error') {
                console.error('Failed to fetch services:', error);
                showNetworkError();
            }
        });
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

let logsEvents = [];
let logsPaused = false;
let logsEventSource = null;

function loadLogsPanel() {
    fetch('/api/traces/history')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }
            return response.json();
        })
        .then(data => {
            logsEvents = data;
            renderLogsTable();
            setupLogsSSE();
            setupLogsControls();
        })
        .catch(error => {
            if (error.message !== 'Unauthorized') {
                console.error('Failed to load logs history:', error);
            }
        });
}

function setupLogsSSE() {
    if (logsEventSource) {
        logsEventSource.close();
    }

    logsEventSource = new EventSource('/api/traces/stream');

    logsEventSource.addEventListener('trace', (event) => {
        if (logsPaused) return;
        const data = JSON.parse(event.data);
        logsEvents.push(data);
        if (logsEvents.length > 1000) {
            logsEvents.shift();
        }
        renderLogsTable();
    });

    logsEventSource.addEventListener('error', () => {
        console.error('Logs SSE error');
        logsEventSource.close();
        logsEventSource = null;
    });
}

function setupLogsControls() {
    const levelFilter = document.getElementById('logs-level-filter');
    const componentFilter = document.getElementById('logs-component-filter');
    const searchInput = document.getElementById('logs-search');
    const pauseButton = document.getElementById('logs-pause');

    if (levelFilter) {
        levelFilter.addEventListener('change', renderLogsTable);
    }

    if (componentFilter) {
        componentFilter.addEventListener('change', renderLogsTable);
    }

    if (searchInput) {
        searchInput.addEventListener('input', renderLogsTable);
    }

    if (pauseButton) {
        pauseButton.addEventListener('click', toggleLogsPause);
    }
}

function toggleLogsPause() {
    logsPaused = !logsPaused;
    const pauseButton = document.getElementById('logs-pause');
    if (pauseButton) {
        pauseButton.textContent = logsPaused ? 'Resume' : 'Pause';
    }
}

function renderLogsTable() {
    const tbody = document.getElementById('logs-table-body');
    if (!tbody) return;

    const levelFilter = document.getElementById('logs-level-filter')?.value || 'all';
    const componentFilter = document.getElementById('logs-component-filter')?.value || 'all';
    const searchTerm = document.getElementById('logs-search')?.value.toLowerCase() || '';

    const filtered = logsEvents.filter(event => {
        if (levelFilter !== 'all' && event.level !== levelFilter) return false;
        if (componentFilter !== 'all' && event.component !== componentFilter) return false;
        if (searchTerm && !event.message.toLowerCase().includes(searchTerm)) return false;
        return true;
    });

    tbody.innerHTML = '';
    filtered.forEach(event => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(event.timestamp).toLocaleString()}</td>
            <td class="log-level-${event.level.toLowerCase()}">${event.level}</td>
            <td>${event.component}</td>
            <td>${event.correlation_id}</td>
            <td>${event.message}</td>
        `;
        tbody.appendChild(row);
    });
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

    eventSource.addEventListener('error', async () => {
        console.error('SSE error, closing connection and checking auth');
        eventSource.close();
        eventSource = null;
        await checkAuthStatus();
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
                body: JSON.stringify({ message })
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

function setupLogDrawer() {
    const toggleButton = document.getElementById('log-toggle');
    const logDrawer = document.getElementById('log-drawer');

    toggleButton.addEventListener('click', () => {
        logDrawer.classList.toggle('open');
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

function renderTraces() {
    const logContent = document.getElementById('log-content');
    const filters = {
        levels: Array.from(document.querySelectorAll('#log-controls input[type="checkbox"][data-level]:checked'))
            .map(cb => cb.getAttribute('data-level')),
        search: document.getElementById('log-search').value.toLowerCase()
    };

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
