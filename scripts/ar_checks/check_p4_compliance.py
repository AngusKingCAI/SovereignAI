from __future__ import annotations

import ast
import sys
from pathlib import Path


def check_p4_compliance() -> int:
    exit_code = 0

    # (a) Count adapters with model.inference capability
    adapters_dir = Path("adapters/external")
    model_inference_adapters = []

    for manifest_path in adapters_dir.glob("*/manifest.toml"):
        try:
            import tomllib
            with manifest_path.open("rb") as f:
                data = tomllib.load(f)

            # Check for model.inference capability
            provides = data.get("provides", [])
            for cap in provides:
                if cap.get("category") == "model_inference":
                    model_inference_adapters.append(manifest_path.parent.name)
                    break
        except Exception:
            continue

    if len(model_inference_adapters) < 2:
        # Check DEBT.md for P4-EXCEPTION
        debt_path = Path("DEBT.md")
        if debt_path.exists():
            with debt_path.open() as f:
                debt_content = f.read()

            # Look for P4-EXCEPTION line (not commented)
            has_exception = False
            for line in debt_content.splitlines():
                stripped = line.strip()
                if stripped.startswith("P4-EXCEPTION:") and not stripped.startswith("#"):
                    has_exception = True
                    break

            if not has_exception:
                print(f"ERROR: Only {len(model_inference_adapters)} model.inference adapter(s) found, but no P4-EXCEPTION in DEBT.md")
                exit_code = 1
            else:
                print(f"OK: {len(model_inference_adapters)} adapter(s) with P4-EXCEPTION in DEBT.md")
        else:
            print(f"ERROR: Only {len(model_inference_adapters)} model.inference adapter(s) found, but DEBT.md does not exist")
            exit_code = 1
    else:
        print(f"OK: {len(model_inference_adapters)} model.inference adapter(s) found")

    # (b) Verify RoutingEngine tests coverage
    test_routing_path = Path("tests/test_routing_engine.py")
    if test_routing_path.exists():
        with test_routing_path.open() as f:
            test_content = f.read()

        required_tests = [
            "failover",
            "single_adapter",
            "all_unhealthy",
            "cpu_only_healthy",
            "manifest_without_routing_priority",
            "get_adapter_returns_instance",
            "get_adapter_none_skip",
        ]

        missing_tests = []
        for test_name in required_tests:
            if test_name not in test_content:
                missing_tests.append(test_name)

        if missing_tests:
            print(f"ERROR: Missing RoutingEngine tests: {', '.join(missing_tests)}")
            exit_code = 1
        else:
            print("OK: All required RoutingEngine tests present")
    else:
        print("WARNING: tests/test_routing_engine.py does not exist")

    # (c) AST scan for unprotected Raise nodes in main.py
    main_path = Path("sovereignai/main.py")
    if main_path.exists():
        with main_path.open() as f:
            main_content = f.read()

        tree = ast.parse(main_content)

        # Find all Raise nodes
        class RaiseVisitor(ast.NodeVisitor):
            def __init__(self):
                self.raises = []
                self.in_test_mode_block = False

            def visit_If(self, node):
                # Check if this is an `if not _test_mode` block
                if isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not):
                    if isinstance(node.test.operand, ast.Name) and node.test.operand.id == "_test_mode":
                        old_in_test_mode = self.in_test_mode_block
                        self.in_test_mode_block = True
                        self.generic_visit(node)
                        self.in_test_mode_block = old_in_test_mode
                        return
                self.generic_visit(node)

            def visit_Raise(self, node):
                if not self.in_test_mode_block:
                    self.raises.append(node)
                self.generic_visit(node)

        visitor = RaiseVisitor()
        visitor.visit(tree)

        # Check if any raise uses AdapterNotFoundError/ServiceNotFoundError/etc.
        forbidden_exceptions = ["AdapterNotFoundError", "ServiceNotFoundError"]
        unprotected_raises = []

        for raise_node in visitor.raises:
            if isinstance(raise_node.exc, ast.Call):
                if isinstance(raise_node.exc.func, ast.Name):
                    if raise_node.exc.func.id in forbidden_exceptions:
                        unprotected_raises.append(raise_node.exc.func.id)

        if unprotected_raises:
            print(f"ERROR: Unprotected raises of {', '.join(set(unprotected_raises))} in main.py")
            exit_code = 1
        else:
            print("OK: No unprotected raises of forbidden exception types in main.py")
    else:
        print("WARNING: sovereignai/main.py does not exist")

    return exit_code


if __name__ == "__main__":
    sys.exit(check_p4_compliance())
