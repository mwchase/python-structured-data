import pytest


def test_different_length_tuples(match):
    assert not match.Matchable((1,))((1, 1))


def test_different_constructors(adt, match):
    class TestClass(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

    matchable = match.Matchable(TestClass.Left(5))
    assert matchable(TestClass.Left(match.pat._))
    assert not matchable(TestClass.Right("abc"))
    assert matchable.matches is None
    with pytest.raises(ValueError):
        assert not matchable[None]


def test_products(adt, match):
    class Base(adt.Product):
        field: int

    class Subclass(Base):
        pass

    base_matchable = match.Matchable(Base(1))
    subclass_matchable = match.Matchable(Subclass(1))
    tuple_matchable = match.Matchable((1,))

    assert base_matchable(Base(1))
    assert subclass_matchable(Subclass(1))

    assert not base_matchable(Subclass(1))
    assert not subclass_matchable(Base(1))
    assert base_matchable.matches is None
    assert subclass_matchable.matches is None
    with pytest.raises(ValueError):
        assert not base_matchable[None]
    with pytest.raises(ValueError):
        assert not subclass_matchable[None]

    assert not base_matchable((1,))
    assert not subclass_matchable((1,))
    assert base_matchable.matches is None
    assert subclass_matchable.matches is None
    with pytest.raises(ValueError):
        assert not base_matchable[None]
    with pytest.raises(ValueError):
        assert not subclass_matchable[None]

    assert not tuple_matchable(Base(1))
    assert tuple_matchable.matches is None
    with pytest.raises(ValueError):
        assert not tuple_matchable[None]
    assert not tuple_matchable(Subclass(1))
    assert tuple_matchable.matches is None
    with pytest.raises(ValueError):
        assert not tuple_matchable[None]


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

        @match.function(positional_until=1)
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
    def double_dip(arg):
        """Nothing interesting."""

    wrapper = match.function(positional_until=1)
    wrapper(double_dip)
    with pytest.raises(ValueError):
        wrapper(double_dip)

    def wrong_shape(*args):
        """Still nothing interesting."""

    with pytest.raises(ValueError):
        wrapper(wrong_shape)

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


def test_property_basics(adt, match):
    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        invert = match.Property()

        @invert.getter
        def invert(self):
            raise ValueError

    with pytest.raises(ValueError):
        TestEither.Left(10).invert

    @TestEither.invert.get_when(TestEither.Left(match.pat.number))
    def negate(number):
        return TestEither.Left(-number)

    @TestEither.invert.get_when(TestEither.Right(match.pat.string))
    def reverse(string):
        return TestEither.Right(string[::-1])

    assert TestEither.Left(10).invert == TestEither.Left(-10)
    assert TestEither.Right("abc").invert == TestEither.Right("cba")

    with pytest.raises(ValueError):
        TestEither.Left(10).invert = 0

    with pytest.raises(ValueError):
        del TestEither.Left(10).invert


def test_property_advanced(adt, match):
    values = {}
    special_values = []

    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        prop = match.Property()

        @prop.setter
        def prop(self, value):
            values[self] = value

        @prop.deleter
        def prop(self):
            del values[self]

    special = TestEither.Left(10)

    @TestEither.prop.set_when(special, match.pat.value)
    def set_special(value):
        special_values.append(value)

    @TestEither.prop.delete_when(special)
    def delete_special():
        special_values.pop()

    TestEither.Right("abc").prop = 1
    del TestEither.Right("abc").prop

    special.prop = 1
    special.prop = 2
    del special.prop
    del special.prop


def test_property_fallback(match):
    class Test:

        prop = match.Property()

    test_obj = Test()
    prop = Test.prop
    with pytest.raises(ValueError):
        assert prop != test_obj.prop


def test_property_is_mostly_immutable(match):
    prop = match.Property(doc="Hi!")
    assert prop.__doc__ == "Hi!"
    prop.__doc__ = "Bye!"
    assert prop.__doc__ == "Bye!"
    del prop.__doc__
    assert prop.__doc__ is None

    @prop.getter
    def prop2(self):
        """I'm a docstring!"""

    assert prop2.__doc__ == "I'm a docstring!"

    with pytest.raises(AttributeError):
        prop.fdel = None

    with pytest.raises(AttributeError):
        del prop2.__wrapped__
