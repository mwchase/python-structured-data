from __future__ import annotations

from structured_data import enum


@enum.enum
class Basic:

    Left: enum.Ctor[int]
    Right: enum.Ctor[str]


@enum.enum
class StringedInternally:

    Left: enum.Ctor['int']
    Right: enum.Ctor['str']


@enum.enum
class Tupled:

    Left: enum.Ctor[int, 'int']
    Right: enum.Ctor[str, 'str']


TEST_CLASSES = [Basic, StringedInternally, Tupled]
