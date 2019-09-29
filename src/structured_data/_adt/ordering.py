

def _ordering_options_are_valid(
    *, eq: bool, order: bool  # pylint: disable=invalid-name
):
    if order and not eq:
        raise ValueError("eq must be true if order is true")


def _can_set_ordering(*, can_set: bool):
    if not can_set:
        raise ValueError("Can't add ordering methods if equality methods are provided.")


def _set_ordering(*, setter, cls: type, source: type):
    collision = setter(
        cls, source.__lt__, source.__le__, source.__gt__, source.__ge__  # type: ignore
    )
    if collision:
        raise TypeError(
            "Cannot overwrite attribute {collision} in class "
            "{name}. Consider using functools.total_ordering".format(
                collision=collision, name=cls.__name__
            )
        )
