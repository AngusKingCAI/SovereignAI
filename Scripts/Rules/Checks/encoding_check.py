# Scripts/Rules/Checks/encoding_check.py
# Frontmatter: id: encoding_check, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Check for proper UTF-8 encoding in governance files, agent: all, persona: governance
"""Custom check function for UTF-8 encoding validation."""
import sys

def encoding_check(tool_call: dict, params: dict) -> dict:
    """Check for encoding violations in file content."""
    tool_name = tool_call.get("tool", "")
    tool_input = tool_call.get("input", {})
    
    # Check file content for encoding issues
    content = tool_input.get("content", "")
    file_path = tool_input.get("file_path", "")
    
    # For edit operations, check the actual file on disk for CRLF
    if tool_name == "edit" and file_path:
        try:
            with open(file_path, 'rb') as f:
                actual_content = f.read()
                # Check for CRLF in the actual file
                if b'\r\n' in actual_content:
                    return {
                        "deny": True,
                        "reason": "BLOCKED by rule SHR-02: encoding violation - file contains Windows line endings (CRLF), use Unix line endings (LF) only"
                    }
        except Exception:
            pass
    
    # Detect potential encoding violations
    # Check for mixed encodings or problematic characters
    try:
        # Try to encode and decode as UTF-8 to detect issues
        content.encode('utf-8').decode('utf-8')
    except UnicodeEncodeError:
        return {
            "deny": True,
            "reason": "BLOCKED by rule SHR-02: encoding violation - content contains characters that cannot be encoded as UTF-8"
        }
    except UnicodeDecodeError:
        return {
            "deny": True,
            "reason": "BLOCKED by rule SHR-02: encoding violation - content contains invalid UTF-8 sequences"
        }
    
    # Check for non-ASCII characters that might have encoding issues
    try:
        for char in content:
            if ord(char) > 127:
                # Non-ASCII character - verify it can be properly encoded
                char.encode('utf-8')
    except UnicodeEncodeError:
        return {
            "deny": True,
            "reason": "BLOCKED by rule SHR-02: encoding violation - content contains problematic non-ASCII characters"
        }
    
    return {"deny": False}