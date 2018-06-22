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
