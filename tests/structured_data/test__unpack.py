def test_unpack():
    from structured_data import _unpack

    empty_tuple = ()

    # This needs a much better test
    assert _unpack.unpack(empty_tuple) is empty_tuple
