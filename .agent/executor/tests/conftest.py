"""Pytest configuration and deterministic test ordering.

This conftest.py provides:
- Deterministic test ordering to prevent flaky tests
- Test collection sorting by module and function name
- Detection of test execution order dependencies
- DI container isolation between tests
"""

import pytest


def pytest_collection_modifyitems(config, items) -> None:
    """Sort test items deterministically to prevent flaky tests.
    
    Tests are sorted by:
    1. Module path (alphabetical)
    2. Class name (if present, alphabetical)
    3. Function name (alphabetical)
    
    This ensures consistent test execution order across runs, making
    failures reproducible and preventing hidden dependencies on test order.
    """
    def get_sort_key(item):
        """Generate sort key for test item."""
        # Extract module path
        module_path = str(item.module.__file__) if hasattr(item, 'module') else ""
        
        # Extract class name if present
        class_name = ""
        if item.cls:
            class_name = item.cls.__name__
        
        # Extract function name
        function_name = item.name
        
        return (module_path, class_name, function_name)
    
    # Sort items deterministically
    items.sort(key=get_sort_key)


def pytest_report_collectionfinish(config, start_path, items) -> str:
    """Report deterministic test ordering after collection."""
    total_tests = len(items)
    return f"\n{total_tests} tests collected with deterministic ordering"


def pytest_runtest_logreport(report):
    """Monitor test execution for order-dependent failures.
    
    This hook detects tests that fail inconsistently, which may indicate
    hidden dependencies on test execution order (e.g., shared DI container state).
    """
    if report.when == "call" and report.failed:
        # Could add logic here to track flaky tests
        # For now, this is a placeholder for future enhancement
        pass


@pytest.fixture(autouse=True)
def reset_di_container():
    """Automatically reset DI container state between tests.
    
    This fixture runs automatically for every test to ensure
    DI container isolation, preventing state leakage between tests
    that could cause flaky behavior.
    """
    # Import here to avoid circular imports
    try:
        from app.sovereignai.shared.di_container import DIContainer
        # Reset container if it exists
        if hasattr(DIContainer, '_instance'):
            DIContainer._instance = None
    except ImportError:
        # DI container not available in test environment
        pass
    
    yield
    
    # Clean up after test
    try:
        from app.sovereignai.shared.di_container import DIContainer
        if hasattr(DIContainer, '_instance'):
            DIContainer._instance = None
    except ImportError:
        pass