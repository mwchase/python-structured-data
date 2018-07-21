def test_tuple(match):

    matcher = match.ValueMatcher((1, 2))
    assert not matcher.match((3,))
    assert matcher.matches is None
    structure = (1, match.pat.a)
    assert matcher.match(structure)
    assert not matcher.match(())
    assert matcher.matches is None


def test_enum(enum, match):

    @enum.enum
    class TestClass:
        StrPair: enum.Ctor[str, str]
        Str: enum.Ctor[str]
    matcher = match.ValueMatcher(TestClass.StrPair('a', 'b'))
    assert not matcher.match(TestClass.Str('c'))
    assert matcher.matches is None
    structure = TestClass.StrPair(match.pat.a, match.pat.b)
    assert matcher.match(structure)


def test_as(match):

    matcher = match.ValueMatcher((1, 2))
    assert not matcher.match(match.pat.tup @ (match.pat.a, 3))
    assert matcher.matches is None
    structure = match.pat.tup @ (1, match.pat.a)
    assert matcher.match(structure)
