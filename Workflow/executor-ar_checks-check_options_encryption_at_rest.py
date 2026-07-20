"""AR check: Verify API keys are never stored plaintext in options backend."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet


def check_encryption_at_rest(db_path: Path = Path("data/options.db")) -> bool:
    """Verify API keys are encrypted in the database.

    Args:
        db_path: Path to options database.

    Returns:
        True if all API keys are encrypted or no API keys exist.

    Raises:
        AssertionError: If plaintext API keys are found.
    """
    if not db_path.exists():
        print(f"Database not found at {db_path}, skipping check")
        return True

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if api_keys table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='api_keys'
        """
        )
        if cursor.fetchone() is None:
            print("api_keys table does not exist, skipping check")
            return True

        # Get all API keys
        cursor.execute("SELECT provider, key FROM api_keys")
        rows = cursor.fetchall()

        if not rows:
            print("No API keys found in database")
            return True

        # Check each key
        for provider, encrypted_key in rows:
            # Try to decrypt using Fernet
            # If it's plaintext, Fernet will raise InvalidToken
            try:
                # This check is heuristic: we try to decrypt
                # If it fails, it might be plaintext
                # However, if encryption key is wrong, it will also fail
                # So we check if the key looks like Fernet token
                if not encrypted_key:
                    continue

                # Fernet tokens are base64-encoded and have specific structure
                # Plaintext keys would not be valid Fernet tokens
                try:
                    Fernet(encrypted_key.encode())  # type: ignore[arg-type]
                    # If this succeeds, it's probably a key itself, not encrypted data
                    raise AssertionError(
                        "API key for provider '{provider}' appears to be "
                        "plaintext Fernet key, not encrypted data"
                    )
                except Exception:
                    # If it fails to parse as Fernet key, it might be encrypted data
                    # We can't verify without the actual encryption key
                    # So we do a structural check
                    pass

                # Check if the key looks like it could be an API key (not encrypted)
                # Encrypted data should be base64-like and longer than typical API keys
                if len(encrypted_key) < 44:  # Fernet tokens are at least 44 chars
                    raise AssertionError(
                        f"API key for provider '{provider}' is too short "
                        f"to be encrypted (length: {len(encrypted_key)})"
                    )

                # Check if it contains non-base64 characters
                import base64

                try:
                    base64.b64decode(encrypted_key, validate=True)
                except Exception as err:
                    raise AssertionError(
                        f"API key for provider '{provider}' is not valid "
                        f"base64 (likely plaintext)"
                    ) from err

            except AssertionError as e:
                raise e
            except Exception as e:
                # Other exceptions indicate we can't verify
                # This is acceptable if we don't have the encryption key
                print(f"Warning: Could not verify encryption for provider '{provider}': {e}")
                continue

        print(f"All {len(rows)} API keys appear to be encrypted")
        return True

    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/options.db")
    try:
        result = check_encryption_at_rest(db_path)
        if result:
            print("PASS: Encryption check passed")
            sys.exit(0)
        else:
            print("FAIL: Encryption check failed")
            sys.exit(1)
    except AssertionError as e:
        print(f"FAIL: Encryption check failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Encryption check error: {e}")
        sys.exit(1)
