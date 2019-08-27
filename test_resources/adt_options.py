import typing

from structured_data import adt


class AllFalseSum(adt.Sum, repr=False, eq=False, order=False):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = False
    eq = False
    order = False


class EqOnlySum(adt.Sum, repr=False, eq=True, order=False):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = False
    eq = True
    order = False


class MinimalOrderSum(adt.Sum, repr=False, eq=True, order=True):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = False
    eq = True
    order = True


class ReprOnlySum(adt.Sum, repr=True, eq=False, order=False):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = True
    eq = False
    order = False


class ReprAndEqSum(adt.Sum, repr=True, eq=True, order=False):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = True
    eq = True
    order = False


class ReprAndOrderSum(adt.Sum, repr=True, eq=True, order=True):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = True
    eq = True
    order = True


class AllFalseProduct(adt.Product, repr=False, eq=False, order=False):

    fst: int
    snd: str

    repr = False
    eq = False
    order = False


class EqOnlyProduct(adt.Product, repr=False, eq=True, order=False):

    fst: int
    snd: str

    repr = False
    eq = True
    order = False


class MinimalOrderProduct(adt.Product, repr=False, eq=True, order=True):

    fst: int
    snd: str

    repr = False
    eq = True
    order = True


class ReprOnlyProduct(adt.Product, repr=True, eq=False, order=False):

    fst: int
    snd: str

    repr = True
    eq = False
    order = False


class ReprAndEqProduct(adt.Product, repr=True, eq=True, order=False):

    fst: int
    snd: str

    repr = True
    eq = True
    order = False


class ReprAndOrderProduct(adt.Product, repr=True, eq=True, order=True):

    fst: int
    snd: str

    repr = True
    eq = True
    order = True


class CustomEqSum(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    def __eq__(self, other):
        return self is other


class CustomEqProduct(adt.Product):

    fst: int
    snd: str

    def __eq__(self, other):
        return self is other


class CustomInitSubclassSum(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    subclasses: "typing.List[typing.Type[CustomInitSubclassSum]]" = []
    dummy_variable: "MyList[CustomInitSubclassSum]"

    def __init_subclass__(cls, **kwargs):
        cls.subclasses.append(cls)
        return super().__init_subclass__(**kwargs)


MyList = typing.List


class CustomNewSum(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    instances: "int" = 0

    def __new__(cls, args):
        self = super().__new__(cls, args)
        CUSTOM_NEW_INSTANCES.append(self)
        CustomNewSum.instances += 1
        return self


CUSTOM_NEW_INSTANCES: typing.List[CustomNewSum] = []


SUM_CLASSES = [
    AllFalseSum,
    EqOnlySum,
    MinimalOrderSum,
    ReprOnlySum,
    ReprAndEqSum,
    ReprAndOrderSum,
]


PRODUCT_CLASSES = [
    AllFalseProduct,
    EqOnlyProduct,
    MinimalOrderProduct,
    ReprOnlyProduct,
    ReprAndEqProduct,
    ReprAndOrderProduct,
]
