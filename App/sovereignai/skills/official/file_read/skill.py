from pathlib import Path


def execute(args: dict[str, str]) -> str:
    path = args.get("path")
    if not path:
        return "Error: path argument required"

    file_path = Path(path)
    if not file_path.exists():
        return f"Error: file not found: {path}"

    try:
        content = file_path.read_text(encoding="utf-8")
        return content
    except Exception as e:
        return f"Error: {e}"
