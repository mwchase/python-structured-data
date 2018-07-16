import pytest


@pytest.fixture(scope='session')
def enum():
    from structured_data import enum
    return enum


@pytest.fixture(scope='session')
def match():
    from structured_data import match
    return match


@pytest.fixture(scope='session')
def _prewritten_methods():
    from structured_data import _prewritten_methods
    return _prewritten_methods


@pytest.fixture(scope='session')
def _enum_constructor():
    from structured_data import _enum_constructor
    return _enum_constructor


@pytest.fixture(scope='session')
def data():
    from structured_data import data
    return data
