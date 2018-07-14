import pytest


@pytest.fixture(scope='session')
def enum():
    from structured_data import enum
    return enum


@pytest.fixture(scope='session')
def match():
    from structured_data import match
    return match
