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

    def fmap(self: 'Maybe[A]', func: typing.Callable[[A], B]) -> 'Maybe[B]':
        just_matcher = Maybe.Just(match.pat.a)
        value_matcher = match.ValueMatcher(self)
        if value_matcher.match(just_matcher):
            return Maybe.Just(func(value_matcher.matches['a']))
        return typing.cast(Maybe[B], self)

    @classmethod
    def return_(cls: 'typing.Type[Maybe[T]]', t: T) -> 'Maybe[T]':
        return cls.Just(t)

    def apply(self: 'Maybe[typing.Callable[[A], [B]]]', a: 'Maybe[A]') -> 'Maybe[B]':
        just_matcher = Maybe.Just(match.pat.a)
        applied = self.fmap(a.fmap)
        value_matcher = match.ValueMatcher(applied)
        if value_matcher.match(just_matcher):
            return value_matcher.matches['a']
        return typing.cast(Maybe[B], applied)

    def bind(self: 'Maybe[A]', func: 'typing.Callable[[A], Maybe[B]]') -> 'Maybe[B]':
        just_matcher = Maybe.Just(match.pat.a)
        applied = self.fmap(func)
        value_matcher = match.ValueMatcher(applied)
        if value_matcher.match(just_matcher):
            return value_matcher.matches['a']
        return typing.cast(Maybe[B], applied)


@enum.enum
class Either(typing.Generic[E, R]):

    Left: enum.Ctor[E]
    Right: enum.Ctor[R]

    def fmap(self: 'Either[A, B]', func: typing.Callable[[B], C]) -> 'Either[A, C]':
        right_matcher = Either.Right(match.pat.right)
        value_matcher = match.ValueMatcher(self)
        if value_matcher.match(right_matcher):
            return Either.Right(func(value_matcher.matches['right']))
        return typing.cast(Either[A, C], self)

    @classmethod
    def return_(cls: 'typing.Type[Either[A, T]]', t: T) -> 'Either[A, T]':
        return cls.Right(t)

    def apply(self: 'Either[A, typing.Callable[[B], C]]', b: 'Either[A, B]') -> 'Either[A, C]':
        right_matcher = Either.Right(match.pat.right)
        applied = self.fmap(b.fmap)
        value_matcher = match.ValueMatcher(applied)
        if value_matcher.match(right_matcher):
            return value_matcher.matches['right']
        return typing.cast(Either[A, C], applied)

    def bind(self: 'Either[A, B]', func: 'typing.Callable[[B], Either[A, C]]') -> 'Either[A, C]':
        right_matcher = Either.Right(match.pat.right)
        applied = self.fmap(func)
        value_matcher = match.ValueMatcher(applied)
        if value_matcher.match(right_matcher):
            return value_matcher.matches['right']
        return typing.cast(Either[A, C], applied)
