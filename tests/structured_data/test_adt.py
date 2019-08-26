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
    for adt_class in adt_module.TEST_CLASSES:
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


def test_valid_eq(option_class):
    if option_class.eq:
        assert option_class.Left(1) == option_class.Left(1)
        assert option_class.Right("abc") == option_class.Right("abc")
        assert option_class.Left(1) != option_class.Right("abc")
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


def test_cant_hash(adt_options):
    with pytest.raises(TypeError):
        assert not hash(adt_options.CustomEq.Left(1))
    assert adt_options.CustomEq.Left(1) != adt_options.CustomEq.Left(1)


def test_str(option_class):
    assert str(option_class.Left(1)) == repr(option_class.Left(1))


def test_cant_init_superclass(option_class):
    with pytest.raises(TypeError):
        assert not option_class(())


def test_customize_constructors(adt_options):
    assert adt_options.CustomInitSubclass.subclasses == [
        adt_options.CustomInitSubclass.Left,
        adt_options.CustomInitSubclass.Right,
    ]


def test_custom_new(adt_options):
    assert adt_options.CustomNew.Left(1) in adt_options.CUSTOM_NEW_INSTANCES
    assert adt_options.CustomNew.instances == 1


def test_invalid_options(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            pass
    for repr_on in (False, True):

        with pytest.raises(ValueError):
            cant_make(repr=repr_on, eq=False, order=True)


def test_cant_generate_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            __eq__ = True
    for repr_on in (False, True):

        with pytest.raises(ValueError):
            cant_make(repr=repr_on, eq=True, order=True)


def test_cant_overwrite_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            __le__ = True
    for repr_on in (False, True):

        class CantMake:
            __le__ = True

        with pytest.raises(TypeError):
            cant_make(repr=repr_on, eq=True, order=True)


def test_basic_product(adt):
    class Product(adt.Product):
        fst: int
        snd: str

    assert Product(1, "")


def test_products_with_default(adt):
    class Product(adt.Product):
        fst: int
        snd: str = ""

    assert Product(1) == Product(1, "")


def test_products_with_all_default(adt):
    class Product(adt.Product):
        fst: int = 1
        snd: str = ""

    assert Product() == Product(snd="", fst=1)


def test_invalid_product_options(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Product, **kwargs):
            value: int
    for repr_on in (False, True):

        with pytest.raises(ValueError):
            cant_make(repr=repr_on, eq=False, order=True)


def test_subclass(adt):
    class Product(adt.Product):
        fst: int
        snd: str

    class Subclass1(Product):
        pass

    class Subclass2(Product):
        fst: "None"

    assert Product(1, "") != Subclass1(1, "")
    assert Subclass2("").snd == ""
    with pytest.raises(TypeError):
        assert not Subclass2(snd="", fst=1)
