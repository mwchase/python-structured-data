import pytest


def test_invalid_sum_options(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            pass

    for repr_on in (False, True):

        with pytest.raises(ValueError, match="^eq must be true if order is true$"):
            cant_make(repr=repr_on, eq=False, order=True)


def test_sum_cant_generate_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            __eq__ = True

    for repr_on in (False, True):

        with pytest.raises(
            ValueError,
            match="^Can't add ordering methods if equality methods are provided.$",
        ):
            cant_make(repr=repr_on, eq=True, order=True)


def test_sum_cant_overwrite_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Sum, **kwargs):
            __le__ = True

    for repr_on in (False, True):

        class CantMake:
            __le__ = True

        with pytest.raises(
            TypeError,
            match=r"^Cannot overwrite attribute __le__ in class CantMake\. Consider using functools.total_ordering$",
        ):
            cant_make(repr=repr_on, eq=True, order=True)


def test_invalid_product_options(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Product, **kwargs):
            value: int

    for repr_on in (False, True):

        with pytest.raises(ValueError, match="^eq must be true if order is true$"):
            cant_make(repr=repr_on, eq=False, order=True)


def test_product_cant_generate_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Product, **kwargs):
            value: int
            __eq__ = True

    for repr_on in (False, True):

        with pytest.raises(
            ValueError,
            match="^Can't add ordering methods if equality methods are provided.$",
        ):
            cant_make(repr=repr_on, eq=True, order=True)


def test_product_cant_overwrite_order(adt):
    def cant_make(**kwargs):
        class CantMake(adt.Product, **kwargs):
            value: int
            __le__ = True

    for repr_on in (False, True):

        class CantMake:
            __le__ = True

        with pytest.raises(
            TypeError,
            match=r"^Cannot overwrite attribute __le__ in class CantMake\. Consider using functools.total_ordering$",
        ):
            cant_make(repr=repr_on, eq=True, order=True)
