# PL/0

from raddsl.rewrite import *
from pl0_parser import parse
from pl0_term import *

TAB = " " * 4

PRELUDE = """
class Mem:
    pass
M = Mem()
def read():
    return int(input())
def write(x):
    print(x)
""".strip()

X, Y, Z = let(X=id), let(Y=id), let(Z=id)

def emit(t):
  if t.out:
    t.code.append(TAB * t.level + t.out)
  return True

def indent(f):
  def walk(t):
    t.level += 1
    m = f(t)
    t.level -= 1
    return m
  return walk

name = rule(Id(X), to(lambda v: "M.%s" % v.X))
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
  name,
  num
))

var = seq(Var(id), build(lambda v: Line("")))

pair = rule(
  [let(X=name), let(Y=num)], to(lambda v: Line("%s = %s" % (v.X, v.Y)))
)

const = rule(Const(let(X=each(pair))), to(lambda v: v.X))

block = delay(lambda: block)
proc = rule(
  Proc(X, let(Y=block)), to(lambda v: [Line("def %s():" % v.X[1]), Tab(v.Y)])
)

stmt = delay(lambda: stmt)
stmt = alt(
  rule(
    Assign(let(X=name), let(Y=expr)),
    to(lambda v: Line("%s = %s" % (v.X, v.Y)))
  ),
  rule(Call(X), to(lambda v: Line("%s()" % v.X[1]))),
  rule(Read(let(X=name)), to(lambda v: Line("%s = read()" % v.X))),
  rule(Write(let(X=name)), to(lambda v: Line("write(%s)" % v.X))),
  rule(Begin(let(X=each(stmt))), to(lambda v: v.X)),
  rule(
    If(let(X=expr), let(Y=stmt)),
    to(lambda v: [Line("if %s:" % v.X), Tab(v.Y)])
  ),
  rule(
    While(let(X=expr), let(Y=stmt)),
    to(lambda v: [Line("while %s:" % v.X), Tab(v.Y)])
  ),
  rule(Nop(), to(lambda v: Line("pass")))
)

block = rule(
  Block(let(X=each(alt(var, const, proc, stmt)))), to(lambda v: v.X)
)

gen = delay(lambda: gen)
gen = alt(Tab(indent(gen)), Line(emit), each(gen))

def trans(source):
  ast = parse(source)
  t = Tree(ast)
  t.level = 0
  t.code = [PRELUDE]
  if seq(block, gen)(t):
    return "\n".join(t.code)
  return None
