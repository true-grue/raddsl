# Simple calculator

from parse import *

ws = many(space)
num = seq(cite(some(digit)), to(1, lambda x: ("num", int(x))))
oper = seq(cite(one_of("+-*/()")), to(1, lambda x: ("op", x)))
token = memo(seq(ws, alt(num, oper)))


def op(o): return seq(token, guard(lambda x: x == ("op", o)), drop)


def left(p): return seq(tab.expr(p + 1), to(3, binop))


tab = Prec(token, lambda x: x[1] if x[0] == "op" else x[0])
tab.prefix["num"] = to(1, lambda x: x[1])
tab.prefix["("] = seq(drop, tab.expr(0), op(")"))
tab.infix["+"] = left, 1
tab.infix["-"] = left, 1
tab.infix["*"] = left, 2
tab.infix["/"] = left, 2

main = seq(tab.expr(0), ws, end)


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
