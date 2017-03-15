class FrozenDict(dict):
    __delitem__ = __setitem__ = NotImplemented
    clear = pop = popitem = setdefault = update = NotImplemented
