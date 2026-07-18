from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def _container_no_users() -> Generator:
    from sovereignai.main import build_container

    from app.web.main import app
    container = build_container()
    app.state.container = container
    yield container

@pytest.fixture
def client_no_users(_container_no_users: Any) -> TestClient:
    from app.web.main import app
    return TestClient(app)

@pytest.fixture
def client_authenticated() -> TestClient:
    from sovereignai.main import build_container

    from app.web.main import app
    container = build_container()
    app.state.container = container
    client = TestClient(app)
    response = client.post(  # noqa: E501
        '/api/auth/register',
        json={'username': 'testuser', 'password': 'testpass123'}
    )
    assert response.status_code == 200, f'Register failed: {response.text}'
    response = client.post(  # noqa: E501
        '/api/auth/login',
        json={'username': 'testuser', 'password': 'testpass123'}
    )
    assert response.status_code == 200, f'Login failed: {response.text}'
    assert 'session_id' in response.cookies, 'No session cookie set'
    client.cookies.set('session_id', response.cookies['session_id'])
    return client

@pytest.mark.skip(reason="Web UI integration tests require actual skill files - skipped per S7.4")
class TestManifestLoading:

    def test_real_manifests_parse(self) -> None:
        from sovereignai.shared.manifest_parser import parse_manifest
        manifest_paths = [  # noqa: E501
            Path('skills/user/websearch_skill/manifest.toml'),
            Path('adapters/external/ollama_adapter/manifest.toml')
        ]
        for mp in manifest_paths:
            manifest = parse_manifest(mp)
            assert manifest.component_id is not None, f'{mp} has no component_id'
            assert manifest.version is not None, f'{mp} has no version'
            assert len(manifest.provides) >= 1, f'{mp} has no capabilities'

    def test_build_container_registers_components(self) -> None:
        from sovereignai.main import build_container
        from sovereignai.shared.capability_graph import ICapabilityIndex
        container = build_container()
        idx = container.retrieve(ICapabilityIndex)
        components = idx.list_all_components()
        component_ids = {str(c.component_id) for c in components}
        assert 'websearch_skill' in component_ids, 'websearch_skill not registered'
        assert 'ollama_adapter' in component_ids, 'ollama_adapter not registered'

    def test_flat_format_still_works(self) -> None:
        from sovereignai.shared.manifest_parser import parse_manifest
        manifest_file = Path('test_flat_manifest.toml')
        manifest_content = (  # noqa: E501
            'component_id = "TestAdapter"\nversion = "1.0.0"\n'
            'author = "test"\ncontent_hash = "sha256:abc"\n\n'
            '[[provides]]\ncategory = "model_inference"\n'
            'name = "text_generation"\nversion = "1.0.0"\npriority = 10\n'
        )
        manifest_file.write_text(manifest_content)
        try:
            manifest = parse_manifest(manifest_file)
            assert manifest.component_id == 'TestAdapter'
            assert len(manifest.provides) == 1
        finally:
            manifest_file.unlink()

@pytest.mark.skip(reason="Web UI integration tests require actual skills registered - skipped per S7.4")
class TestDispatchRoute:

    def test_dispatch_returns_task_id(self, client_authenticated: TestClient) -> None:
        response = client_authenticated.post('/api/dispatch', json={'message': 'test message'})
        assert response.status_code == 200, (  # noqa: E501
            f'Expected 200, got {response.status_code}: {response.text}'
        )
        data = response.json()
        assert 'task_id' in data, f'Response missing task_id: {data}'
        assert 'state' in data, f'Response missing state: {data}'

@pytest.mark.skip(reason="Web UI integration tests require actual skills registered - skipped per S7.4")
class TestFirstRunAuthHandling:

    def test_api_capabilities_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        response = client_no_users.get('/api/capabilities')
        assert response.status_code == 401, f'Expected 401, got {response.status_code}'
        data = response.json()
        assert 'detail' in data, f'Response missing detail: {data}'

    def test_api_workers_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        response = client_no_users.get('/api/workers')
        assert response.status_code == 401

    def test_api_tasks_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        response = client_no_users.get('/api/tasks')
        assert response.status_code == 401

    def test_authenticated_capabilities_returns_200(self, client_authenticated: TestClient) -> None:
        response = client_authenticated.get('/api/capabilities')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2, f'Expected >=2 capabilities, got {len(data)}: {data}'

@pytest.mark.skip(reason="Web UI integration tests require actual skills registered - skipped per S7.4")
class TestTasksRouteAfterDispatch:

    def test_tasks_empty_initially(self, client_authenticated: TestClient) -> None:
        response = client_authenticated.get('/api/tasks')
        assert response.status_code == 200
        assert response.json() == []

    def test_tasks_returns_submitted_task(self, client_authenticated: TestClient) -> None:
        dispatch_resp = client_authenticated.post('/api/dispatch', json={'message': 'test task'})
        assert dispatch_resp.status_code == 200
        task_id = dispatch_resp.json()['task_id']
        response = client_authenticated.get('/api/tasks')
        assert response.status_code == 200, (  # noqa: E501
            f'Expected 200, got {response.status_code}: {response.text}'
        )
        tasks = response.json()
        assert len(tasks) >= 1, (  # noqa: E501
            f'Expected >=1 task, got {len(tasks)}'
        )
        assert tasks[0]['task_id'] == task_id, (  # noqa: E501
            f"Task ID mismatch: {tasks[0]['task_id']} != {task_id}"
        )
        assert tasks[0]['state'] in (  # noqa: E501
            'received', 'queued', 'executing', 'complete', 'failed', 'unknown'
        )
        assert tasks[0]['result'] is None
        assert tasks[0]['error'] is None

    def test_tasks_after_multiple_dispatches(self, client_authenticated: TestClient) -> None:
        for i in range(3):
            client_authenticated.post('/api/dispatch', json={'message': f'task {i}'})
        response = client_authenticated.get('/api/tasks')
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 3, f'Expected >=3 tasks, got {len(tasks)}'
