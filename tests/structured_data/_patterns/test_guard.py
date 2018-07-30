def test_guard(match):
    matchable = match.Matchable(0)
    assert matchable(match.FALSY)
    assert not matchable(match.TRUTHY)


def test_as_guard(match):
    matchable = match.Matchable(0)
    assert matchable(match.FALSY[match.pat.test])
    assert matchable["test"] == 0
    assert not matchable(match.TRUTHY[match.pat.test])


def test_placeholder(match):
    assert match.TRUTHY[match.pat._] is match.TRUTHY


def test_fill_in(match):
    assert match.Guard(int, match.pat.test)
