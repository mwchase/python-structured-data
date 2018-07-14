import pytest


def test_generic_subclass_succeeds(enum):

    @enum.enum
    class TestClass(typing.Generic[T]):
        Variant: enum.Ctor[()]

    assert TestClass.Variant()


def test_ctor_usable_as_empty(enum):
    assert enum.Ctor is enum.Ctor[()]


def test_ctor_converts_to_tuple(enum):
    assert enum.Ctor[(list,)] is enum.Ctor[list]


def test_ctor_controls_subclass_creation(enum):
    with pytest.raises(TypeError):
        class CantMake(enum.Ctor):
            pass


def test_ctor_cant_index_twice(enum):
    with pytest.raises(TypeError):
        assert not enum.Ctor[list][list]


def ctor_cant_assign_attribute(enum):
    ctor = enum.Ctor[list]
    with pytest.raises(AttributeError):
        ctor.args = ()
