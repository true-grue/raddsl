# Infix to AST translator

from raddsl_parse import *

ast_op = to(3, lambda x, o, y: (o[1], x, y))
ast_uop = to(2, lambda o, x: (o[1], x))

ws = many(space)
num = seq(cite(some(digit)), to(1, lambda x: ("num", int(x))))
var = seq(cite(seq(letter, many(alt(letter, digit)))),
          to(1, lambda x: ("var", x)))
op = seq(cite(one_of("+-*/^()")), to(1, lambda x: ("sym", x)))
token = seq(ws, alt(num, var, op))

def token_is(k): return seq(token, guard(lambda x: x[0] == k))
def with_val(v): return guard(lambda x: x[1] == v)
def sym(v): return seq(token_is("sym"), with_val(v), drop)
def left(p): return seq(tab.expr(p + 1), ast_op)
def right(p): return seq(tab.expr(p), ast_op)

tab = Prec(token, lambda t: t[1] if t[0] == "sym" else t[0])
expr = tab.expr(0)
tab.prefix["num"] = tab.prefix["var"] = empty
tab.prefix["("] = seq(drop, expr, sym(")"))
tab.prefix["-"] = seq(tab.expr(4), ast_uop)

tab.infix["+"] = tab.infix["-"] = left, 1
tab.infix["*"] = tab.infix["/"] = left, 2
tab.infix["^"] = right, 3

def calc(text):
    """
    >>> calc("b^2 - 4*a*c")
    ('-', ('^', ('var', 'b'), ('num', 2)), ('*', ('*', ('num', 4), ('var', 'a')), ('var', 'c')))
    """
    s = State(text)
    if not expr(s):
        print("%s\n%s" % (text, " " * s.err + "^ Eh?"))
        return None
    return(s.out[0])
