import pytest


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
    del prop.__doc__
    assert prop.__doc__ is None

    @prop.getter
    def prop2(self):
        """I'm a docstring!"""

    with pytest.raises(AttributeError):
        prop.fdel = None

    with pytest.raises(AttributeError):
        del prop2.__wrapped__
