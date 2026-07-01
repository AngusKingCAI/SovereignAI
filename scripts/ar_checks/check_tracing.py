#!/usr/bin/env python3
import ast
import sys
from pathlib import Path


def has_side_effects(node: ast.AST) -> bool:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            name = func.id
            if name in ("open", "write", "read"):
                return True
        elif isinstance(func, ast.Attribute):
            if func.attr in ("publish", "subscribe"):
                return True
    elif isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                if target.value.id == "self":
                    return True
    elif isinstance(node, ast.AugAssign):
        return True
    return False


def has_trace_emit(node: ast.AST) -> bool:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            if func.attr == "emit":
                return True
    return False


def check_function(func_node: ast.FunctionDef, allowlist: set[str], file_path: str) -> tuple[bool, str]:
    if func_node.name == "__init__":
        has_only_field_assign = True
        for stmt in func_node.body:
            if not isinstance(stmt, ast.Assign):
                has_only_field_assign = False
                break
            for target in stmt.targets:
                if not (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self"):
                    has_only_field_assign = False
                    break
        if has_only_field_assign:
            return True, ""
    
    has_side_effect = False
    has_emit = False
    
    for node in ast.walk(func_node):
        if has_side_effects(node):
            has_side_effect = True
        if has_trace_emit(node):
            has_emit = True
    
    allowlist_key = f"{file_path}:{func_node.name}"
    if has_side_effect and not has_emit and allowlist_key not in allowlist:
        return False, f"Function {func_node.name} has side effects but no trace.emit()"
    
    return True, ""


def main():
    root = Path("sovereignai")
    if not root.exists():
        print("sovereignai/ directory not found")
        sys.exit(1)
    
    allowlist_path = Path("scripts/ar_checks/check_tracing_allowlist.txt")
    try:
        allowlist = set(allowlist_path.read_text().strip().splitlines())
    except FileNotFoundError:
        allowlist = set()
    
    violations = []
    
    for py_file in root.rglob("*.py"):
        try:
            content = py_file.read_text()
            tree = ast.parse(content, filename=str(py_file))
        except SyntaxError:
            continue
        
        rel_path = str(py_file.relative_to(root)).replace("\\", "/")
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                ok, msg = check_function(node, allowlist, rel_path)
                if not ok:
                    violations.append(f"{py_file}:{node.lineno}: {msg}")
    
    if violations:
        for v in violations:
            print(v)
        sys.exit(1)
    
    print("discovery clean")
    sys.exit(0)


if __name__ == "__main__":
    main()
