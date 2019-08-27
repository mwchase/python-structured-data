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


class CustomEq(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    def __eq__(self, other):
        return self is other


class CustomInitSubclass(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    subclasses: "typing.List[typing.Type[CustomInitSubclass]]" = []
    dummy_variable: "MyList[CustomInitSubclass]"

    def __init_subclass__(cls, **kwargs):
        cls.subclasses.append(cls)
        return super().__init_subclass__(**kwargs)


MyList = typing.List


class CustomNew(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    instances: "int" = 0

    def __new__(cls, args):
        self = super().__new__(cls, args)
        CUSTOM_NEW_INSTANCES.append(self)
        CustomNew.instances += 1
        return self


CUSTOM_NEW_INSTANCES: typing.List[CustomNew] = []


SUM_CLASSES = [AllFalseSum, EqOnlySum, MinimalOrderSum, ReprOnlySum, ReprAndEqSum, ReprAndOrderSum]
