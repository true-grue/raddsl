# code formatter

from raddsl.rewrite import *
from term import *

X, Y = let(X=id), let(Y=id)

box_rules = alt(
  rule(Id(X), to(lambda v: H(v.X))),
  rule(Int(X), to(lambda v: H(str(v.X)))),
  rule(Assign(X, Y), to(lambda v: H(v.X, "=", H(v.Y, ";", sep="")))),
  rule(Bop(let(O=id), X, Y), to(lambda v: H(v.X, v.O, v.Y))),
  rule(Block(X), to(lambda v: V(*v.X, nest="\t"))),
  rule(If(let(C=id), X), to(lambda v: V(
    H("if", H("(", v.C, ")", sep=""), "{"), v.X, "}"
  ))),
  rule(Func(X, [], Y), to(lambda v: V(
    H("void", H(v.X, "(void)", sep="")), "{", v.Y, "}"
  )))
)

box = topdown(opt(box_rules))

def fmt(box):
  def unbox(box):
    if is_term(box):
      hd, tl = box[0], [unbox(x) for x in box[1:]]
      if hd == "H":
        return hd.get("sep", " ").join(tl)
      if hd == "V":
        return [hd.get("nest", ""), tl]
    return box

  def flatten(lst, nest=""):
    if type(lst) == list:
      return "\n".join([flatten(y, nest + lst[0]) for y in lst[1]])
    return nest + lst

  return flatten(unbox(box))

ast = Func(Id("foo"), [],
  Block([
    If(Bop(">", Id("x"), Int(0)), Block([
      Assign(Id("x"), Int(0))
    ])),
    Assign(Id("y"), Id("z"))
  ])
)

def format_test():
  t = Tree(ast)
  box(t)
  return fmt(t.out)
