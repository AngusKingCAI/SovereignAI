#!/usr/bin/env python3
"""Fix import paths in app/sovereignai/ to use sovereignai.* instead of app.sovereignai.*"""

import re
from pathlib import Path

def fix_imports_in_file(file_path: Path) -> int:
    """Replace 'from app.sovereignai' with 'from sovereignai' in a file."""
    content = file_path.read_text()
    original = content
    
    # Replace import statements
    content = re.sub(r'from app\.sovereignai\.', 'from sovereignai.', content)
    content = re.sub(r'import app\.sovereignai\.', 'import sovereignai.', content)
    
    if content != original:
        file_path.write_text(content)
        return 1
    return 0

def fix_ui_imports_in_file(file_path: Path) -> int:
    """UI files outside sovereignai package should use sovereignai.* imports (no app. prefix)."""
    content = file_path.read_text()
    original = content
    
    # Replace app.sovereignai.* with sovereignai.* for UI files
    content = re.sub(r'from app\.sovereignai\.', 'from sovereignai.', content)
    content = re.sub(r'import app\.sovereignai\.', 'import sovereignai.', content)
    
    if content != original:
        file_path.write_text(content)
        return 1
    return 0

def main():
    # Fix app/sovereignai/ imports - these should use sovereignai.* (no app. prefix)
    sovereignai_dir = Path('app/sovereignai')
    if not sovereignai_dir.exists():
        print(f"Directory not found: {sovereignai_dir}")
        return 1
    
    fixed_count = 0
    for py_file in sovereignai_dir.rglob('*.py'):
        fixed_count += fix_imports_in_file(py_file)
    
    # Fix test files - these should use sovereignai.* imports to match source
    tests_dir = Path('.agent/executor/tests')
    if tests_dir.exists():
        for py_file in tests_dir.rglob('*.py'):
            fixed_count += fix_imports_in_file(py_file)
    
    # Fix UI files - these should also use sovereignai.* imports (no app. prefix)
    for ui_dir in ['app/web', 'app/tui', 'app/cli', 'app/phone']:
        ui_path = Path(ui_dir)
        if ui_path.exists():
            for py_file in ui_path.rglob('*.py'):
                fixed_count += fix_ui_imports_in_file(py_file)
    
    print(f"Fixed {fixed_count} files")
    return 0

if __name__ == '__main__':
    exit(main())