import pytest


def test_matching(enum, match):

    @enum.enum
    class TestClass:
        StrPair: enum.Ctor[str, str]
    matcher = match.ValueMatcher(
        ((1, 2), TestClass.StrPair('a', 'b')))
    assert not matcher.match((
        (match.pat._, 4),
        match.pat._))
    assert matcher.matches is None
    structure = (
        match.pat.tup @ (1, match.pat.a),
        TestClass.StrPair(
            match.pat.b, match.pat.c))
    assert matcher.match(structure)
    assert matcher.matches == dict(tup=(1, 2), a=2, b='a', c='b')
    assert matcher.matches[match.pat.a, match.pat.b, match.pat.c, match.pat.tup] == (2, 'a', 'b', (1, 2))
    assert list(matcher.matches) == ['tup', 'a', 'b', 'c']  # Should preserve ordering.
    assert match.names(structure) == ['tup', 'a', 'b', 'c']
    assert matcher.matches[dict(hello=match.pat.a, world=match.pat.b)] == dict(hello=2, world='a')


def test_map_interface(match):
    matcher = match.ValueMatcher((1, 2, 3, 4))
    matcher.match((match.pat.a, match.pat._, match.pat._, match.pat.b))
    assert len(matcher.matches) == 2
    with pytest.raises(KeyError):
        assert not matcher.matches[None]

    matcher.matches[match.pat.c] = 7
    del matcher.matches[match.pat.c]

    with pytest.raises(TypeError):
        matcher.matches[None] = None

    with pytest.raises(KeyError):
        del matcher.matches[None]


def test_duplicated_binding(match):
    structure = (match.pat.a, match.pat.a)
    with pytest.raises(ValueError):
        assert not match.names(structure)


def test_different_length_tuples(match):
    assert not match.ValueMatcher((1,)).match((1, 1))


def test_different_constructors(enum, match):
    @enum.enum
    class TestClass:
        Left: enum.Ctor[int]
        Right: enum.Ctor[str]
    matcher = match.ValueMatcher(TestClass.Left(5))
    assert not matcher.match(TestClass.Right('abc'))
