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
    class CanMake(adt.Sum):
        Constructor: "7[55{.red$"  # noqa

    assert CanMake


def test_ignore_classvar(adt):
    class Empty(adt.Product):
        class_var: typing.ClassVar[int] = 1
        str_class_var: "typing.ClassVar[int]" = 2
        empty: typing.ClassVar = 3
        error: "Garbage" = 4  # noqa
        error2: "7[55{.red$" = 5  # noqa
        error3: "Garbage[int]" = 6  # noqa

    assert tuple.__getitem__(Empty(), slice(None)) == (4, 5, 6)
