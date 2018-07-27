from structured_data import adt


@adt.adt
class Basic:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    left_type = (int,)
    right_type = (str,)


@adt.adt
class StringedInternally:

    Left: adt.Ctor["int"]
    Right: adt.Ctor["str"]

    left_type = (int,)
    right_type = (str,)


@adt.adt
class StringedExternally:

    Left: "adt.Ctor[int]"
    Right: "adt.Ctor[str]"

    left_type = (int,)
    right_type = (str,)


@adt.adt
class Tupled:

    Left: adt.Ctor[int, "int"]
    Right: "adt.Ctor[str, str]"

    left_type = (int, int)
    right_type = (str, str)


TEST_CLASSES = [Basic, StringedInternally, StringedExternally, Tupled]
