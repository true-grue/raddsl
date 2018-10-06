# calc

from raddsl.rewrite import *
from calc_parser import parse, Int, BinOp

X, Y = let(X=id), let(Y=id)

calc_rules = alt(
  Int(id),
  rule(BinOp("+", Int(X), Int(Y)), to(lambda v: Int(v.X + v.Y))),
  rule(BinOp("-", Int(X), Int(Y)), to(lambda v: Int(v.X - v.Y))),
  rule(BinOp("*", Int(X), Int(Y)), to(lambda v: Int(v.X * v.Y))),
  rule(BinOp("/", Int(X), Int(Y)), to(lambda v: Int(v.X // v.Y)))
)

def calc(src):
  t = Tree(parse(src))
  bottomup(calc_rules)(t)
  return t.out
