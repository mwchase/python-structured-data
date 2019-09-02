from __future__ import annotations

from structured_data import adt


class Basic(adt.Sum):

    Left: adt.Ctor[int]
    Right: adt.Ctor[str]

    left_type = (int,)
    right_type = (str,)


class Tupled(adt.Sum):

    Left: adt.Ctor[int, int]
    Right: adt.Ctor[str, str]

    left_type = (int, int)
    right_type = (str, str)


class Empty(adt.Sum):

    Left: adt.Ctor
    Right: adt.Ctor

    left_type = ()
    right_type = ()


class Product(adt.Product):

    fst: int
    snd: str
    blank: None


SUM_CLASSES = [Basic, Tupled, Empty]
