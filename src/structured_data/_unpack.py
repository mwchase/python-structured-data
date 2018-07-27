def unpack(instance: tuple) -> tuple:
    """Return the inside of any ADT instance.

    This function is not meant for general use.
    """
    return tuple.__getitem__(instance, slice(None))


__all__ = ["unpack"]
