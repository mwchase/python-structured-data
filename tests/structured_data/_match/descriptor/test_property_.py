import pytest


def test_property_basics(adt, match):
    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        invert = match.function(property())

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

    assert TestEither.Right.invert.__get__(
        TestEither.Left(4), TestEither.Left
    ) == TestEither.Left(-4)

    with pytest.raises(ValueError):
        TestEither.Left(10).invert = 0

    with pytest.raises(ValueError):
        TestEither.Right.invert.__set__(TestEither.Left(0), 0)

    with pytest.raises(ValueError):
        del TestEither.Left(10).invert

    with pytest.raises(ValueError):
        TestEither.Right.invert.__delete__(TestEither.Left(50))


def test_property_advanced(adt, match):
    values = {}
    special_values = []

    @match.Placeholder
    def special(cls):
        return cls.Left(10)

    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        prop = match.function(property())

        @prop.setter
        def prop(self, value):
            values[self] = value

        @prop.deleter
        def prop(self):
            del values[self]

        @prop.set_when(match.pat._, 5)
        def __set_5():
            pass

        @prop.set_when(special, special)
        def __set_double_special():
            special_values.extend([None, None])

        @prop.set_when(match.pat._, special)
        def __set_as_special():
            pass

        @prop.set_when(special, match.pat.value)
        def __set_special(value):
            special_values.append(value)

        @prop.delete_when(special)
        def __delete_special():
            special_values.pop()

    special = TestEither.Left(10)

    TestEither.Right("abc").prop = 1
    del TestEither.Right("abc").prop

    special.prop = 1
    special.prop = 2
    del special.prop
    del special.prop

    special.prop = 5
    with pytest.raises(IndexError):
        del special.prop

    TestEither.Right("abc").prop = special
    with pytest.raises(KeyError):
        del TestEither.Right("abc").prop

    special.prop = special
    del special.prop
    del special.prop

    bad_deco = TestEither.prop.set_when(match.pat.a, match.pat.a)
    with pytest.raises(ValueError):
        assert not bad_deco(None)


def test_property_fallback(match):
    class Test:

        prop = match.function(property())

    test_obj = Test()
    prop = Test.prop
    with pytest.raises(ValueError):
        assert prop != test_obj.prop


def test_property_is_mostly_immutable(match):
    prop = match.function(property(doc="Hi!"))
    del prop.__doc__
    assert prop.__doc__ is None

    @prop.getter
    def prop2(self):
        """I'm a docstring!"""

    with pytest.raises(AttributeError):
        prop.fdel = None

    with pytest.raises(AttributeError):
        del prop2.__wrapped__


def test_proxy(match):

    class Test:
        prop = match.function(property())

    class Test2(Test):
        pass

    @Test2.prop.getter
    def prop_get(self):
        """I'm a docstring!"""

    @Test2.prop.setter
    def prop_set(self, value):
        """I'm a docstring!"""

    @Test2.prop.deleter
    def prop_delete(self):
        """I'm a docstring!"""


def test_proxy_doc(match):

    class Base:
        @match.function
        @property
        def prop(self):
            """Docstring."""

    class Test(Base):
        pass

    assert Test.prop.__doc__ == "Docstring."
