import typing

from structured_data import adt


@adt.adt(repr=False, eq=False, order=False)
class AllFalse:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = False
    eq = False
    order = False


@adt.adt(repr=False, eq=True, order=False)
class EqOnly:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = False
    eq = True
    order = False


@adt.adt(repr=False, eq=True, order=True)
class MinimalOrder:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = False
    eq = True
    order = True


@adt.adt(repr=True, eq=False, order=False)
class ReprOnly:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = True
    eq = False
    order = False


@adt.adt(repr=True, eq=True, order=False)
class ReprAndEq:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = True
    eq = True
    order = False


@adt.adt(repr=True, eq=True, order=True)
class ReprAndOrder:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    repr = True
    eq = True
    order = True


@adt.adt
class CustomEq:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    def __eq__(self, other):
        return self is other


@adt.adt
class CustomInitSubclass:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    subclasses: "typing.List[typing.Type[CustomInitSubclass]]" = []
    dummy_variable: "MyList[CustomInitSubclass]"

    def __init_subclass__(cls, **kwargs):
        cls.subclasses.append(cls)
        return super().__init_subclass__(**kwargs)


MyList = typing.List


@adt.adt
class CustomNew:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    instances: "int" = 0

    def __new__(cls, args):
        self = super().__new__(cls, args)
        CUSTOM_NEW_INSTANCES.append(self)
        CustomNew.instances += 1
        return self


CUSTOM_NEW_INSTANCES: typing.List[CustomNew] = []


TEST_CLASSES = [AllFalse, EqOnly, MinimalOrder, ReprOnly, ReprAndEq, ReprAndOrder]
