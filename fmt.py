# Code formatter

from rewrite import *


class Head(dict):
    def __eq__(self, right):
        return self["tag"] == right

    def __ne__(self, right):
        return not self.__eq__(right)


def make_term(tag):
    return lambda *args, **attrs: (Head(tag=tag, **attrs),) + args


def is_term(x):
    return isinstance(x, tuple)


H = make_term("H")
V = make_term("V")


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


Var = make_term("Var")
Int = make_term("Int")
Assign = make_term("Assign")
Bop = make_term("Bop")
If = make_term("If")
Func = make_term("Func")

X, Y = let(X=any), let(Y=any)

kernelc = topdown(opt(alt(
    rule(Var(X), to(lambda v: H(v.X))),
    rule(Int(X), to(lambda v: H(str(v.X)))),
    rule(Assign(X, Y), to(lambda v: H(v.X, "=", H(v.Y, ";", sep="")))),
    rule(Bop(let(O=any), X, Y), to(lambda v: H(v.X, v.O, v.Y))),
    rule(If(let(C=any), X), to(lambda v: V(
        H("if", H("(", v.C, ")", sep=""), "{"), V(*v.X, tab="\t"), "}"
    ))),
    rule(Func(X, [], Y), to(lambda v: V(
        H("void", H(v.X, "(void)", sep="")), "{", V(*v.Y, tab="\t"), "}"
    )))
)))

python = topdown(opt(alt(
    rule(Var(X), to(lambda v: H(v.X))),
    rule(Int(X), to(lambda v: H(str(v.X)))),
    rule(Assign(X, Y), to(lambda v: H(v.X, "=", v.Y))),
    rule(Bop(let(O=any), X, Y), to(lambda v: H(v.X, v.O, v.Y))),
    rule(If(let(C=any), X), to(lambda v: V(
        H("if", H(v.C, ":", sep="")), V(*v.X, tab=" " * 4)))),
    rule(Func(X, [], Y), to(lambda v: V(
        H("def", H(v.X, "():", sep="")), V(*v.Y, tab=" " * 4)
    )))
)))


def ast_to_text(ast, rules):
    """
    >>> ast = Func(Var("foo"), [], [
    ...     If(Bop(">", Var("x"), Int(0)), [
    ...         Assign(Var("x"), Int(0)),
    ...         Assign(Var("z"), Bop("+", Var("y"), Int(1)))
    ...     ]),
    ...     Assign(Var("y"), Var("z"))
    ... ])
    >>> ast_to_text(ast, kernelc)
    'void foo(void)\\n{\\n\\tif (x > 0) {\\n\\t\\tx = 0;\\n\\t\\tz = y + 1;\\n\\t}\\n\\ty = z;\\n}'
    >>> ast_to_text(ast, python)
    'def foo():\\n    if x > 0:\\n        x = 0\\n        z = y + 1\\n    y = z'
    """
    t = Tree(ast)
    return fmt(t.out) if rules(t) else None
