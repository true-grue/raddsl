# Simple calculator

from parse import *

ws = many(space)
num = seq(quote(some(digit)), to(1, lambda x: ("num", int(x))))
oper = seq(quote(one_of("+-*/()")), to(1, lambda x: ("op", x)))
token = memo(seq(ws, alt(num, oper)))


def op(o): return seq(token, guard(lambda x: x == ("op", o)), drop)


def left(p): return seq(expr(p + 1), to(3, binop))


table, expr = precedence(token, lambda x: x[1] if x[0] == "op" else x[0])
table["num"] = to(1, lambda x: x[1]), None
table["("] = seq(drop, expr(0), op(")")), None
table["+"] = left, 1
table["-"] = left, 1
table["*"] = left, 2
table["/"] = left, 2
main = seq(expr(0), ws, end)


def binop(x, o, y): return int(eval("%s%s%s" % (x, o[1], y)))


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
