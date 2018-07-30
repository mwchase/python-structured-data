def test_guard(match):
    matchable = match.Matchable(0)
    assert matchable(match.FALSY)
    assert not matchable(match.TRUTHY)


def test_as_guard(match):
    matchable = match.Matchable(0)
    assert matchable(match.FALSY[match.pat.test])
    assert matchable["test"] == 0
    assert not matchable(match.TRUTHY[match.pat.test])
