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


def test_product_valid_eq(product_option_class):
    if product_option_class.eq:
        assert product_option_class(1, "abc") == product_option_class(1, "abc")
        # This next one is invalid type-wise.
        assert hash(product_option_class(1, "abc"))
    else:
        instance = product_option_class(1, "abc")
        assert instance
        # The base class should compare by object identity instead.
        assert instance == instance
        assert product_option_class(1, "abc") != product_option_class(1, "abc")


def test_product_repr(product_option_class):
    if product_option_class.repr:
        assert (
            repr(product_option_class(1, "abc"))
            == f"{product_option_class.__name__}(1, 'abc')"
        )
    else:
        assert repr(product_option_class(1, "abc")) == "(1, 'abc')"


def test_sum_cant_hash(adt_options):
    with pytest.raises(TypeError):
        assert not hash(adt_options.CustomEqSum.Left(1))
    fst = adt_options.CustomEqSum.Left(1)
    snd = adt_options.CustomEqSum.Left(1)
    assert fst != snd


def test_product_cant_hash(adt_options):
    with pytest.raises(TypeError):
        assert not hash(adt_options.CustomEqProduct(1, "abc"))
    fst = adt_options.CustomEqProduct(1, "abc")
    snd = adt_options.CustomEqProduct(1, "abc")
    assert fst != snd


def test_product_base_hash(adt_options):
    assert isinstance(hash(adt_options.ReprOnlyProduct(1, "abc")), int)


def test_product_lt(product_option_class):
    if product_option_class.order:
        assert not (product_option_class(1, "abc") < product_option_class(1, "abc"))
    else:
        with pytest.raises(TypeError):
            assert (product_option_class(1, "abc") < product_option_class(1, "abc"))
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") < (True,)


def test_product_le(product_option_class):
    if product_option_class.order:
        assert (product_option_class(1, "abc") <= product_option_class(1, "abc"))
    else:
        with pytest.raises(TypeError):
            assert not (product_option_class(1, "abc") <= product_option_class(1, "abc"))
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") <= (True,)


def test_product_gt(product_option_class):
    if product_option_class.order:
        assert not (product_option_class(1, "abc") > product_option_class(1, "abc"))
    else:
        with pytest.raises(TypeError):
            assert (product_option_class(1, "abc") > product_option_class(1, "abc"))
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") > (True,)


def test_product_ge(product_option_class):
    if product_option_class.order:
        assert (product_option_class(1, "abc") >= product_option_class(1, "abc"))
    else:
        with pytest.raises(TypeError):
            assert not (product_option_class(1, "abc") >= product_option_class(1, "abc"))
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") >= (True,)


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


def test_invalid_sum_options(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            pass

    for repr_on in (False, True):

        with pytest.raises(ValueError):
            cant_make(repr=repr_on, eq=False, order=True)


def test_sum_cant_generate_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            __eq__ = True

    for repr_on in (False, True):

        with pytest.raises(ValueError):
            cant_make(repr=repr_on, eq=True, order=True)


def test_sum_cant_overwrite_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            __le__ = True

    for repr_on in (False, True):

        class CantMake:
            __le__ = True

        with pytest.raises(TypeError):
            cant_make(repr=repr_on, eq=True, order=True)


def test_invalid_product_options(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Product, **kwargs):
            value: int

    for repr_on in (False, True):

        with pytest.raises(ValueError):
            cant_make(repr=repr_on, eq=False, order=True)


def test_product_cant_generate_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Product, **kwargs):
            value: int
            __eq__ = True

    for repr_on in (False, True):

        with pytest.raises(ValueError):
            cant_make(repr=repr_on, eq=True, order=True)


def test_product_cant_overwrite_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Product, **kwargs):
            value: int
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


def test_products_with_bad_default(adt):
    with pytest.raises(TypeError):

        class Product(adt.Product):
            fst: int = 1
            snd: str


def test_subclass_to_sum(adt):
    class Base:
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

    class Sum(Base, adt.Sum):
        pass

    assert Sum.Left(1)
    assert Sum.Right("")


def test_subclass_product_unchanged(adt):
    class Product(adt.Product):
        fst: int
        snd: str

    class Subclass(Product):
        pass

    assert Product(1, "") != Subclass(1, "")


def test_subclass_product_redacted(adt):
    class Product(adt.Product):
        fst: int
        snd: str

    class Subclass(Product):
        fst: "None"

    assert "snd" in dir(Subclass(""))
    assert "fst" not in dir(Subclass(""))

    assert tuple.__getitem__(Subclass(""), slice(None)) == ("",)
    assert Subclass("").snd == ""
    with pytest.raises(TypeError):
        assert not Subclass(snd="", fst=1)

    with pytest.raises(AttributeError):
        assert not Subclass("").fst


def test_subclass_product_ordered(adt):
    class Product(adt.Product):
        fst: int
        snd: str

    class Subclass(Product, order=True):
        pass


def test_cannot_init_sum(adt):
    with pytest.raises(TypeError):
        assert not adt.Sum()


def test_cannot_init_product(adt):
    with pytest.raises(TypeError):
        assert not adt.Product()


def test_custom_product_new(adt):
    class Product(adt.Product):
        name: str
        lst: typing.List[str]

        def __new__(cls, name, lst=None):
            if lst is None:
                lst = []
            return super().__new__(cls, name, lst)

    class Subclass(Product):
        lst: None

    assert Product("test") == Product("test", [])
    assert tuple.__getitem__(Subclass("test"), slice(None)) == ("test",)
