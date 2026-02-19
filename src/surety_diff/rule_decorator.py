def compare_rule(func=None, name=None):
    class CompareRule:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def __repr__(self):
            return name or self.func.__name__

    if func:
        return CompareRule(func)

    return CompareRule
