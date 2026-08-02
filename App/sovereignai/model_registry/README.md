# Model Registry

A provider-agnostic model registry with synchronization, offline mode, SSE updates, and API layer.

## Architecture

The model registry is organized into several key components:

### Core Components

- **schema.py**: Pydantic models for data validation and database schema definitions
- **database.py**: SQLite database management with transaction safety
- **sync.py**: Provider synchronization service with adapter pattern
- **offline.py**: Offline mode with stale data detection
- **events.py**: Event bus for SSE updates
- **sse.py**: Server-Sent Events endpoint for real-time updates
- **api.py**: FastAPI routes for model and provider queries
- **ui_contract.py**: JSON data contract for TUI integration

### Provider Adapters

- **adapters/openai.py**: OpenAI API adapter
- **adapters/ollama.py**: Ollama adapter
- **adapters/__init__.py**: Adapter registry

## Database Schema

### Tables

- **providers**: Provider metadata (id, name, api_base_url, auth_type, is_enabled)
- **families**: Model families (id, provider_id, name, description)
- **models**: Model definitions (id, family_id, name)
- **model_versions**: Model versions with capabilities (id, model_id, version_string, release_date, is_latest, context_window, supports_vision, supports_tools, capabilities)
- **sync_runs**: Synchronization run tracking (id, provider_id, started_at, completed_at, status, error_class)
- **sync_errors**: Error logging (id, timestamp, provider_adapter_name, error_class, safe_error_message)

## Usage

### Initialization

```python
from sovereignai.model_registry.database import initialize_database

conn = initialize_database()
```

### Synchronization

```python
from sovereignai.model_registry.sync import ModelSyncService
from sovereignai.model_registry.adapters import get_adapter

adapter = get_adapter("openai")
service = ModelSyncService(conn)
result = service.sync_provider(adapter, "openai")
```

### Offline Mode

```python
from sovereignai.model_registry.offline import OfflineModeManager

manager = OfflineModeManager(conn, stale_threshold_hours=24)
is_fresh = manager.is_data_fresh("openai")
```

### API Layer

```python
from sovereignai.model_registry.api import app

# Run FastAPI server
uvicorn sovereignai.model_registry.api:app --reload
```

## AR Checks

The model registry includes architecture rule checks to ensure compliance:

- **No Direct Provider Calls**: Ensures provider API calls only go through SyncService
- **Adapter Registry**: Ensures all adapter modules are properly registered
- **Transaction Safety**: Ensures database operations use transactions

Run all checks:
```bash
python .agent/executor/checks/run_model_registry_ar_checks.py
```

## Testing

Run all model registry tests:
```bash
pytest .agent/executor/tests/sovereignai/test_model_registry/ -v
```

## Event Bus

The event bus provides real-time updates via SSE:

- **provider_sync_started**: Emitted when provider sync begins
- **provider_sync_completed**: Emitted when provider sync completes
- **provider_sync_failed**: Emitted when provider sync fails

Events include provider_id, status, and metadata.
