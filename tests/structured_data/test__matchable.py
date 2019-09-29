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
