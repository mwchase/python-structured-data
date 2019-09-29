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
def adt__prewritten_methods():
    import structured_data._adt.prewritten_methods

    return structured_data._adt.prewritten_methods


@pytest.fixture(scope="session")
def adt__constructor():
    import structured_data._adt.constructor

    return structured_data._adt.constructor


@pytest.fixture(scope="session")
def _stack_iter():
    from structured_data import _stack_iter

    return _stack_iter


@pytest.fixture(scope="session")
def _pep_570_when():
    from structured_data import _pep_570_when

    return _pep_570_when


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
        "NoOptionsSum",
        "AllFalseSum",
        "EqOnlySum",
        "MinimalOrderSum",
        "ReprOnlySum",
        "ReprAndEqSum",
        "ReprAndOrderSum",
    ],
)
def sum_option_class(adt_options, request):
    return getattr(adt_options, request.param)


@pytest.fixture(
    scope="session",
    params=[
        "NoOptionsProduct",
        "AllFalseProduct",
        "EqOnlyProduct",
        "MinimalOrderProduct",
        "ReprOnlyProduct",
        "ReprAndEqProduct",
        "ReprAndOrderProduct",
    ],
)
def product_option_class(adt_options, request):
    return getattr(adt_options, request.param)
