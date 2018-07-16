import typing

from . import enum

T = typing.TypeVar('T')
R = typing.TypeVar('R')
E = typing.TypeVar('E')


@enum.enum
class Maybe(typing.Generic[T]):

    Just: enum.Ctor[T]
    Nothing: enum.Ctor


@enum.enum
class Either(typing.Generic[E, R]):

    Left: enum.Ctor[E]
    Right: enum.Ctor[R]
