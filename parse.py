# raddsl 03082019
# Author: Peter Sovietov

class Stream:
    def __init__(self, buf):
        self.buf = buf
        self.pos = 0
        self.epos = 0
        self.out = []
        self.memo = {}


def back(s, i, j, err=True):
    if err and s.pos > s.epos:
        s.epos = s.pos
    s.pos = i
    del s.out[j:]
    return False


def peek(f):
    def parse(s):
        i, j = s.pos, len(s.out)
        t = f(s)
        s.pos = i
        del s.out[j:]
        return t
    return parse


def npeek(f):
    def parse(s):
        i, j = s.pos, len(s.out)
        t = f(s)
        s.pos = i
        del s.out[j:]
        return not t
    return parse


def alt(*args):
    def parse(s):
        for f in args:
            if f(s):
                return True
        return False
    return parse


def many(f):
    def parse(s):
        while f(s):
            pass
        return True
    return parse


def some(f):
    def parse(s):
        if not f(s):
            return False
        while f(s):
            pass
        return True
    return parse


def seq(*args):
    def parse(s):
        i, j = s.pos, len(s.out)
        for f in args:
            if not f(s):
                return back(s, i, j)
        return True
    return parse


def repeat(f, n):
    def parse(s):
        i, j = s.pos, len(s.out)
        for i in range(n):
            if not f(s):
                return back(s, i, j)
        return True
    return parse


def quote(*args):
    f = seq(*args)

    def parse(s):
        i = s.pos
        if f(s):
            s.out.append(s.buf[i:s.pos])
            return True
        return False
    return parse


def push(f):
    def parse(s):
        i = s.pos
        if f(s):
            s.out.append(s.buf[i])
            return True
        return False
    return parse


def unpack(f):
    def parse(s):
        f(s)
        s.out += s.out.pop()
        return True
    return parse


def guard(f):
    def parse(s):
        return f(s.out[-1])
    return parse


def to(n, f):
    def parse(s):
        i = len(s.out) - n
        s.out[i:] = [f(*s.out[i:])]
        return True
    return parse


def group(*args):
    f = seq(*args)

    def parse(s):
        i = len(s.out)
        if f(s):
            s.out[i:] = [s.out[i:]]
            return True
        return False
    return parse


def eat(f):
    def parse(s):
        if s.pos < len(s.buf) and f(s.buf[s.pos]):
            s.pos += 1
            return True
        return False
    return parse


def a(term):
    def parse(s):
        i = s.pos + len(term)
        if s.buf[s.pos:i] == term:
            s.pos = i
            return True
        return False
    return parse


def match(words):
    d = {}
    for w in words:
        d[len(w)] = d.get(len(w), set()) | set([w])
    sets = sorted(d.items(), reverse=True)

    def parse(s):
        for x in sets:
            if s.buf[s.pos:s.pos + x[0]] in x[1]:
                s.pos += x[0]
                return True
        return False
    return parse


def empty(s): return True


def opt(f): return alt(f, empty)


def non(f): return seq(npeek(f), any)


def maybe(f, x): return alt(f, to(0, lambda: x))


def one_of(chars): return eat(lambda c: c in chars)


def range_of(a, b): return eat(lambda x: a <= x <= b)


def list_of(f, delim): return seq(f, many(seq(delim, f)))


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
    def parse(s):
        key = f, s.pos
        if key in s.memo:
            o, s.pos = s.memo[key]
            s.out.append(o)
            return True
        if not f(s):
            return False
        s.memo[key] = s.out[-1], s.pos
        return True
    return parse


def precedence(token, tag):
    table = {}

    def prefix(s):
        if not token(s):
            return False
        e = table.get(tag(s.out[-1]))
        return e and e[1] is None and e[0](s)

    def infix(s, p):
        i, j = s.pos, len(s.out)
        if not token(s):
            return False
        e = table.get(tag(s.out[-1]))
        if e and e[1] is not None and e[1] >= p:
            s.out.append(e)
            return True
        return back(s, i, j, False)

    def expr(s, min_p):
        i, j = s.pos, len(s.out)
        if not prefix(s):
            return back(s, i, j, False)
        while infix(s, min_p):
            f, p = s.out.pop()
            if not f(p)(s):
                return back(s, i, j)
        return True

    return table, lambda p: lambda s: expr(s, p)
