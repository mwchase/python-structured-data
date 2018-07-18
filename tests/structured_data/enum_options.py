import typing

from structured_data import enum


@enum.enum(repr=False, eq=False, order=False)
class AllFalse:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    repr = False
    eq = False
    order = False


@enum.enum(repr=False, eq=True, order=False)
class EqOnly:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    repr = False
    eq = True
    order = False


@enum.enum(repr=False, eq=True, order=True)
class MinimalOrder:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    repr = False
    eq = True
    order = True


@enum.enum(repr=True, eq=False, order=False)
class ReprOnly:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    repr = True
    eq = False
    order = False


@enum.enum(repr=True, eq=True, order=False)
class ReprAndEq:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    repr = True
    eq = True
    order = False


@enum.enum(repr=True, eq=True, order=True)
class ReprAndOrder:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    repr = True
    eq = True
    order = True


@enum.enum
class CustomEq:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    def __eq__(self, other):
        return self is other


@enum.enum
class CustomInitSubclass:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    subclasses: 'typing.List[typing.Type[CustomInitSubclass]]' = []
    dummy_variable: 'MyList[CustomInitSubclass]'

    def __init_subclass__(cls, **kwargs):
        cls.subclasses.append(cls)
        return super().__init_subclass__(**kwargs)


MyList = typing.List


@enum.enum
class CustomNew:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    instances: 'int' = 0

    def __new__(cls, args):
        self = super().__new__(cls, args)
        CUSTOM_NEW_INSTANCES.append(self)
        CustomNew.instances += 1
        return self


CUSTOM_NEW_INSTANCES: typing.List[CustomNew] = []


TEST_CLASSES = [AllFalse, EqOnly, MinimalOrder, ReprOnly, ReprAndEq, ReprAndOrder]
