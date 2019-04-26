# Simple calculator

from parse import *

ws = many(space)
num = seq(quote(some(digit)), to(1, lambda x: ("num", int(x))))
oper = seq(quote(one_of("+-*/()")), to(1, lambda x: ("op", x)))
token = seq(ws, alt(num, oper))
skip = lambda o: seq(token, pop(lambda x: x == ("op", o)))
left = lambda p: seq(expr(p + 1), to(3, binop))
tag = lambda x: x[1] if x[0] == "op" else x[0]
table, expr = precedence(token, tag)
table["num"] = to(1, lambda x: x[1]), None
table["("] = seq(drop, expr(0), skip(")")), None
table["+"] = left, 1
table["-"] = left, 1
table["*"] = left, 2
table["/"] = left, 2
main = seq(expr(0), end)


def binop(x, o, y):
    return int(eval("%s%s%s" % (x, o[1], y)))


def calc(text):
    """
    >>> calc("(100 / 10) * 4 + 2")
    42
    """
    s = Stream(text)
    if not main(s):
        print("%s\n%s" % (text, " " * s.epos + "^ Eh?"))
        return None
    return(s.out[0])
