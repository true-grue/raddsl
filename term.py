# Terms with attributes

class Head(dict):
    def __eq__(self, right):
        return self["tag"] == right

    def __ne__(self, right):
        return not self.__eq__(right)

    def __repr__(self):
        return '"%s"' % self["tag"]


def make_term(tag):
    return lambda *args, **attrs: (Head(tag=tag, **attrs),) + args


def clone_term(term, **kwargs):
    return (Head(term[0], **kwargs),) + term[1:]


def attr(term, name):
    return term[0][name]


def set_attr(term, name, val):
    term[0][name] = val
    return term


def is_term(x):
    return isinstance(x, tuple)
