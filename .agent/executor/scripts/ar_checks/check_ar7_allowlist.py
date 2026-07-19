#!/usr/bin/env python3
"""AR7 allowlist check: Verify UI files import only allowed sovereignai.* modules per AR12."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Allowlist from test_ar7_no_core_imports_in_ui.py
WEB_MAIN_ALLOWED_IMPORTS = {
    'sovereignai.shared.container',
    'sovereignai.shared.container.DIContainer',
    'sovereignai.shared.event_bus',
    'sovereignai.shared.event_bus.EventBus',
    'sovereignai.shared.event_registry',
    'sovereignai.shared.event_registry.EventRegistry',
    'sovereignai.shared.capability_api',
    'sovereignai.shared.capability_api.CapabilityAPI',
    'sovereignai.shared.capability_graph',
    'sovereignai.shared.capability_graph.ICapabilityIndex',
    'sovereignai.shared.auth',
    'sovereignai.shared.auth.AuthMiddleware',
    'sovereignai.shared.trace_emitter',
    'sovereignai.shared.trace_emitter.TraceEmitter',
    'sovereignai.shared.types',
    'sovereignai.shared.types.CapabilityCategory',
    'sovereignai.shared.types.TaskState',
    'sovereignai.shared.types.TASK_STATE_CHANNEL',
    'sovereignai.shared.types.TaskStateChanged',
    'sovereignai.shared.types.TraceLevel',
    'sovereignai.shared.task_state_machine',
    'sovereignai.shared.task_state_machine.ITaskStateQuery',
    'sovereignai.main',
    'sovereignai.main.build_container',
    'sovereignai.skills.runner',
    'sovereignai.skills.runner.ISkillRunner',
    'sovereignai.skills.session',
    'sovereignai.skills.session.SkillSession',
    'sovereignai.managers.coding',
    'sovereignai.managers.coding.CodingManager',
    'sovereignai.indexing.symbol_map',
    'sovereignai.indexing.symbol_map.SymbolMap',
    'sovereignai.indexing.symbol_map.SymbolMapUnavailableError',
    'sovereignai.memory.graph_backend',
    'sovereignai.memory.graph_backend.TaskGraphCache',
}

TUI_ALLOWED_IMPORTS = {
    'sovereignai.shared.container',
    'sovereignai.shared.container.DIContainer',
    'sovereignai.shared.capability_api',
    'sovereignai.shared.capability_api.CapabilityAPI',
    'sovereignai.shared.capability_graph',
    'sovereignai.shared.capability_graph.ICapabilityIndex',
    'sovereignai.shared.auth',
    'sovereignai.shared.auth.AuthMiddleware',
    'sovereignai.shared.auth.AuthError',
    'sovereignai.shared.trace_emitter',
    'sovereignai.shared.trace_emitter.TraceEmitter',
    'sovereignai.shared.types',
    'sovereignai.shared.types.CapabilityCategory',
    'sovereignai.shared.types.CapabilityQuery',
    'sovereignai.shared.types.TaskState',
    'sovereignai.shared.types.TraceLevel',
    'sovereignai.shared.task_state_machine',
    'sovereignai.shared.task_state_machine.ITaskStateQuery',
    'sovereignai.main',
    'sovereignai.main.build_container',
    'sovereignai.shared.lifecycle_manager',
    'sovereignai.shared.lifecycle_manager.LifecycleManager',
    'sovereignai.shared.hardware_probe',
    'sovereignai.shared.hardware_probe.HardwareProbe',
    'sovereignai.shared.model_catalog',
    'sovereignai.shared.model_catalog.ModelCatalog',
    'sovereignai.shared.librarian',
    'sovereignai.shared.librarian.Librarian',
    'sovereignai.managers.coding',
    'sovereignai.managers.coding.CodingManager',
}

CORE_INTERNALS_CONCRETE_DENYLIST = {
    'sovereignai.shared.event_bus',
    'sovereignai.shared.lifecycle_manager',
    'sovereignai.shared.routing_engine',
    'sovereignai.shared.dag_validator',
    'sovereignai.shared.manifest_parser',
    'sovereignai.shared.relay_placeholder',
    'sovereignai.shared.container'
}

UI_PACKAGE_DENYLIST = {
    'sovereignai.shared',
    'sovereignai.orchestrator',
    'sovereignai.managers',
    'sovereignai.workers',
    'sovereignai.librarian',
    'sovereignai.adapters',
    'sovereignai.skills',
}

WEB_TUI_DIRECTORIES = ['app/web', 'app/tui']


def _scan_imports(file_path: Path) -> set[str]:
    """Scan Python file for import statements."""
    tree = ast.parse(file_path.read_text(encoding='utf-8'))
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


def check_file(file_path: Path, ui_dir: str) -> list[str]:
    """Check a single file for AR7 violations. Returns list of error messages."""
    errors: list[str] = []
    imports = _scan_imports(file_path)

    forbidden_concrete = {
        imp for imp in imports
        if any(imp.startswith(prefix) for prefix in CORE_INTERNALS_CONCRETE_DENYLIST)
    }
    forbidden_package = {
        imp for imp in imports
        if any(imp.startswith(prefix) for prefix in UI_PACKAGE_DENYLIST)
    }

    is_web_main = file_path.name == 'main.py' and file_path.parent.name == 'web'
    is_tui_main = file_path.name == 'main.py' and file_path.parent.name == 'tui'
    is_tui_file = (
        file_path.parent.name == 'tui'
        or (file_path.parent.name == 'panels' and file_path.parent.parent.name == 'tui')
    )

    if is_web_main:
        forbidden_concrete -= WEB_MAIN_ALLOWED_IMPORTS
        forbidden_package -= {'sovereignai.main'}
        allowed_skills = {
            'sovereignai.skills.runner',
            'sovereignai.skills.runner.ISkillRunner',
            'sovereignai.skills.session',
            'sovereignai.skills.session.SkillSession',
        }
        forbidden_package -= allowed_skills
        forbidden_package -= {
            imp for imp in forbidden_package
            if imp.startswith('sovereignai.shared')
        }
    if is_tui_main or is_tui_file:
        forbidden_concrete -= TUI_ALLOWED_IMPORTS
        forbidden_package -= {'sovereignai.main'}
        forbidden_package -= {
            imp for imp in forbidden_package
            if imp.startswith('sovereignai.shared')
        }

    if forbidden_concrete:
        errors.append(
            f'{file_path}: imports forbidden concrete core modules: '
            f'{forbidden_concrete}. Per AR7, UIs must consume the Capability API only.'
        )
    if forbidden_package:
        errors.append(
            f'{file_path}: imports forbidden package: {forbidden_package}. '
            'Per AR7, UIs must not import sovereignai.* packages directly.'
        )

    return errors


def main() -> int:
    """Check all UI files for AR7 allowlist compliance."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    all_errors: list[str] = []

    for ui_dir in WEB_TUI_DIRECTORIES:
        ui_path = repo_root / ui_dir
        if not ui_path.exists():
            continue

        py_files = list(ui_path.rglob('*.py'))
        for py_file in py_files:
            errors = check_file(py_file, ui_dir)
            all_errors.extend(errors)

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1

    print('AR7 allowlist check passed: All UI files import only allowed sovereignai.* modules')
    return 0


if __name__ == '__main__':
    sys.exit(main())
