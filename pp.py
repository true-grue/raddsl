# Pretty printer for arithmetic expressions

from lib.raddsl_rewrite import *
from lib.term import *


Num = make_term("Num")
Var = make_term("Var")
Uop = make_term("Uop")
Bop = make_term("Bop")


def arule(f):
    def walk(s):
        t = clone_term(s.out)
        s.out = f(t)
        return True
    return walk


@arule
def inherited_init(t):
    return set_attr(t, "prec", 0)


def inherited_bop(prec):
    @arule
    def f(t):
        t = rewrite_term(t, 2, clone_term(t[2], prec=prec))
        return rewrite_term(t, 3, clone_term(t[3], prec=prec))
    return f


def synthesized_bop(prec):
    @arule
    def f(t):
        s = attr(t[2], "pp") + t[1] + attr(t[3], "pp")
        if attr(t, "prec") > prec:
            s = "(" + s + ")"
        return set_attr(t, "pp", s)
    return f


@arule
def synthesized_lit(t):
    return set_attr(t, "pp", str(t[1]))


inherited = alt(
    seq(Bop(alt("+", "-"), Any, Any), inherited_bop(1)),
    seq(Bop(alt("*", "/"), Any, Any), inherited_bop(2)),
    alt(Var(Any), Num(Any))
)

synthesized = alt(
    seq(Bop(alt("+", "-"), Any, Any), synthesized_bop(1)),
    seq(Bop(alt("*", "/"), Any, Any), synthesized_bop(2)),
    seq(alt(Var(Any), Num(Any)), synthesized_lit)
)

ag = seq(inherited_init, downup(inherited, synthesized))


def pp(ast):
    """
    >>> pp(Bop('+', Bop('-', Bop('+', Num(2), Bop('*', Num(2), Num(3))), Bop('*', Bop('/', Num(2), Num(2)), Bop('-', Num(4), Num(3)))), Num(1)))
    '2+2*3-2/2*(4-3)+1'
    """
    s = State(ast)
    return attr(s.out, "pp") if ag(s) else None
