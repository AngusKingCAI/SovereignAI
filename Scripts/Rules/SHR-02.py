# Scripts/Rules/SHR-02.py
# id: SHR-02, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Encoding compliance rule implementation, agent: all, persona: governance
"""SHR-02: Encoding compliance - ensures UTF-8 encoding and proper line endings."""
import re

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Standardized rule evaluation function."""
    rule_id = rule["id"]
    
    # Check if tool is in target tools (if specified)
    target_tools = params.get("target_tools", [])
    if target_tools and tool_name not in target_tools:
        return {"decision": "allow", "rule_id": rule_id}
    
    # Get standardized message
    message = params.get("message", f"violation of rule {rule_id} requires explicit user confirmation")
    
    # Extract common fields
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")
    
    # Check encoding violations (if specified)
    check_encoding = params.get("check_encoding", False)
    if check_encoding:
        # For edit operations, check the actual file on disk for CRLF
        if tool_name == "edit" and file_path:
            try:
                with open(file_path, 'rb') as f:
                    actual_content = f.read()
                    if b'\r\n' in actual_content:
                        return {
                            "decision": "deny",
                            "reason": f"⛔ BLOCKED by rule {rule_id}: {message}",
                            "rule_id": rule_id
                        }
            except Exception:
                pass
        
        # Detect potential encoding violations
        try:
            content.encode('utf-8').decode('utf-8')
        except UnicodeEncodeError:
            return {
                "decision": "deny",
                "reason": f"⛔ BLOCKED by rule {rule_id}: encoding violation - content contains characters that cannot be encoded as UTF-8",
                "rule_id": rule_id
            }
        except UnicodeDecodeError:
            return {
                "decision": "deny",
                "reason": f"⛔ BLOCKED by rule {rule_id}: encoding violation - content contains invalid UTF-8 sequences",
                "rule_id": rule_id
            }
        
        # Check for non-ASCII characters that might have encoding issues
        try:
            for char in content:
                if ord(char) > 127:
                    char.encode('utf-8')
        except UnicodeEncodeError:
            return {
                "decision": "deny",
                "reason": f"⛔ BLOCKED by rule {rule_id}: encoding violation - content contains problematic non-ASCII characters",
                "rule_id": rule_id
            }
    
    return {"decision": "allow", "rule_id": rule_id}