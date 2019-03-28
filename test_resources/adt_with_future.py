from __future__ import annotations

from structured_data import adt


@adt.adt
class Basic:

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    left_type = (int,)
    right_type = (str,)


@adt.adt
class Tupled:

    Left: adt.Ctor[int, int]
    Right: adt.Ctor[str, str]

    left_type = (int, int)
    right_type = (str, str)


@adt.adt
class Empty:

    Left: adt.Ctor
    Right: adt.Ctor

    left_type = ()
    right_type = ()


TEST_CLASSES = [Basic, Tupled, Empty]
