import mimetypes
from pathlib import Path

BINARY_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".bin",
    ".class",
    ".jar",
    ".war",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
    ".o",
    ".a",
    ".lib",
    ".obj",
}

HIDDEN_DIRS = {
    ".git",
    ".venv",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
}


def execute(args: dict[str, str]) -> str:
    pattern = args.get("pattern")
    project_root = args.get("project_root", str(Path.cwd()))
    max_depth_str = args.get("max_depth", "10")
    max_depth = int(max_depth_str) if max_depth_str else 10

    if not pattern:
        return "Error: pattern argument required"

    root = Path(project_root)
    if not root.exists():
        return f"Error: project_root not found: {project_root}"

    results = []
    _search_recursive(root, pattern, 0, max_depth, root, results)

    if not results:
        return f"No files found matching pattern: {pattern}"

    return "\n".join(results)


def _search_recursive(
    current: Path,
    pattern: str,
    current_depth: int,
    max_depth: int,
    project_root: Path,
    results: list[str],
) -> None:
    if current_depth > max_depth:
        return

    try:
        for item in current.iterdir():
            if item.name in HIDDEN_DIRS:
                continue

            if item.is_symlink():
                continue

            if item.is_dir():
                _search_recursive(
                    item, pattern, current_depth + 1, max_depth, project_root, results
                )
            elif item.is_file():
                if item.suffix.lower() in BINARY_EXTENSIONS:
                    continue

                mime_type, _ = mimetypes.guess_type(str(item))
                if mime_type and mime_type.startswith("image/"):
                    continue

                if item.match(pattern):
                    results.append(str(item))

    except PermissionError:
        pass
