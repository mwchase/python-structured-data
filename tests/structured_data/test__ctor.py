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
    class CanMake:
        Constructor: "7[55{.red$"  # noqa

    assert adt.adt(CanMake)
