"""AR7 enforcement: UI processes and the Capability API must not import core internals.

Per A5: a static-import test confirms the Capability API has no
transitive imports from core internals. UI processes (web/, cli/,
tui/, phone/) are also subject to this rule.

This test scans Python files in the relevant directories and checks
their import statements against a deny-list of core modules.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

# Modules that are concrete core implementations — the Capability API
# may NOT import these directly. Per Finding 4 (Rev2): protocol modules
# (capability_graph, task_state_machine) are NOT in this list —
# the Capability API is allowed to import protocols (ICapabilityIndex,
# ITaskStateQuery). Per Rev3 Finding 4: auth and routing_engine removed
# (API legitimately imports AuthMiddleware; NoActiveProviderError moved
# to types.py). Only true concrete internals remain.
CORE_INTERNALS_CONCRETE_DENYLIST = {
    "sovereignai.shared.event_bus",
    "sovereignai.shared.lifecycle_manager",
    "sovereignai.shared.routing_engine",
    "sovereignai.shared.dag_validator",
    "sovereignai.shared.manifest_parser",
    "sovereignai.shared.relay_placeholder",
    # Per Rev7 Finding 3: "sovereignai.shared.trace_emitter" REMOVED from
    # this denylist. The Capability API legitimately imports TraceEmitter
    # for its constructor type annotation. TraceEmitter is a cross-cutting
    # observability contract (every component receives it via DI), not a
    # concrete implementation that the API should avoid. UIs are still
    # protected because UI_PACKAGE_DENYLIST has "sovereignai.shared" as a
    # prefix, which blocks "sovereignai.shared.trace_emitter".
    "sovereignai.shared.container",
}

# Package-level imports forbidden in UI directories only.
# Per Rev3 Finding 5: `import sovereignai.shared` then `shared.event_bus.publish()`
# bypasses the leaf-module denylist. UIs must not import the package.
# Per Rev3 Finding 8: `sovereignai.shared.types` also forbidden for UIs
# (types are core internals; UIs consume the Capability API only).
# Per Rev5 Finding 3: uses prefix matching (any import starting with a
# denied prefix is forbidden). Catches `import sovereignai.adapters.external.foo`.
# Per Rev5 Finding 4: `sovereignai.shared.types` REMOVED from UI denylist —
# UIs need types (CapabilityCategory, TaskState) to call the API. Types are
# data contracts, not implementation. Re-exported from capability_api.py.
UI_PACKAGE_DENYLIST = {
    "sovereignai.shared",
    "sovereignai.orchestrator",
    "sovereignai.managers",
    "sovereignai.workers",
    "sovereignai.librarian",
    "sovereignai.adapters",
    "sovereignai.skills",
}


# Directories to scan for forbidden imports
UI_DIRECTORIES = ["web", "cli", "tui", "phone"]
# Plus the Capability API itself (it imports protocols, not concrete classes)
CAPABILITY_API_FILE = "sovereignai/shared/capability_api.py"


def _scan_imports(file_path: Path) -> set[str]:
    """Return the set of module names imported by a Python file.

    Per Finding 4 (Rev2): scans both `ast.Import` and `ast.ImportFrom`
    nodes. For `ImportFrom`, checks both `node.module` AND each
    `alias.name` — catches `from sovereignai.shared import event_bus`
    where `node.module` is `sovereignai.shared` but `alias.name` is
    `event_bus` (a forbidden sub-module).

    Known limitation: does NOT catch dynamic imports
    (`importlib.import_module()`). A runtime `sys.modules` audit is
    deferred to DEBT until UI processes actually exist.

    Args:
        file_path: Path to a .py file.

    Returns:
        Set of fully-qualified module names imported.
    """
    tree = ast.parse(file_path.read_text())
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
            # Per Finding 4: also check each imported name as a sub-module
            # Catches `from sovereignai.shared import event_bus` where
            # node.module is "sovereignai.shared" and alias.name is "event_bus"
            for alias in node.names:
                imports.add(f"{node.module}.{alias.name}")
    return imports


def test_capability_api_does_not_import_concrete_core_classes() -> None:
    """Verify the Capability API imports only protocols, not concrete classes.

    Per A5: Plan 4's Capability API must import only ICapabilityIndex
    and ITaskStateQuery (protocols), never concrete implementation
    classes like EventBus or LifecycleManager.

    Per Finding 4 (Rev2): the denylist now excludes protocol modules
    (capability_graph, task_state_machine) — the API is allowed to
    import protocols. Only concrete implementation modules are
    forbidden. The test also catches `from ... import` sub-module forms.
    """
    api_path = Path(CAPABILITY_API_FILE)
    if not api_path.exists():
        pytest.skip("Capability API not yet created")
    imports = _scan_imports(api_path)
    forbidden = {
        imp
        for imp in imports
        if any(imp.startswith(prefix) for prefix in CORE_INTERNALS_CONCRETE_DENYLIST)
    }
    assert not forbidden, (
        f"Capability API imports forbidden concrete core modules: {forbidden}. "
        f"Per AR7, it must import only protocols (ICapabilityIndex, "
        f"ITaskStateQuery), never concrete classes."
    )


@pytest.mark.parametrize("ui_dir", UI_DIRECTORIES)
def test_ui_directories_do_not_import_core_internals(ui_dir: str) -> None:
    """Verify UI process directories do not import from sovereignai/ internals.

    Per AR7: UIs (web, cli, tui, phone) are separate processes that
    consume the Capability API. They may not import from core
    internals directly.

    Per Finding 4 (Rev2): the test catches `from ... import` sub-module forms.

    Per Rev3 Finding 5: also checks for package-level imports
    (`import sovereignai.shared` then attribute access).

    Per Rev3 Finding 8: also checks for `sovereignai.shared.types`.

    Currently these directories are empty (no UI code yet — UIs are
    post-batch). This test will start enforcing once UI files exist.
    """
    ui_path = Path(__file__).resolve().parent.parent / ui_dir
    if not ui_path.exists():
        pytest.skip(f"UI directory {ui_dir}/ does not exist yet")
    py_files = list(ui_path.rglob("*.py"))
    if not py_files:
        pytest.skip(f"No .py files in {ui_dir}/ yet")
    for py_file in py_files:
        imports = _scan_imports(py_file)
        # Per Rev5 Finding 3: prefix matching for both denylists
        forbidden_concrete = {
            imp
            for imp in imports
            if any(imp.startswith(prefix) for prefix in CORE_INTERNALS_CONCRETE_DENYLIST)
        }
        forbidden_package = {
            imp for imp in imports if any(imp.startswith(prefix) for prefix in UI_PACKAGE_DENYLIST)
        }
        assert not forbidden_concrete, (
            f"{py_file} imports forbidden concrete core modules: {forbidden_concrete}. "
            f"Per AR7, UIs must consume the Capability API only."
        )
        assert not forbidden_package, (
            f"{py_file} imports forbidden package: {forbidden_package}. "
            f"Per AR7, UIs must not import sovereignai.* packages directly."
        )
