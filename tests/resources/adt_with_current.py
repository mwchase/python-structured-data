from structured_data import adt


class Basic(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    left_type = (int,)
    right_type = (str,)


class StringedInternally(adt.Sum):

    Left: adt.Ctor["int"]
    Right: adt.Ctor["str"]

    left_type = (int,)
    right_type = (str,)


class StringedExternally(adt.Sum):

    Left: "adt.Ctor[int]"
    Right: "adt.Ctor[str]"

    left_type = (int,)
    right_type = (str,)


class Tupled(adt.Sum):

    Left: adt.Ctor[int, "int"]
    Right: "adt.Ctor[str, str]"

    left_type = (int, int)
    right_type = (str, str)


class Empty(adt.Sum):

    Left: adt.Ctor
    Right: "adt.Ctor"

    left_type = ()
    right_type = ()


SUM_CLASSES = [Basic, StringedInternally, StringedExternally, Tupled, Empty]
