def test_unpack():
    from structured_data import _unpack

    # This needs a much better test
    assert _unpack.unpack(()) is ()
