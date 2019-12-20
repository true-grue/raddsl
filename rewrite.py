# raddsl 16112019
# Author: Peter Sovietov


SEQ_TYPES = tuple, list


class Tree:
    def __init__(self, out=None, **attrs):
        self.__dict__.update(attrs)
        self.env = Env()
        self.out = out


class Env(dict):
    def __getattr__(self, name):
        return self[name]


def is_list(x): return type(x) in SEQ_TYPES


def match_seq(tree, pat, x):
    i = 0
    for p in pat:
        if not match(tree, p, x[i]):
            return False
        i += 1
    return True


def match(tree, pat, x):
    if callable(pat):
        x, tree.out = tree.out, x
        b, tree.out = pat(tree), x
        return b
    if not is_list(pat):
        return pat == x
    if is_list(x) and len(x) == len(pat):
        return match_seq(tree, pat, x)
    return False


def apply(tree, pat):
    return pat(tree) if callable(pat) else match(tree, pat, tree.out)


def non(pat):
    def walk(tree):
        return not apply(tree, pat)
    return walk


def alt(*args):
    def walk(tree):
        old = tree.env
        for pat in args:
            if apply(tree, pat):
                return True
            tree.env = old
        return False
    return walk


def seq(*args):
    def walk(tree):
        old = tree.out
        for pat in args:
            if not apply(tree, pat):
                tree.out = old
                return False
        return True
    return walk


def let(**kwargs):
    name, pat = list(kwargs.items())[0]

    def walk(tree):
        if apply(tree, pat):
            if name in tree.env:
                return match(tree, tree.env[name], tree.out)
            tree.env = Env(tree.env)
            tree.env[name] = tree.out
            return True
        return False
    return walk


def rule(*args):
    pat = seq(*args)

    def walk(tree):
        env = tree.env
        tree.env = Env()
        b = pat(tree)
        tree.env = env
        return b
    return walk


def to(f):
    def walk(tree):
        tree.out = f(tree.env)
        return True
    return walk


def where(*args):
    pat = seq(*args)

    def walk(tree):
        old = tree.out
        b = pat(tree)
        tree.out = old
        return b
    return walk


def build(f):
    def walk(tree):
        tree.out = f(tree)
        return True
    return walk


def cons(first, rest):
    def walk(tree):
        if is_list(tree.out) and tree.out:
            b = match(tree, first, tree.out[:len(first)])
            return b and match(tree, rest, tree.out[len(first):])
        return False
    return walk


def rewrite_seq(tree, pat, x):
    old = x
    if type(x) is list:
        x = tuple(x)
    i = 0
    for p in pat:
        if not rewrite_rec(tree, p, x[i]):
            return False
        x = x[:i] + (tree.out,) + x[i + 1:]
        i += 1
    tree.out = list(x) if type(old) is list else x
    return True


def rewrite_rec(tree, pat, x):
    tree.out = x
    if callable(pat):
        return pat(tree)
    if not is_list(pat):
        return pat == x
    if is_list(x) and len(x) == len(pat):
        return rewrite_seq(tree, pat, x)
    return False


def rewrite(pat):
    def walk(tree):
        old = tree.out
        if not rewrite_rec(tree, pat, tree.out):
            tree.out = old
            return False
        return True
    return walk


def many(pat):
    if not callable(pat):
        pat = seq(pat)

    def walk(tree):
        x = tree.out
        old = x
        if type(x) is list:
            x = tuple(x)
        i = 0
        for tree.out in old:
            if is_list(tree.out):
                if not pat(tree):
                    tree.out = old
                    return False
                x = x[:i] + (tree.out,) + x[i + 1:]
            i += 1
        tree.out = list(x) if type(old) is list else x
        return True
    return walk


def repeat(pat):
    def walk(tree):
        while True:
            old = tree.out
            if not apply(tree, pat):
                tree.out = old
                return True
    return walk


def any(t): return True


def env(f): return lambda t: f(t.env)(t)


def opt(*args): return alt(seq(*args), any)


def delay(f): return lambda t: f()(t)


def guard(f): return lambda t: f(t.env)


def topdown(x):
    f = seq(x, many(delay(lambda: f)))
    return f


def bottomup(x):
    f = seq(many(delay(lambda: f)), x)
    return f


def innermost(x):
    f = bottomup(opt(seq(x, delay(lambda: f))))
    return f


def bottomup_except(stop, x):
    f = alt(stop, seq(many(delay(lambda: f)), x))
    return f
