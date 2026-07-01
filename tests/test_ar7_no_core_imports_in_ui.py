from __future__ import annotations

import ast
from pathlib import Path

import pytest

CORE_INTERNALS_CONCRETE_DENYLIST = {'sovereignai.shared.event_bus', 'sovereignai.shared.lifecycle_manager', 'sovereignai.shared.routing_engine', 'sovereignai.shared.dag_validator', 'sovereignai.shared.manifest_parser', 'sovereignai.shared.relay_placeholder', 'sovereignai.shared.container'}
WEB_MAIN_ALLOWED_IMPORTS = {'sovereignai.shared.container', 'sovereignai.shared.container.DIContainer', 'sovereignai.shared.event_bus', 'sovereignai.shared.event_bus.EventBus', 'sovereignai.shared.capability_api', 'sovereignai.shared.capability_api.CapabilityAPI', 'sovereignai.shared.capability_graph', 'sovereignai.shared.capability_graph.ICapabilityIndex', 'sovereignai.shared.auth', 'sovereignai.shared.auth.AuthMiddleware', 'sovereignai.shared.trace_emitter', 'sovereignai.shared.trace_emitter.TraceEmitter', 'sovereignai.shared.types', 'sovereignai.shared.types.CapabilityCategory', 'sovereignai.shared.types.TaskState', 'sovereignai.shared.types.TASK_STATE_CHANNEL', 'sovereignai.shared.types.TaskStateChanged', 'sovereignai.shared.types.TraceLevel', 'sovereignai.shared.task_state_machine', 'sovereignai.shared.task_state_machine.ITaskStateQuery', 'sovereignai.shared.database_registry', 'sovereignai.shared.database_registry.DatabaseRegistry', 'sovereignai.shared.service_registry', 'sovereignai.shared.service_registry.ServiceRegistry'}
UI_PACKAGE_DENYLIST = {'sovereignai.shared', 'sovereignai.orchestrator', 'sovereignai.managers', 'sovereignai.workers', 'sovereignai.librarian', 'sovereignai.adapters', 'sovereignai.skills'}
UI_DIRECTORIES = ['web', 'cli', 'tui', 'phone']
CAPABILITY_API_FILE = 'sovereignai/shared/capability_api.py'

def _scan_imports(file_path: Path) -> set[str]:
    tree = ast.parse(file_path.read_text())
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
            for alias in node.names:
                imports.add(f'{node.module}.{alias.name}')
    return imports

def test_capability_api_does_not_import_concrete_core_classes() -> None:
    api_path = Path(CAPABILITY_API_FILE)
    if not api_path.exists():
        pytest.skip('Capability API not yet created')
    imports = _scan_imports(api_path)
    forbidden = {imp for imp in imports if any(imp.startswith(prefix) for prefix in CORE_INTERNALS_CONCRETE_DENYLIST)}
    assert not forbidden, f'Capability API imports forbidden concrete core modules: {forbidden}. Per AR7, it must import only protocols (ICapabilityIndex, ITaskStateQuery), never concrete classes.'

@pytest.mark.parametrize('ui_dir', UI_DIRECTORIES)
def test_ui_directories_do_not_import_core_internals(ui_dir: str) -> None:
    ui_path = Path(__file__).resolve().parent.parent / ui_dir
    if not ui_path.exists():
        pytest.skip(f'UI directory {ui_dir}/ does not exist yet')
    py_files = list(ui_path.rglob('*.py'))
    if not py_files:
        pytest.skip(f'No .py files in {ui_dir}/ yet')
    for py_file in py_files:
        imports = _scan_imports(py_file)
        forbidden_concrete = {imp for imp in imports if any(imp.startswith(prefix) for prefix in CORE_INTERNALS_CONCRETE_DENYLIST)}
        forbidden_package = {imp for imp in imports if any(imp.startswith(prefix) for prefix in UI_PACKAGE_DENYLIST)}
        is_web_main = py_file.name == 'main.py' and py_file.parent.name == 'web'
        if is_web_main:
            forbidden_concrete -= WEB_MAIN_ALLOWED_IMPORTS
            forbidden_package -= {'sovereignai.main'}
            forbidden_package -= {imp for imp in forbidden_package if imp.startswith('sovereignai.shared')}
        assert not forbidden_concrete, f'{py_file} imports forbidden concrete core modules: {forbidden_concrete}. Per AR7, UIs must consume the Capability API only.'
        assert not forbidden_package, f'{py_file} imports forbidden package: {forbidden_package}. Per AR7, UIs must not import sovereignai.* packages directly.'
