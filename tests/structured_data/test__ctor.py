import typing

import pytest


def test_ctor_usable_as_empty(adt):
    assert adt.Ctor is adt.Ctor[()]


def test_ctor_converts_to_tuple(adt):
    assert adt.Ctor[(list,)] is adt.Ctor[list]


def test_ctor_controls_subclass_creation(adt):
    with pytest.raises(TypeError):

        class CantMake(adt.Ctor):
            pass


def test_ctor_cant_index_twice(adt):
    with pytest.raises(TypeError):
        assert not adt.Ctor[list][list]


def test_ignore_gibberish(adt):
    class Base:
        pass

    Base.__annotations__ = {"Constructor": "7[55{.red$"}

    class CanMake(Base, adt.Sum):
        pass

    assert CanMake


def test_ignore_classvar(adt):
    class Base:
        class_var = 1
        str_class_var = 2
        empty = 3
        error = 4
        error2 = 5
        error3 = 6

    Base.__annotations__ = {
        "class_var": typing.ClassVar[int],
        "str_class_var": "typing.ClassVar[int]",
        "empty": typing.ClassVar,
        "error": "Garbage",
        "error2": "7[55{.red$",
        "error3": "Garbage[int]",
    }

    class Empty(Base, adt.Product):
        pass

    assert tuple.__getitem__(Empty(), slice(None)) == (4, 5, 6)
