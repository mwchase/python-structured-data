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
    def unit(cls: 'typing.Type[Maybe[T]]', t: T) -> 'Maybe[T]':
        return cls.Just(t)

    def join(self: 'Maybe[Maybe[A]]') -> 'Maybe[A]':
        just_matcher = Maybe.Just(match.pat.a)
        value_matcher = match.ValueMatcher(self)
        if value_matcher.match(just_matcher):
            return value_matcher.matches['a']
        return typing.cast(Maybe[A], self)

    def apply(self: 'Maybe[typing.Callable[[A], [B]]]', a: 'Maybe[A]') -> 'Maybe[B]':
        return self.bind(a.fmap)

    def bind(self: 'Maybe[A]', func: 'typing.Callable[[A], Maybe[B]]') -> 'Maybe[B]':
        return self.fmap(func).join()


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
    def unit(cls: 'typing.Type[Either[A, T]]', t: T) -> 'Either[A, T]':
        return cls.Right(t)

    def join(self: 'Either[A, Either[A, B]]') -> 'Either[A, B]':
        right_matcher = Either.Right(match.pat.right)
        value_matcher = match.ValueMatcher(self)
        if value_matcher.match(right_matcher):
            return value_matcher.matches['right']
        return typing.cast(Either[A, B], self)

    def apply(self: 'Either[A, typing.Callable[[B], C]]', b: 'Either[A, B]') -> 'Either[A, C]':
        return self.bind(b.fmap)

    def bind(self: 'Either[A, B]', func: 'typing.Callable[[B], Either[A, C]]') -> 'Either[A, C]':
        return self.fmap(func).join()
