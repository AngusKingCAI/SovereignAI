#!/usr/bin/env python3
import ast
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

STDLIB_MODULES = {
    "os", "sys", "json", "pathlib", "threading", "datetime", "typing", "dataclasses",
    "collections", "uuid", "re", "math", "time", "random", "functools", "itertools",
    "contextlib", "asyncio", "concurrent", "unittest", "pytest", "hypothesis",
    "argparse", "queue", "__future__", "abc", "importlib", "sqlite3", "tomllib",
    "secrets", "hashlib", "subprocess", "shutil", "platform", "enum", "contextvars",
    "tempfile", "ctypes", "traceback", "gc", "ast", "io", "logging", "warnings",
    "inspect", "textwrap", "copy", "decimal", "fractions", "string", "types",
    "sysctl", "mimetypes",
}

LOCAL_PACKAGES = {
    "app",
    "app.sovereignai",
    "app.databases",
    "app.services",
    "app.web",
    "app.tui",
    "app.adapters",
    "app.skills",
    "sovereignai",
    "databases",
    "services",
    "web",
    "tui",
    "adapters",
    "skills",
}


def parse_requirements(requirements_path: Path) -> set[str]:
    deps = set()
    if not requirements_path.exists():
        return deps

    with open(requirements_path, encoding="utf-8") as f:
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
    "tree_sitter_python": "tree-sitter-python",
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
    "tree_sitter",
}


def parse_pyproject_dev_deps(pyproject_path: Path) -> set[str]:
    deps = set()
    if not pyproject_path.exists():
        return deps

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    for dep in dev_deps:
        pkg_name = dep.split(">=")[0].split("==")[0].split("<")[0].strip()
        if pkg_name:
            deps.add(pkg_name)

    return deps


def extract_imports(file_path: Path) -> set[str]:
    imports = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                imports.add(node.module.split(".")[0])
    except Exception:
        pass

    return imports


def check_local_package_exists(package: str, repo_root: Path) -> bool:
    if package == "app":
        package_path = repo_root / "app"
    elif package.startswith("app."):
        package_path = repo_root / "app" / package.replace("app.", "")
    else:
        package_path = repo_root / "app" / package
    return package_path.exists() and package_path.is_dir()


def main():
    # Get repo root from git to handle different script locations
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, cwd=Path(__file__).parent,
    )
    repo_root = (
        Path(result.stdout.strip()) if result.returncode == 0
        else Path(__file__).parent.parent.parent.parent.parent
    )
    requirements_txt = repo_root / "app" / "txt" / "requirements.txt"
    pyproject_toml = repo_root / "pyproject.toml"

    requirements_deps = parse_requirements(requirements_txt)
    dev_deps = parse_pyproject_dev_deps(pyproject_toml)

    production_dirs = [
        repo_root / "app" / "sovereignai",
        repo_root / "app" / "databases",
        repo_root / "app" / "services",
        repo_root / "app" / "web",
        repo_root / "app" / "tui",
        repo_root / "app" / "adapters",
    ]

    test_dirs = [repo_root / "app" / "tests"]

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
                    missing_deps.append(
                        f"{file_path}: '{imp}' (transitive of '{parent}') "
                        f"not in app/txt/requirements.txt"
                    )
                continue

            if is_test_file:
                if normalized_imp not in dev_deps and normalized_imp not in requirements_deps:
                    missing_deps.append(
                        f"{file_path}: '{imp}' not in pyproject.toml "
                        f"[project.optional-dependencies] dev or app/txt/requirements.txt"
                    )
            else:
                if normalized_imp not in requirements_deps:
                    missing_deps.append(f"{file_path}: '{imp}' not in app/txt/requirements.txt")

    if missing_deps:
        print("Missing dependencies:", file=sys.stderr)
        for dep in missing_deps:
            print(f"  {dep}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
