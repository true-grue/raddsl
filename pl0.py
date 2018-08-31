# PL/0

from lib.dsl_match import *
from pl0_parser import parse
from pl0_term import *

TAB = " " * 4

PRELUDE = """class Mem:
  pass
M = Mem()
def read():
  return int(input())
def write(x):
  print(x)"""

X = let(X=id)
Y = let(Y=id)
Z = let(Z=id)

def emit(t):
  if t.out:
    t.code.append(TAB * t.level + "".join(t.out))
  return True

def indent(t):
  t.level += 1
  return True

def dedent(t):
  t.level -= 1
  return True

ident = rule(Id(X), to(lambda v: "M.%s" % v.X))
num = rule(Num(X), to(lambda v: "%s" % v.X))

def trans_op(x):
  if x == "=": return "=="
  if x == "#": return "!="
  if x == "/": return "//"
  return x

expr = bottomup(alt(
  rule(Binop(X, Y, Z), to(lambda v: "(%s %s %s)" % (v.Y, trans_op(v.X), v.Z))),
  rule(Unop("odd", Y), to(lambda v: "(%s & 1 != 0)" % v.Y)),
  rule(Unop(X, Y), to(lambda v: "%s%s" % (v.X, v.Y))),
  ident,
  num
))

var = seq(Var(id), build(lambda v: Line([])))

pair = rule(
  [let(X=ident), let(Y=num)], to(lambda v: Line(["%s = %s" % (v.X, v.Y)]))
)

const = rule(Const(let(X=each(pair))), to(lambda v: v.X))

block = delay(lambda: block)

proc = rule(
  Proc(X, let(Y=block)),
  to(lambda v: [Line(["def ", v.X[1], "():"]), Tab(v.Y)])
)

stmt = delay(lambda: stmt)

stmt = alt(
  rule(
    Assign(let(X=ident), let(Y=expr)), to(lambda v: Line([v.X, " = ", v.Y]))
  ),
  rule(Call(X), to(lambda v: Line(["%s()" % v.X[1]]))),
  rule(Read(let(X=ident)), to(lambda v: Line([v.X, " = read()"]))),
  rule(Write(let(X=ident)), to(lambda v: Line(["write(", v.X, ")"]))),
  rule(Begin(let(X=each(stmt))), to(lambda v: v.X)),
  rule(
    If(let(X=expr), let(Y=stmt)),
    to(lambda v: [Line(["if ", v.X, ":"]), Tab(v.Y)])
  ),
  rule(
    While(let(X=expr), let(Y=stmt)),
    to(lambda v: [Line(["while ", v.X, ":"]), Tab(v.Y)])
  ),
  seq(Nop(), build(lambda v: Line(["pass"])))
)

block = rule(
  Block(let(X=each(alt(var, const, proc, stmt)))), to(lambda v: v.X)
)

gen = delay(lambda: gen)

gen = alt(Tab(seq(indent, gen, dedent)), Line(emit), each(gen))

def trans(source):
  ast = parse(source)
  t = Tree(ast)
  t.level = 0
  t.code = [PRELUDE]
  if seq(block, gen)(t):
    return "\n".join(t.code)
  return None

with open("primes.pl0") as f:
  source = f.read()
print(trans(source))
