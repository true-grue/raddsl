# PL/0

from lib.dsl_parse import *
from pl0_term import *

def parse_expr(rest):
  expr, rest = rest[0], rest[1:]
  while rest:
    o, x, rest = rest[0], rest[1], rest[2:]
    expr = Binop(o[1], expr, x)
  return expr

var = to(1, lambda x: Var(x))
const = to(1, lambda x: Const(x))
block = to(1, lambda x: Block(x))
proc = to(2, lambda x, y: Proc(x, y))
assign = to(2, lambda x, y: Assign(x, y))
call = to(1, lambda x: Call(x))
read = to(1, lambda x: Read(x))
write = to(1, lambda x: Write(x))
begin = to(1, lambda x: Begin(x))
if_stmt = to(2, lambda x, y: If(x, y))
while_stmt = to(2, lambda x, y: While(x, y))
unop = to(2, lambda o, x: Unop(o[1], x))
binop = to(3, lambda x, o, y: Binop(o[1], x, y))
expr = to(1, lambda x: parse_expr(x))
negate = to(2, lambda o, x: [
  Unop("-", x[0])] + x[1:] if o and o[1] == "-" else x)
nop = to(0, lambda: Nop())
