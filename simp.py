# Algebraic simplifications

from rewrite import *


class Head(dict):
    def __eq__(self, right):
        return self["tag"] == right

    def __ne__(self, right):
        return not self.__eq__(right)

    def __repr__(self):
        return self["tag"]


def make_term(tag):
    return lambda *args, **attrs: (Head(tag=tag, **attrs),) + args


Var = make_term("Var")
Int = make_term("Int")
Neg = make_term("Neg")
Add = make_term("+")
Sub = make_term("-")
Mul = make_term("*")

X, Y, Z = let(X=non(Int(any))), let(Y=non(Int(any))), let(Z=non(Int(any)))
C, D = Int(let(C=any)), Int(let(D=any))


def Cadd(x, y):
    return alt(Add(x, y), Add(y, x))


def Cmul(x, y):
    return alt(Mul(x, y), Mul(y, x))


rules = innermost(alt(
    rule(Cadd(C, D), to(lambda v: Int(v.C + v.D))),
    rule(Sub(C, D), to(lambda v: Int(v.C - v.D))),
    rule(Cmul(C, D), to(lambda v: Int(v.C * v.D))),
    rule(Neg(C), to(lambda v: Int(-v.C))),
    rule(Cmul(Int(1), X), to(lambda v: v.X)),
    rule(Cmul(Int(-1), X), to(lambda v: Neg(v.X))),
    rule(Sub(X, C), to(lambda v: Add(v.X, Int(-v.C)))),
    rule(Cadd(Cmul(X, Y), Cmul(X, Z)), to(lambda v: Mul(v.X, Add(v.Y, v.Z)))),
    rule(Sub(Cmul(X, Y), Cmul(X, Z)), to(lambda v: Mul(v.X, Sub(v.Y, v.Z)))),
    rule(Cadd(Int(0), X), to(lambda v: v.X)),
    rule(Sub(X, X), to(lambda v: Int(0))),
    rule(Cmul(Int(0), X), to(lambda v: Int(0))),
    rule(Neg(Sub(X, Y)), to(lambda v: Sub(v.Y, v.X))),
    rule(Cadd(X, Cadd(C, Y)), to(lambda v: Add(Int(v.C), Add(v.X, v.Y)))),
    rule(Cadd(X, Sub(C, Y)), to(lambda v: Add(Int(v.C), Sub(v.X, v.Y)))),
    rule(Cadd(X, Sub(Y, C)), to(lambda v: Sub(Add(v.X, v.Y), Int(v.C)))),
    rule(Cadd(X, Sub(C, Y)), to(lambda v: Sub(Sub(v.X, v.Y), Int(v.C)))),
    rule(Cadd(X, Sub(Y, C)), to(lambda v: Add(Int(v.C), Sub(v.X, v.Y)))),
    rule(Cadd(C, Cadd(D, X)), to(lambda v: Add(Int(v.C + v.D), v.X))),
    rule(Cadd(C, Sub(D, X)), to(lambda v: Sub(Int(v.C + v.D), v.X))),
    rule(Cadd(C, Sub(X, D)), to(lambda v: Add(Int(v.C - v.D), v.X))),
    rule(Sub(C, Sub(X, D)), to(lambda v: Sub(Int(v.C + v.D), v.X))),
    rule(Sub(C, Sub(D, X)), to(lambda v: Add(Int(v.C - v.D), v.X))),
    rule(Cmul(C, Cmul(D, X)), to(lambda v: Mul(Int(v.C * v.D), v.X)))
))


def simplify(ast):
    """
    >>> ast = Add(Add(Sub(Var("x"), Int(4)), Sub(Var("y"), Int(5))), Add(Var("z"), Int(10)))
    >>> simplify(ast)
    (+, (Int, 1), (+, (Var, 'z'), (+, (Var, 'y'), (Var, 'x'))))
    """
    t = Tree(ast)
    return t.out if rules(t) else None