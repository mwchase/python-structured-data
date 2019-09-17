import inspect


def test_no_collide(_pep_570_when):
    @_pep_570_when.pep_570_when
    def decorated(throwaway, kwargs):
        del throwaway
        return kwargs

    assert decorated(None, kwargs=True, throwaway=False) == {
        "kwargs": True,
        "throwaway": False,
    }
    assert decorated.__name__ == "decorated"

    signature = inspect.signature(decorated)
    assert signature.parameters["throwaway"] == inspect.Parameter(
        "throwaway", inspect.Parameter.POSITIONAL_ONLY
    )
    assert signature.parameters["kwargs"] == inspect.Parameter(
        "kwargs", inspect.Parameter.VAR_KEYWORD
    )
