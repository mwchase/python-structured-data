import importlib
import typing

import pytest

T = typing.TypeVar("T")


@pytest.fixture(scope="session", params=["current", "future"])
def adt_module(request):
    return importlib.import_module(f"test_resources.adt_with_{request.param}")


def test_generic_subclass_succeeds(adt):
    class TestClass(adt.Sum, typing.Generic[T]):
        Variant: adt.Ctor[()]

    assert TestClass.Variant()


def test_adt_class(adt_module):
    for adt_class in adt_module.SUM_CLASSES:
        assert adt_class

        annotations_left = typing.get_type_hints(
            adt_class.Left.__new__, vars(adt_module)
        )
        expected_annotations_left = {"return": adt_class}
        for (index, typ) in enumerate(adt_class.left_type):
            expected_annotations_left[f"_{index}"] = typ
        assert annotations_left == expected_annotations_left

        annotations_right = typing.get_type_hints(
            adt_class.Right.__new__, vars(adt_module)
        )
        expected_annotations_right = {"return": adt_class}
        for (index, typ) in enumerate(adt_class.right_type):
            expected_annotations_right[f"_{index}"] = typ
        assert annotations_right == expected_annotations_right


def test_sum_valid_eq(sum_option_class):
    if sum_option_class.eq:
        assert sum_option_class.Left(1) == sum_option_class.Left(1)
        assert sum_option_class.Right("abc") == sum_option_class.Right("abc")
        assert sum_option_class.Left(1) != sum_option_class.Right("abc")
        # This next one is invalid type-wise.
        assert sum_option_class.Left(1) != sum_option_class.Right(1)
        assert sum_option_class.Left(1) != sum_option_class.Left(2)
        assert hash(sum_option_class.Left(1))
    else:
        instance = sum_option_class.Left(1)
        assert instance
        # The base class should compare by object identity instead.
        assert instance == instance
        assert sum_option_class.Left(1) != sum_option_class.Left(1)


def test_sum_repr(sum_option_class):
    if sum_option_class.repr:
        assert repr(sum_option_class.Left(1)) == f"{sum_option_class.__name__}.Left(1)"
    else:
        assert repr(sum_option_class.Left(1)) == "(1,)"


def test_sum_cant_hash(adt_options):
    with pytest.raises(TypeError):
        assert not hash(adt_options.CustomEqSum.Left(1))
    fst = adt_options.CustomEqSum.Left(1)
    snd = adt_options.CustomEqSum.Left(1)
    assert fst != snd


def test_str(sum_option_class):
    assert str(sum_option_class.Left(1)) == repr(sum_option_class.Left(1))


def test_cant_init_superclass(sum_option_class):
    with pytest.raises(TypeError):
        assert not sum_option_class(())


def test_customize_constructors(adt_options):
    assert adt_options.CustomInitSubclassSum.subclasses == [
        adt_options.CustomInitSubclassSum.Left,
        adt_options.CustomInitSubclassSum.Right,
    ]


def test_custom_new(adt_options):
    assert adt_options.CustomNewSum.Left(1) in adt_options.CUSTOM_NEW_INSTANCES
    assert adt_options.CustomNewSum.instances == 1


def test_subclass_to_sum(adt):
    class Base:
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

    class Sum(Base, adt.Sum):
        pass

    assert Sum.Left(1)
    assert Sum.Right("")


def test_cannot_init_sum(adt):
    with pytest.raises(TypeError):
        assert not adt.Sum()


def test_sum_property(adt):
    class TestSum(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        @property
        def prop(self):
            pass

    test_value = TestSum.Left(1)
    assert test_value.prop is None
    with pytest.raises(AttributeError):
        test_value.prop = 1
    with pytest.raises(AttributeError):
        test_value.dne = 1
    with pytest.raises(AttributeError):
        test_value.Left = 1
    with pytest.raises(AttributeError):
        del test_value.prop
    with pytest.raises(AttributeError):
        del test_value.dne
    with pytest.raises(AttributeError):
        del test_value.Left
