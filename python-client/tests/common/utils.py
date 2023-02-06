import itertools

flatten = itertools.chain.from_iterable


def all_subclasses(cls):
    """
    Return all subclasses of a class, recursively.
    """
    # `type` and other metaclasses don't behave nicely with `__subclasses__`,
    # we have to filter them out
    if cls is type or type in cls.__bases__:
        return []

    level_1 = cls.__subclasses__()
    return set(level_1).union(flatten(map(all_subclasses, level_1)))
