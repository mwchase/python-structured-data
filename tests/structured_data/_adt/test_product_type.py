import typing

import pytest


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
            assert product_option_class(1, "abc") < product_option_class(1, "abc")
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") < (True,)


def test_product_le(product_option_class):
    if product_option_class.order:
        assert product_option_class(1, "abc") <= product_option_class(1, "abc")
    else:
        with pytest.raises(TypeError):
            assert not (
                product_option_class(1, "abc") <= product_option_class(1, "abc")
            )
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") <= (True,)


def test_product_gt(product_option_class):
    if product_option_class.order:
        assert not (product_option_class(1, "abc") > product_option_class(1, "abc"))
    else:
        with pytest.raises(TypeError):
            assert product_option_class(1, "abc") > product_option_class(1, "abc")
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") > (True,)


def test_product_ge(product_option_class):
    if product_option_class.order:
        assert product_option_class(1, "abc") >= product_option_class(1, "abc")
    else:
        with pytest.raises(TypeError):
            assert not (
                product_option_class(1, "abc") >= product_option_class(1, "abc")
            )
    with pytest.raises(TypeError):
        assert not product_option_class(1, "abc") >= (True,)


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
    assert Product(snd="abc") == Product(1, "abc")


def test_products_with_bad_default(adt):
    with pytest.raises(TypeError):

        class Product(adt.Product):
            fst: int = 1
            snd: str


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


def test_unsetting(adt):
    class Prod(adt.Product):
        fst: int
        snd: str

        __lt__ = False

    class Subclass(Prod, order=True):
        __lt__ = adt.Product.__lt__

    assert Subclass(3, "abc") > Subclass(2, "def")


def test_product_property(adt):
    class TestProduct(adt.Product):
        fst: int
        snd: str

        @property
        def prop(self):
            pass

    test_value = TestProduct(1, "abc")
    assert test_value.prop is None
    with pytest.raises(AttributeError):
        test_value.prop = 1
    with pytest.raises(AttributeError):
        test_value.dne = 1
    with pytest.raises(AttributeError):
        del test_value.prop
    with pytest.raises(AttributeError):
        del test_value.dne
