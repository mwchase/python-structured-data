import pytest


@pytest.fixture(scope="session")
def adt():
    from structured_data import adt

    return adt


@pytest.fixture(scope="session")
def match():
    from structured_data import match

    return match


@pytest.fixture(scope="session")
def _prewritten_methods():
    from structured_data import _prewritten_methods

    return _prewritten_methods


@pytest.fixture(scope="session")
def _adt_constructor():
    from structured_data import _adt_constructor

    return _adt_constructor


@pytest.fixture(scope="session")
def data():
    from structured_data import data

    return data


@pytest.fixture(scope="session")
def adt_options():
    import test_resources.adt_options

    return test_resources.adt_options


@pytest.fixture(
    scope="session",
    params=[
        "AllFalse",
        "EqOnly",
        "MinimalOrder",
        "ReprOnly",
        "ReprAndEq",
        "ReprAndOrder",
    ],
)
def option_class(adt_options, request):
    return getattr(adt_options, request.param)
