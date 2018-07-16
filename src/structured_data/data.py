import typing

from . import enum
from . import match

T = typing.TypeVar('T')
R = typing.TypeVar('R')
E = typing.TypeVar('E')

A = typing.TypeVar('A')
B = typing.TypeVar('B')
C = typing.TypeVar('C')


@enum.enum
class Maybe(typing.Generic[T]):

    Just: enum.Ctor[T]
    Nothing: enum.Ctor


@enum.enum
class Either(typing.Generic[E, R]):

    Left: enum.Ctor[E]
    Right: enum.Ctor[R]
