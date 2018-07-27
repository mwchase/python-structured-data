import pytest


@pytest.fixture(scope="session")
def structured_data():
    import structured_data as _structured_data

    return _structured_data
