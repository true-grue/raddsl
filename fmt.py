# Code formatter

from raddsl_rewrite import *
from term import Head, make_term, is_term

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

pexpr = delay(lambda: pexpr)
stmt = delay(lambda: stmt)

val = alt(
    rule(Var(let(X=Any)), to(lambda v: H(v.X))),
    rule(Int(let(X=Any)), to(lambda v: H(str(v.X))))
)

pexpr = alt(
    val,
    rule(Bop(let(O=Any), let(X=pexpr), let(Y=pexpr)),
         to(lambda v: H("(", H(v.X, v.O, v.Y), ")", sep="")))
)

expr = alt(
    val,
    rule(Bop(let(O=Any), let(X=pexpr), let(Y=pexpr)),
         to(lambda v: H(v.X, v.O, v.Y)))
)

stmt = alt(
    expr,
    rule(Assign(let(X=expr), let(Y=expr)),
         to(lambda v: H(v.X, "=", H(v.Y, ";", sep="")))),
    rule(If(let(X=expr), let(Y=stmt)), to(lambda v: V(
        H("if", H("(", v.X, ")", sep=""), "{"), V(*v.Y, tab="\t"), "}"
    ))),
    rule(Func(let(X=expr), [], let(Y=stmt)), to(lambda v: V(
        H("void", H(v.X, "(void)", sep="")), "{", V(*v.Y, tab="\t"), "}"
    ))),
    to_all(stmt)
)


def ast_to_text(ast, rules):
    """
    >>> ast = Func(Var("foo"), [], [
    ...     If(Bop(">", Bop("+", Var("x"), Int(1)), Int(0)), [
    ...         Assign(Var("x"), Int(0)),
    ...         Assign(Var("z"), Bop("+", Var("y"), Int(1)))
    ...     ]),
    ...     Assign(Var("y"), Var("z"))
    ... ])
    >>> ast_to_text(ast, stmt)
    'void foo(void)\\n{\\n\\tif ((x + 1) > 0) {\\n\\t\\tx = 0;\\n\\t\\tz = y + 1;\\n\\t}\\n\\ty = z;\\n}'
    """
    t = State(ast)
    return fmt(t.out) if rules(t) else None
