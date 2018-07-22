import pytest

from . import adt_options


@pytest.fixture(scope='session')
def adt():
    from structured_data import adt
    return adt


@pytest.fixture(scope='session')
def match():
    from structured_data import match
    return match


@pytest.fixture(scope='session')
def _prewritten_methods():
    from structured_data import _prewritten_methods
    return _prewritten_methods


@pytest.fixture(scope='session')
def _adt_constructor():
    from structured_data import _adt_constructor
    return _adt_constructor


@pytest.fixture(scope='session')
def data():
    from structured_data import data
    return data


@pytest.fixture(scope='session', params=adt_options.TEST_CLASSES)
def option_class(request):
    return request.param
