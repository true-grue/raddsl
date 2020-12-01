# Author: Peter Sovietov


class State:
    def __init__(self, buf, **attrs):
        self.buf = buf
        self.pos = 0
        self.err = 0
        self.out = []
        self.mem = {}
        self.__dict__.update(attrs)


def back(s, curr, is_error=True):
    if is_error and s.pos > s.err:
        s.err = s.pos
    buf_pos, out_pos = curr
    s.pos = buf_pos
    del s.out[out_pos:]
    return False


def peek(f):
    def walk(s):
        buf_pos, out_pos = s.pos, len(s.out)
        res = f(s)
        s.pos = buf_pos
        del s.out[out_pos:]
        return res
    return walk


def npeek(f):
    def walk(s):
        buf_pos, out_pos = s.pos, len(s.out)
        res = f(s)
        s.pos = buf_pos
        del s.out[out_pos:]
        return not res
    return walk


def alt(*args):
    def walk(s):
        for f in args:
            if f(s):
                return True
        return False
    return walk


def many(f):
    def walk(s):
        while f(s):
            pass
        return True
    return walk


def some(f):
    def walk(s):
        if not f(s):
            return False
        while f(s):
            pass
        return True
    return walk


def seq(*args):
    def walk(s):
        curr = s.pos, len(s.out)
        for f in args:
            if not f(s):
                return back(s, curr)
        return True
    return walk


def repeat(f, n):
    def walk(s):
        curr = s.pos, len(s.out)
        for i in range(n):
            if not f(s):
                return back(s, curr)
        return True
    return walk


def cite(*args):
    f = seq(*args)

    def walk(s):
        pos = s.pos
        if f(s):
            s.out.append(s.buf[pos:s.pos])
            return True
        return False
    return walk


def push(f):
    def walk(s):
        pos = s.pos
        if f(s):
            s.out.append(s.buf[pos])
            return True
        return False
    return walk


def unpack(f):
    def walk(s):
        f(s)
        s.out += s.out.pop()
        return True
    return walk


def guard(f):
    def walk(s): return f(s.out[-1])
    return walk


def to(n, f):
    def walk(s):
        out_pos = len(s.out) - n
        s.out[out_pos:] = [f(*s.out[out_pos:])]
        return True
    return walk


def group(*args):
    f = seq(*args)

    def walk(s):
        out_pos = len(s.out)
        if f(s):
            s.out[out_pos:] = [s.out[out_pos:]]
            return True
        return False
    return walk


def eat(f):
    def walk(s):
        if s.pos < len(s.buf) and f(s.buf[s.pos]):
            s.pos += 1
            return True
        return False
    return walk


def a(pat):
    def walk(s):
        pos = s.pos + len(pat)
        if s.buf[s.pos:pos] == pat:
            s.pos = pos
            return True
        return False
    return walk


def match(words):
    d = {}
    for w in words:
        d[len(w)] = d.get(len(w), set()) | set([w])
    sets = sorted(d.items(), reverse=True)

    def walk(s):
        for size, patterns in sets:
            if s.buf[s.pos:s.pos + size] in patterns:
                s.pos += size
                return True
        return False
    return walk


def empty(s): return True


def opt(f): return alt(f, empty)


def non(f): return seq(npeek(f), any)


def maybe(f, x): return alt(f, to(0, lambda: x))


def one_of(chars): return eat(lambda c: c in chars)


def range_of(a, b): return eat(lambda x: a <= x <= b)


def list_of(f, d): return seq(f, many(seq(d, f)))


any = eat(lambda x: True)
drop = unpack(to(1, lambda x: []))
end = npeek(any)
digit = eat(lambda x: x.isdigit())
letter = eat(lambda x: x.isalpha())
lower = eat(lambda x: x.islower())
upper = eat(lambda x: x.isupper())
alnum = eat(lambda x: x.isalnum())
space = eat(lambda x: x.isspace())


def memo(f):
    def walk(s):
        key = f, s.pos
        if key in s.mem:
            out, s.pos = s.mem[key]
            s.out.append(out)
            return True
        if not f(s):
            return False
        s.mem[key] = s.out[-1], s.pos
        return True
    return walk


class Prec:
    def __init__(self, token, key):
        self.token = token
        self.key = key
        self.prefix = {}
        self.infix = {}

    def prefix_expr(self, s):
        if not self.token(s):
            return False
        expr = self.prefix.get(self.key(s.out[-1]))
        return expr and expr(s)

    def infix_expr(self, s, min_prec):
        curr = s.pos, len(s.out)
        if self.token(s):
            entry = self.infix.get(self.key(s.out[-1]))
            if entry and entry[1] >= min_prec:
                return entry
            back(s, curr, is_error=False)
        return None, 0

    def parse(self, s, min_prec):
        curr = s.pos, len(s.out)
        if not self.prefix_expr(s):
            return back(s, curr, is_error=False)
        while True:
            expr, prec = self.infix_expr(s, min_prec)
            if not expr:
                return True
            if not expr(prec)(s):
                return back(s, curr)

    def expr(self, prec): return lambda s: self.parse(s, prec)
