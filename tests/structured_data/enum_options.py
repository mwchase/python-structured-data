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


TEST_CLASSES = [AllFalse, EqOnly, MinimalOrder, ReprOnly, ReprAndEq, ReprAndOrder]
