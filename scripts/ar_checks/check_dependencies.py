#!/usr/bin/env python3
import ast
import os
import sys
import re
from pathlib import Path
from typing import Set, Dict, List, Tuple

STDLIB_MODULES = {
    "os", "sys", "json", "pathlib", "threading", "datetime", "typing",
    "dataclasses", "collections", "uuid", "re", "math", "time", "random",
    "functools", "itertools", "contextlib", "asyncio", "concurrent",
}

PRODUCTION_DIRS = ["sovereignai", "databases", "services", "web", "tui", "adapters"]
DEV_TEST_DIRS = ["tests"]


def extract_imports_from_file(filepath: Path) -> Set[str]:
    imports = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    except (SyntaxError, UnicodeDecodeError):
        pass
    return imports


def parse_requirements_txt(filepath: Path) -> Set[str]:
    packages = set()
    if not filepath.exists():
        return packages
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                match = re.match(r"^[a-zA-Z0-9_-]+", line)
                if match:
                    packages.add(match.group(0).lower())
    return packages


def parse_pyproject_toml_dev(filepath: Path) -> Set[str]:
    packages = set()
    if not filepath.exists():
        return packages
    try:
        import tomli
    except ImportError:
        try:
            import tomllib as tomli
        except ImportError:
            print("Error: Neither tomli nor tomllib available. Install tomli.", file=sys.stderr)
            return packages
    
    with open(filepath, "rb") as f:
        data = tomli.load(f)
    
    dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    for dep in dev_deps:
        match = re.match(r"^[a-zA-Z0-9_-]+", dep)
        if match:
            packages.add(match.group(0).lower())
    return packages


def main():
    script_dir = Path(__file__).parent.parent.parent
    repo_root = script_dir
    
    requirements_txt = repo_root / "txt" / "requirements.txt"
    pyproject_toml = repo_root / "pyproject.toml"
    
    runtime_packages = parse_requirements_txt(requirements_txt)
    dev_packages = parse_pyproject_toml_dev(pyproject_toml)
    
    all_imports: Dict[str, Set[str]] = {}
    missing_deps: List[Tuple[str, str, str]] = []
    
    for dir_name in PRODUCTION_DIRS + DEV_TEST_DIRS:
        dir_path = repo_root / dir_name
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob("*.py"):
            imports = extract_imports_from_file(py_file)
            for imp in imports:
                if imp in STDLIB_MODULES:
                    continue
                if imp not in all_imports:
                    all_imports[imp] = set()
                all_imports[imp].add(str(py_file.relative_to(repo_root)))
    
    for imp, files in all_imports.items():
        imp_lower = imp.lower()
        
        is_production = any(any(f.startswith(d + "/") for d in PRODUCTION_DIRS) for f in files)
        is_dev_test = any(any(f.startswith(d + "/") for d in DEV_TEST_DIRS) for f in files)
        
        if is_production and imp_lower not in runtime_packages:
            for f in files:
                if f.startswith(tuple(d + "/" for d in PRODUCTION_DIRS)):
                    missing_deps.append((f, imp, "txt/requirements.txt"))
        
        if is_dev_test and imp_lower not in dev_packages and imp_lower not in runtime_packages:
            for f in files:
                if f.startswith(tuple(d + "/" for d in DEV_TEST_DIRS)):
                    missing_deps.append((f, imp, "pyproject.toml [project.optional-dependencies] dev"))
    
    if missing_deps:
        print("Missing dependencies:", file=sys.stderr)
        for filepath, imp, target in missing_deps:
            print(f"  {filepath}: imports '{imp}' but not in {target}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
