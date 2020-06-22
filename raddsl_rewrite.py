# Author: Peter Sovietov


class Env(dict):
    def __getattr__(self, name):
        return self[name]


class State:
    def __init__(self, out, **attrs):
        self.out = out
        self.env = Env()
        self.__dict__.update(attrs)


def is_atom(term):
    return not isinstance(term, (tuple, list))


def update(term, n, elem):
    elem = (elem,) if isinstance(term, tuple) else [elem]
    return term[:n] + elem + term[n + 1:]


def match(s, out, pat):
    if callable(pat):
        out, s.out = s.out, out
        res, s.out = pat(s), out
        return res
    return match_term(s, out, pat)


def match_term(s, out, pat):
    if is_atom(pat):
        return pat == out
    if is_atom(out) or len(out) != len(pat):
        return False
    for x, y in zip(out, pat):
        if not match(s, x, y):
            return False
    return True


def apply(s, pat):
    return pat(s) if callable(pat) else match_term(s, s.out, pat)


def non(pat): return lambda s: not apply(s, pat)


def alt(*args):
    def walk(s):
        env = s.env
        for pat in args:
            if apply(s, pat):
                return True
            s.env = env
        return False
    return walk


def seq(*args):
    def walk(s):
        out = s.out
        for pat in args:
            if not apply(s, pat):
                s.out = out
                return False
        return True
    return walk


def let(**kwargs):
    name, pat = list(kwargs.items())[0]

    def walk(s):
        if apply(s, pat):
            if name in s.env:
                return match(s, s.out, s.env[name])
            s.env = Env(s.env)
            s.env[name] = s.out
            return True
        return False
    return walk


def rule(*args):
    f = seq(*args)

    def walk(s):
        env = s.env
        s.env = Env()
        res = f(s)
        s.env = env
        return res
    return walk


def to(f):
    def walk(s):
        s.out = f(s.env)
        return True
    return walk


def where(*args):
    f = seq(*args)

    def walk(s):
        old = s.out
        res = f(s)
        s.out = old
        return res
    return walk


def build(f):
    def walk(s):
        s.out = f(s)
        return True
    return walk


def cons(before, after):
    def walk(s):
        if isinstance(s.out, list) and s.out:
            res = match(s, s.out[:len(before)], before)
            return res and match(s, s.out[len(before):], after)
        return False
    return walk


def rewrite_rec(s, out, pat):
    s.out = out
    if callable(pat):
        return pat(s)
    if is_atom(pat):
        return pat == out
    if is_atom(out) or len(out) != len(pat):
        return False
    for i, p in enumerate(pat):
        if not rewrite_rec(s, out[i], p):
            return False
        out = update(out, i, s.out)
    s.out = out
    return True


def rewrite(pat):
    def walk(s):
        out = s.out
        if not rewrite_rec(s, out, pat):
            s.out = out
            return False
        return True
    return walk


def every(pat):
    def walk(s):
        out = s.out
        res = out
        for i, term in enumerate(out):
            if not is_atom(term):
                s.out = term
                if not apply(s, pat):
                    s.out = out
                    return False
                res = update(res, i, s.out)
        s.out = res
        return True
    return walk


def repeat(pat):
    def walk(s):
        while True:
            out = s.out
            if not apply(s, pat):
                s.out = out
                return True
    return walk


def any(s): return True


def env(f): return lambda s: f(s.env)(s)


def opt(*args): return alt(seq(*args), any)


def delay(f): return lambda s: f()(s)


def guard(f): return lambda s: f(s.env)


def topdown(pat):
    f = seq(pat, every(delay(lambda: f)))
    return f


def bottomup(pat):
    f = seq(every(delay(lambda: f)), pat)
    return f


def innermost(pat):
    f = bottomup(opt(seq(pat, delay(lambda: f))))
    return f
