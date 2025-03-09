def pytest_configure(config):
    """
    Register a custom marker for database tests.
    """
    config.addinivalue_line(
        "markers", "dbtest: mark test as requiring database access"
    )
