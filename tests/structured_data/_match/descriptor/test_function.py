import pytest


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
    @match.placeholder
    def left_number(cls):
        return cls.Left(match.pat.number)

    @match.placeholder
    def right_string(cls):
        return cls.Right(match.pat.string)

    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        @match.method
        def invert(self):
            """Reverse the the object according to some criteria."""

        @invert.when(self=left_number)
        def __negate(number):
            return TestEither.Left(-number)

        @invert.when(self=right_string)
        def __reverse(string):
            return TestEither.Right(string[::-1])

    assert TestEither.Left(10).invert() == TestEither.Left(-10)
    assert TestEither.Right("abc").invert() == TestEither.Right("cba")
    assert TestEither.invert(TestEither.Left(5)) == TestEither.Left(-5)

    assert not hasattr(TestEither.Left.invert, "when")
    assert TestEither.Left.invert(TestEither.Right("abc")) == TestEither.Right("cba")
    assert TestEither.Right.invert.__get__(
        TestEither.Left(7), TestEither.Left
    )() == TestEither.Left(-7)


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
        """Ignore me."""

    with pytest.raises(ValueError):
        takes_kwargs(None)

    @takes_kwargs.when(arg_to_function=match.pat.kwarg)
    def impl(kwarg, **kwargs):
        return kwarg, kwargs

    assert takes_kwargs(1, a=2) == (1, {"a": 2})

    with pytest.raises(TypeError):
        takes_kwargs(1, kwarg=1)

    @match.function
    def not_enough(arg):
        """This has an argument. Failing to provide a binding for it should fail."""

    @not_enough.when()
    def bad_match():
        """This shouldn't match."""

    with pytest.raises(ValueError):
        assert not_enough(None)
