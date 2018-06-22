import typing

import pytest

T = typing.TypeVar('T')


def test_main():
    pass


def test_generic_subclass_succeeds(structured_data):

    @structured_data.enum
    class TestClass(typing.Generic[T]):
        Variant: structured_data.Ctor[()]

    assert TestClass.Variant()


def test_ctor_usable_as_empty(structured_data):
    assert structured_data.Ctor is structured_data.Ctor[()]


def test_ctor_converts_to_tuple(structured_data):
    assert structured_data.Ctor[(list,)] is structured_data.Ctor[list]


def test_ctor_controls_subclass_creation(structured_data):
    with pytest.raises(TypeError):
        class CantMake(structured_data.Ctor, object):
            pass


def test_ctor_cant_index_twice(structured_data):
    with pytest.raises(TypeError):
        assert not structured_data.Ctor[list][list]


def test_matching(structured_data):

    @structured_data.enum
    class TestClass:
        StrPair: structured_data.Ctor[str, str]
    matcher = structured_data.ValueMatcher(
        ((1, 2), TestClass.StrPair('a', 'b')))
    assert not matcher.match((
        (structured_data.Pattern('_'), 4),
        structured_data.Pattern('_')))
    assert matcher.matches is None
    assert matcher.match((
        structured_data.Pattern('tup') @ (1, structured_data.Pattern('a')),
        TestClass.StrPair(
            structured_data.Pattern('b'), structured_data.Pattern('c'))))
    assert matcher.matches == dict(tup=(1, 2), a=2, b='a', c='b')
