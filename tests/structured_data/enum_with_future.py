from __future__ import annotations

from structured_data import enum


@enum.enum
class Basic:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]

    left_type = (int,)
    right_type = (str,)


@enum.enum
class Tupled:

    Left: enum.Ctor[int, int]
    Right: enum.Ctor[str, str]

    left_type = (int, int)
    right_type = (str, str)


TEST_CLASSES = [Basic, Tupled]
