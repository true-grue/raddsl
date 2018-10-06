# prop
# http://releases.strategoxt.org/strategoxt-manual/strategoxt-manual-0.17pre18708-z74k09nh/manual/one-page/index.html

from raddsl.rewrite import *

X, Y = let(X=id), let(Y=id)

make_term = lambda t: lambda *a: (t,) + a

Atom = make_term("Atom")
T = make_term("T")
F = make_term("F")
And = make_term("And")
Or = make_term("Or")
Not = make_term("Not")
Impl = make_term("Impl")
Eq = make_term("Eq")

eval_rules = alt(
  rule(Not(T()), to(lambda v: F())),
  rule(Not(F()), to(lambda v: T())),
  rule(And(T(), X), to(lambda v: v.X)),
  rule(And(X, T()), to(lambda v: v.X)),
  rule(And(F(), X), to(lambda v: F())),
  rule(And(X, F()), to(lambda v: F())),
  rule(Or(T(), X), to(lambda v: T())),
  rule(Or(X, T()), to(lambda v: T())),
  rule(Or(F(), X), to(lambda v: v.X)),
  rule(Or(X, F()), to(lambda v: v.X)),
  rule(Impl(T(), X), to(lambda v: v.X)),
  rule(Impl(X, T()), to(lambda v: T())),
  rule(Impl(F(), X), to(lambda v: T())),
  rule(Eq(F(), X), to(lambda v: Not(v.X))),
  rule(Eq(X, F()), to(lambda v: Not(v.X))),
  rule(Eq(T(), X), to(lambda v: v.X)),
  rule(Eq(X, T()), to(lambda v: v.X))
)

eval_prop = bottomup(repeat(eval_rules))

DefN = rule(Not(X), to(lambda v: Impl(v.X, F())))
DefI = rule(Impl(X, Y), to(lambda v: Or(Not(v.X), v.Y)))
DefE = rule(Eq(X, Y), to(lambda v: And(Impl(v.X, v.Y), Impl(v.Y, v.X))))
DefO1 = rule(Or(X, Y), to(lambda v: Impl(Not(v.X), v.Y)))
DefO2 = rule(Or(X, Y), to(lambda v: Not(And(Not(v.X), Not(v.Y)))))
DefA1 = rule(And(X, Y), to(lambda v: Not(Or(Not(v.X), Not(v.Y)))))
DefA2 = rule(And(X, Y), to(lambda v: Not(Impl(v.X, Not(v.Y)))))
IDefI = rule(Or(Not(X), Y), to(lambda v: Impl(v.X, v.Y)))
IDefE = rule(And(Impl(X, Y), Impl(Y, X)), to(lambda v: Eq(v.X, v.Y)))

desugar = topdown(opt(alt(DefI, DefE)))
impl_nf = topdown(repeat(alt(DefN, DefA2, DefO1, DefE)))

def prop_test():
  t = Tree(And(Impl(T(), And(Atom("p"), Atom("q"))), Atom("p")))
  seq(desugar, eval_prop)(t)
  return t.out
