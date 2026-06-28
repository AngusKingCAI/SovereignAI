// SovereignAI web UI - vanilla JavaScript application

document.addEventListener('DOMContentLoaded', () => {
    // Fetch and render capabilities on load
    fetchCapabilities();

    // Setup SSE connection
    setupSSE();

    // Setup task form
    setupTaskForm();

    // Setup log drawer toggle
    setupLogToggle();
});

function fetchCapabilities() {
    fetch('/api/capabilities')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('capability-list');
            list.innerHTML = '';
            data.forEach(cap => {
                const li = document.createElement('li');
                li.textContent = `${cap.category}/${cap.name} - ${cap.description} (priority: ${cap.priority})`;
                list.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Failed to fetch capabilities:', error);
        });
}

function setupSSE() {
    const eventSource = new EventSource('/api/traces/stream');
    const statusDiv = document.getElementById('connection-status');
    const logContent = document.getElementById('log-content');

    eventSource.addEventListener('open', () => {
        statusDiv.textContent = 'Connected';
        statusDiv.style.color = 'green';
    });

    eventSource.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        const logEntry = document.createElement('div');
        logEntry.className = `trace-${data.level}`;
        logEntry.textContent = `[${data.timestamp}] [${data.level}] [${data.component}] ${data.message}`;
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    });

    eventSource.addEventListener('gap', (event) => {
        const data = JSON.parse(event.data);
        const logEntry = document.createElement('div');
        logEntry.className = 'trace-warn';
        logEntry.textContent = `--- GAP: ${data.dropped} events dropped ---`;
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    });

    eventSource.addEventListener('task_state', (event) => {
        const data = JSON.parse(event.data);
        const logEntry = document.createElement('div');
        logEntry.className = 'trace-info';
        logEntry.textContent = `[TASK STATE] Task ${data.task_id}: ${data.old_state} -> ${data.new_state}`;
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    });

    eventSource.addEventListener('error', () => {
        statusDiv.textContent = 'Reconnecting...';
        statusDiv.style.color = 'orange';
    });
}

function setupTaskForm() {
    const form = document.getElementById('task-form');
    const taskStatusContent = document.getElementById('task-status-content');
    let pollInterval = null;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const taskData = {
            category: formData.get('category'),
            capability_name: formData.get('capability_name'),
            payload: formData.get('payload')
        };

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            taskStatusContent.textContent = `Task submitted: ${result.task_id} (state: ${result.state})`;

            // Start polling task state
            if (pollInterval) {
                clearInterval(pollInterval);
            }
            pollInterval = setInterval(() => pollTaskState(result.task_id), 1000);
        } catch (error) {
            console.error('Failed to submit task:', error);
            taskStatusContent.textContent = `Error: ${error.message}`;
        }
    });

    function pollTaskState(taskId) {
        fetch(`/api/tasks/${taskId}`)
            .then(response => response.json())
            .then(data => {
                taskStatusContent.textContent = `Task ${taskId}: state=${data.state}`;
                if (data.state === 'COMPLETE' || data.state === 'FAILED') {
                    clearInterval(pollInterval);
                    if (data.state === 'COMPLETE') {
                        taskStatusContent.textContent = `Task ${taskId}: COMPLETE - ${data.result || 'No result'}`;
                    } else {
                        taskStatusContent.textContent = `Task ${taskId}: FAILED - ${data.error || 'No error details'}`;
                    }
                }
            })
            .catch(error => {
                console.error('Failed to poll task state:', error);
            });
    }
}

function setupLogToggle() {
    const toggleButton = document.getElementById('log-toggle');
    const logDrawer = document.getElementById('log-drawer');
    const logContent = document.getElementById('log-content');

    toggleButton.addEventListener('click', () => {
        if (logContent.style.display === 'none') {
            logContent.style.display = 'block';
        } else {
            logContent.style.display = 'none';
        }
    });
}
