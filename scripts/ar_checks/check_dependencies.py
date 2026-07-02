#!/usr/bin/env python3
import ast
import sys
import tomli
from pathlib import Path


STDLIB_MODULES = {
    "os", "sys", "json", "pathlib", "threading", "datetime", "typing", "dataclasses",
    "collections", "uuid", "re", "math", "time", "random", "functools", "itertools",
    "contextlib", "asyncio", "concurrent", "unittest", "pytest", "hypothesis",
    "argparse", "queue", "__future__", "abc", "importlib", "sqlite3", "tomllib",
    "secrets", "hashlib", "subprocess", "shutil", "platform", "enum", "contextvars",
    "tempfile", "ctypes", "traceback", "gc", "ast", "io", "logging", "warnings",
    "inspect", "textwrap", "copy", "decimal", "fractions", "string", "types",
    "sysctl",
}

LOCAL_PACKAGES = {
    "sovereignai",
    "databases",
    "services",
    "web",
    "tui",
    "adapters",
    "tests",
    "scripts",
    "skills",
}


def parse_requirements(requirements_path: Path) -> set[str]:
    deps = set()
    if not requirements_path.exists():
        return deps
    
    with open(requirements_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pkg_name = line.split(">=")[0].split("==")[0].split("<")[0].strip()
                if pkg_name:
                    deps.add(pkg_name)
    
    return deps


PACKAGE_ALIASES = {
    "nvidia_ml_py3": "nvidia-ml-py",
    "llama_cpp": "llama-cpp-python",
    "httpx": "httpx2",
}

TRANSITIVE_DEPENDENCIES = {
    "starlette": "fastapi",
    "pydantic": "fastapi",
    "anyio": "fastapi",
    "typing_extensions": "fastapi",
    "annotated_doc": "fastapi",
    "typing_inspection": "fastapi",
    "httpcore": "httpx",
    "h11": "httpx",
    "idna": "httpx",
    "truststore": "httpx",
    "diskcache": "llama-cpp-python",
}

OPTIONAL_IMPORTS = {
    "torch",
}


def parse_pyproject_dev_deps(pyproject_path: Path) -> set[str]:
    deps = set()
    if not pyproject_path.exists():
        return deps
    
    with open(pyproject_path, "rb") as f:
        data = tomli.load(f)
    
    dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    for dep in dev_deps:
        pkg_name = dep.split(">=")[0].split("==")[0].split("<")[0].strip()
        if pkg_name:
            deps.add(pkg_name)
    
    return deps


def extract_imports(file_path: Path) -> set[str]:
    imports = set()
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and not node.level:
                    imports.add(node.module.split(".")[0])
    except Exception:
        pass
    
    return imports


def check_local_package_exists(package: str, repo_root: Path) -> bool:
    package_path = repo_root / package
    return package_path.exists() and package_path.is_dir()


def main():
    repo_root = Path(__file__).parent.parent.parent
    requirements_txt = repo_root / "txt" / "requirements.txt"
    pyproject_toml = repo_root / "pyproject.toml"
    
    requirements_deps = parse_requirements(requirements_txt)
    dev_deps = parse_pyproject_dev_deps(pyproject_toml)
    
    production_dirs = [
        repo_root / "sovereignai",
        repo_root / "databases",
        repo_root / "services",
        repo_root / "web",
        repo_root / "tui",
        repo_root / "adapters",
    ]
    
    test_dirs = [repo_root / "tests"]
    
    all_imports = {}
    missing_deps = []
    
    for directory in production_dirs + test_dirs:
        if not directory.exists():
            continue
        
        for py_file in directory.rglob("*.py"):
            imports = extract_imports(py_file)
            all_imports[str(py_file.relative_to(repo_root))] = imports
    
    for file_path, imports in all_imports.items():
        is_test_file = file_path.startswith("tests")
        
        for imp in imports:
            if imp in STDLIB_MODULES:
                continue
            
            if imp in OPTIONAL_IMPORTS:
                continue
            
            if imp in LOCAL_PACKAGES:
                if not check_local_package_exists(imp, repo_root):
                    missing_deps.append(f"{file_path}: local package '{imp}' not found in repo")
                continue
            
            normalized_imp = PACKAGE_ALIASES.get(imp, imp)
            
            if normalized_imp in TRANSITIVE_DEPENDENCIES:
                parent = TRANSITIVE_DEPENDENCIES[normalized_imp]
                if parent not in requirements_deps:
                    missing_deps.append(f"{file_path}: '{imp}' (transitive of '{parent}') not in txt/requirements.txt")
                continue
            
            if is_test_file:
                if normalized_imp not in dev_deps and normalized_imp not in requirements_deps:
                    missing_deps.append(f"{file_path}: '{imp}' not in pyproject.toml [project.optional-dependencies] dev or txt/requirements.txt")
            else:
                if normalized_imp not in requirements_deps:
                    missing_deps.append(f"{file_path}: '{imp}' not in txt/requirements.txt")
    
    if missing_deps:
        print("Missing dependencies:", file=sys.stderr)
        for dep in missing_deps:
            print(f"  {dep}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
