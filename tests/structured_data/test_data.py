def test_maybe_just(data):
    assert data.Maybe.Just(1)


def test_maybe_nothing(data):
    assert not data.Maybe.Nothing()


def test_maybe_nothing_not_equal(data):
    assert data.Maybe.Nothing() != ()


def test_in_just(data):
    assert "abc" in data.Maybe.Just("abc")


def test_empty_list(data):
    assert list(data.Maybe.Nothing()) == []


def test_just_list(data):
    assert list(data.Maybe.Just("foo")) == ["foo"]


def test_reversed(data):
    assert list(reversed(data.Maybe.Just("oof"))) == ["oof"]


def test_result(data):
    assert data.Either.Left("failed")
    assert data.Either.Right(5)
