#!/usr/bin/env python3
"""AR15 check: Verify adapter manifests declare health_check() in kwargs per AR15."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def check_manifest(manifest_path: Path) -> list[str]:
    """Check a single manifest.toml for health_check() declaration."""
    errors: list[str] = []

    try:
        content = manifest_path.read_text(encoding='utf-8')
        manifest = tomllib.loads(content)
    except Exception as e:
        errors.append(f'{manifest_path}: Failed to parse TOML: {e}')
        return errors

    # Check if manifest has component section
    component = manifest.get('component', {})
    if not component:
        errors.append(f'{manifest_path}: Missing [component] section')
        return errors

    # Check for health_check in kwargs
    kwargs = component.get('kwargs', {})
    if 'health_check' not in kwargs:
        errors.append(
            f'{manifest_path}: Missing health_check in component.kwargs. '
            'Per AR15, adapters must declare health_check() method.'
        )

    return errors


def main() -> int:
    """Check all adapter manifests for AR15 compliance."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    adapters_dir = repo_root / 'app' / 'adapters'

    if not adapters_dir.exists():
        print(f'Adapters directory not found: {adapters_dir}')
        return 0

    all_errors: list[str] = []

    # Check both external and internal adapters
    for adapter_type in ['external', 'internal']:
        adapter_path = adapters_dir / adapter_type
        if not adapter_path.exists():
            continue

        manifest_files = list(adapter_path.rglob('manifest.toml'))
        for manifest_file in manifest_files:
            errors = check_manifest(manifest_file)
            all_errors.extend(errors)

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1

    print('AR15 check passed: All adapter manifests declare health_check() in kwargs')
    return 0


if __name__ == '__main__':
    sys.exit(main())
