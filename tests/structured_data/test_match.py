import pytest


def test_matching(adt, match):
    class TestClass(adt.Sum):
        StrPair: adt.Ctor[str, str]

    matchable = match.Matchable(((1, 2), TestClass.StrPair("a", "b")))
    assert not matchable(((match.pat._, 4), match.pat._))
    assert matchable.matches is None
    with pytest.raises(ValueError):
        assert not matchable[None]
    structure = match.Bind(
        (match.pat.tup[1, match.pat.a], TestClass.StrPair(match.pat.b, match.pat.c)),
        bound=5,
    )
    assert matchable(structure)
    assert matchable.matches == dict(tup=(1, 2), a=2, b="a", c="b", bound=5)
    assert matchable[match.pat.a, match.pat.b, match.pat.c, match.pat.tup] == (
        2,
        "a",
        "b",
        (1, 2),
    )
    assert list(matchable.matches) == [
        "tup",
        "a",
        "b",
        "c",
        "bound",
    ]  # Should preserve ordering.
    assert match.names(structure) == ["tup", "a", "b", "c", "bound"]
    assert matchable[dict(hello=match.pat.a, world=match.pat.b)] == dict(
        hello=2, world="a"
    )


def test_map_interface(match):
    matchable = match.Matchable((1, 2, 3, 4))
    matchable((match.pat.a, match.pat._, match.pat._, match.pat.b))
    assert len(matchable.matches) == 2
    with pytest.raises(KeyError):
        assert not matchable[None]

    matchable.matches[match.pat.c] = 7
    del matchable.matches[match.pat.c]

    with pytest.raises(TypeError):
        matchable.matches[None] = None

    with pytest.raises(KeyError):
        del matchable.matches[None]


def test_different_length_tuples(match):
    assert not match.Matchable((1,))((1, 1))


def test_different_constructors(adt, match):
    class TestClass(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

    matchable = match.Matchable(TestClass.Left(5))
    assert not matchable(TestClass.Right("abc"))


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

    assert not base_matchable((1,))
    assert not subclass_matchable((1,))

    assert not tuple_matchable(Base(1))
    assert not tuple_matchable(Subclass(1))


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
