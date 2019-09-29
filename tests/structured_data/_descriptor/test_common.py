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
