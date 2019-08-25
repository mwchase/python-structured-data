def test_no_collide(_pep_570_when):
    @_pep_570_when.pep_570_when
    def decorated(throwaway, kwargs):
        del throwaway
        return kwargs

    assert decorated(None, kwargs=True, throwaway=False) == {
        "kwargs": True,
        "throwaway": False,
    }
