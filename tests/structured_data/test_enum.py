import importlib
import typing

import pytest

from . import enum_options

T = typing.TypeVar('T')


@pytest.fixture(scope='session', params=['current', 'future'])
def enum_module(request):
    return importlib.import_module(
        f'.enum_with_{request.param}', __name__.rpartition('.')[0])


def test_generic_subclass_succeeds(enum):

    @enum.enum
    class TestClass(typing.Generic[T]):
        Variant: enum.Ctor[()]

    assert TestClass.Variant()


def test_enum_class(enum_module):
    for enum_class in enum_module.TEST_CLASSES:
        assert enum_class

        annotations_left = typing.get_type_hints(
            enum_class.Left.__new__, vars(enum_module))
        expected_annotations_left = {'return': enum_class}
        for (index, typ) in enumerate(enum_class.left_type):
            expected_annotations_left[f'_{index}'] = typ
        assert annotations_left == expected_annotations_left

        annotations_right = typing.get_type_hints(
            enum_class.Right.__new__, vars(enum_module))
        expected_annotations_right = {'return': enum_class}
        for (index, typ) in enumerate(enum_class.right_type):
            expected_annotations_right[f'_{index}'] = typ
        assert annotations_right == expected_annotations_right


def test_valid_eq(option_class):
    if option_class.eq:
        assert option_class.Left(1) == option_class.Left(1)
        assert option_class.Right('abc') == option_class.Right('abc')
        assert option_class.Left(1) != option_class.Right('abc')
        # This next one is invalid type-wise.
        assert option_class.Left(1) != option_class.Right(1)
        assert option_class.Left(1) != option_class.Left(2)
        assert hash(option_class.Left(1))
    else:
        instance = option_class.Left(1)
        assert instance
        # The base class should compare by object identity instead.
        assert instance == instance
        assert option_class.Left(1) != option_class.Left(1)


def test_cant_hash():
    with pytest.raises(TypeError):
        assert not hash(enum_options.CustomEq.Left(1))
    assert (
        enum_options.CustomEq.Left(1) != enum_options.CustomEq.Left(1))


def test_str(option_class):
    assert str(option_class.Left(1)) == repr(option_class.Left(1))


def test_cant_init_superclass(option_class):
    with pytest.raises(TypeError):
        assert not option_class(())


def test_customize_constructors():
    assert enum_options.CustomInitSubclass.subclasses == [
        enum_options.CustomInitSubclass.Left,
        enum_options.CustomInitSubclass.Right]


def test_custom_new():
    assert enum_options.CustomNew.Left(1) in enum_options.CUSTOM_NEW_INSTANCES
    assert enum_options.CustomNew.instances == 1


def test_invalid_options(enum):
    for repr_on in (False, True):
        class CantMake:
            pass
        with pytest.raises(ValueError):
            enum.enum(repr=repr_on, eq=False, order=True)(CantMake)


def test_cant_generate_order(enum):
    for repr_on in (False, True):
        class CantMake:
            __eq__ = True
        with pytest.raises(ValueError):
            enum.enum(repr=repr_on, eq=True, order=True)(CantMake)


def test_cant_overwrite_order(enum):
    for repr_on in (False, True):
        class CantMake:
            __le__ = True
        with pytest.raises(TypeError):
            enum.enum(repr=repr_on, eq=True, order=True)(CantMake)
