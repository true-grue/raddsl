# code formatter

from raddsl.rewrite import *
from term import *

X, Y = let(X=id), let(Y=id)

kernel = topdown(opt(alt(
  rule(Id(X), to(lambda v: H(v.X))),
  rule(Int(X), to(lambda v: H(str(v.X)))),
  rule(Assign(X, Y), to(lambda v: H(v.X, "=", H(v.Y, ";", sep="")))),
  rule(Bop(let(O=id), X, Y), to(lambda v: H(v.X, v.O, v.Y))),
  rule(If(let(C=id), X), to(lambda v: V(
    H("if", H("(", v.C, ")", sep=""), "{"), V(*v.X, tab="\t"), "}"
  ))),
  rule(Func(X, [], Y), to(lambda v: V(
    H("void", H(v.X, "(void)", sep="")), "{", V(*v.Y, tab="\t"), "}"
  )))
)))

python = topdown(opt(alt(
  rule(Id(X), to(lambda v: H(v.X))),
  rule(Int(X), to(lambda v: H(str(v.X)))),
  rule(Assign(X, Y), to(lambda v: H(v.X, "=", v.Y))),
  rule(Bop(let(O=id), X, Y), to(lambda v: H(v.X, v.O, v.Y))),
  rule(If(let(C=id), X), to(lambda v: V(
    H("if", H(v.C, ":", sep="")), V(*v.X, tab=" " * 4)))),
  rule(Func(X, [], Y), to(lambda v: V(
    H("def", H(v.X, "():", sep="")), V(*v.Y, tab=" " * 4)
  )))
)))

def fmt(box):
  def unbox(box):
    if is_term(box):
      hd, tl = box[0], [unbox(x) for x in box[1:]]
      if hd == "H":
        return hd.get("sep", " ").join(tl)
      if hd == "V":
        return [hd.get("tab", ""), tl]
    return box

  def flatten(lst, tab=""):
    if isinstance(lst, list):
      return "\n".join([flatten(y, tab + lst[0]) for y in lst[1]])
    return tab + lst

  return flatten(unbox(box))

ast = Func(Id("foo"), [], [
    If(Bop(">", Id("x"), Int(0)), [
      Assign(Id("x"), Int(0)),
      Assign(Id("z"), Bop("+", Id("y"), Int(1)))
    ]),
    Assign(Id("y"), Id("z"))
  ]
)

def kernel_test():
  t = Tree(ast)
  kernel(t)
  return fmt(t.out)

def python_test():
  t = Tree(ast)
  python(t)
  return fmt(t.out)
