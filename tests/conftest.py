import os


def pytest_configure():
    os.environ['SOVEREIGNAI_TEST_MODE'] = '1'
