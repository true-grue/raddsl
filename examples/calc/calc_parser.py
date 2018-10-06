# calc

from raddsl.parse import *

make_term = lambda t: lambda *a: (t,) + a

Int = make_term("Int")
Op = make_term("Op")
BinOp = make_term("BinOp")

tok_op = to(1, Op)
tok_none = to(0, lambda: None)
tok_num = to(1, lambda x: Int(int(x)))

ws = seq(some(space), tok_none)
num = seq(quote(some(digit)), tok_num)
oper = seq(quote(one_of("+-*/()")), tok_op)
tokens = seq(many(alt(ws, oper, num)), end)

op = lambda o: eat(lambda x: x == ("Op", o))
val = lambda x: x[1] if x[0] == "Op" else x[0]

ast_bop = to(3, lambda x, o, y: BinOp(o[1], x, y))
left_bop = lambda b: seq(push(id), expr(b + 1), ast_bop)

expr = tdop(lambda x: prefix.get(val(x)), lambda x: infix.get(val(x)))

prefix = {
  "Int": push(id),
  "(": seq(id, expr(0), op(")"))
}

infix = {
  "+": (left_bop, 10),
  "-": (left_bop, 10),
  "*": (left_bop, 20),
  "/": (left_bop, 20)
}

def scan(src):
  s = Stream(src)
  return [x for x in s.out if x] if tokens(s) else []

def parse(src):
  s = Stream(scan(src))
  return s.out[0] if expr(0)(s) else []
