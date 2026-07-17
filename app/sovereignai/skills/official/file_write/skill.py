from pathlib import Path


def execute(args: dict[str, str]) -> str:
    path = args.get("path")
    content = args.get("content")
    if not path:
        return "Error: path argument required"
    if content is None:
        return "Error: content argument required"

    file_path = Path(path)
    try:
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error: {e}"
