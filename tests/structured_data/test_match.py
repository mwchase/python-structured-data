import pytest


def test_decorate_in_order(match):
    def constant(func):
        del func
        return 0

    def double(func):
        return func, func

    @double
    @constant
    def normal():
        """Dummy function"""

    @match.decorate_in_order(constant, double)
    def with_helper():
        """Dummy function"""

    assert normal == with_helper


def test_function(match):
    @match.function
    def function(a, b):
        """Wrapped test function."""

    @function.when(a=3, b=match.pat.b)
    def return_b(b):
        return b

    @function.when(b=2, a=match.pat.a)
    def return_a(a):
        return a

    @function.when(a=match.pat.a, b=match.pat.b)
    def multiply(a, b):
        return a * b

    assert function(3, 2) == 2
    assert function(4, 2) == 4
    assert function(4, 4) == 16


def test_method(adt, match):
    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        @match.function
        def invert(self):
            """Reverse the the object according to some criteria."""

    @TestEither.invert.when(self=TestEither.Left(match.pat.number))
    def negate(number):
        return TestEither.Left(-number)

    @TestEither.invert.when(self=TestEither.Right(match.pat.string))
    def reverse(string):
        return TestEither.Right(string[::-1])

    assert TestEither.Left(10).invert() == TestEither.Left(-10)
    assert TestEither.Right("abc").invert() == TestEither.Right("cba")


def test_method_positional(adt, match):
    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        @match.function
        def dummy_func(self, arg, /):  # noqa: E225
            """A dummy test function for now."""


def test_trivial_match_function(match):
    @match.function
    def trivial(*trivial_args, **trivial_kwargs):
        """Not a very interesting function."""

    @trivial.when()
    def passthrough(*args, **kwargs):
        return args, kwargs

    assert trivial() == ((), {})
    assert trivial(1, a=2) == ((1,), {"a": 2})


def test_match_function_errors(match):

    @match.function
    def takes_kwargs(arg_to_function, **kwargs):
        raise ValueError

    with pytest.raises(ValueError):
        takes_kwargs(None)

    @takes_kwargs.when(arg_to_function=match.pat.kwarg)
    def impl(kwarg, **kwargs):
        return kwarg, kwargs

    assert takes_kwargs(1, a=2) == (1, {"a": 2})

    with pytest.raises(TypeError):
        takes_kwargs(1, kwarg=1)


def test_function_types(match):
    @match.function
    @classmethod
    def class_method(cls):
        """This is a class method."""

    @match.function
    @staticmethod
    def static_method():
        """This is a static method."""

    @match.function
    @property
    def prop(self):
        """This is a property."""
