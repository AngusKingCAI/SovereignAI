"""Load and save user configuration from ~/.sovereignai/config.json."""
import contextlib
import json
import os
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(os.path.expanduser("~/.sovereignai/config.json"))

def load_config() -> dict[str, Any]:
    """Load user configuration from the config file and return empty dict if not found."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

def save_config(config: dict[str, Any]) -> None:
    """Save user configuration to the config file with restrictive file permissions."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    with contextlib.suppress(OSError):
        os.chmod(CONFIG_PATH, 0o600)

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value by using a dotted key path for nested dictionary access."""
    config = load_config()
    for part in key.split("."):
        if not isinstance(config, dict):
            return default
        config = config.get(part, default)
    return config

def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value by using a dotted key path for nested dictionary access."""
    config = load_config()
    parts = key.split(".")
    d = config
    for part in parts[:-1]:
        d = d.setdefault(part, {})
    d[parts[-1]] = value
    save_config(config)

def get_api_key(provider: str) -> str | None:
    """Retrieve the stored API key for a specific provider from the configuration."""
    return get_config_value(f"api_keys.{provider}")

def set_api_key(provider: str, key: str) -> None:
    """Store an API key for a specific provider in the configuration file."""
    set_config_value(f"api_keys.{provider}", key)

def delete_api_key(provider: str) -> None:
    """Remove the stored API key for a specific provider from the configuration."""
    config = load_config()
    config.get("api_keys", {}).pop(provider, None)
    save_config(config)
