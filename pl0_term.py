# PL/0

make_term = lambda tag: lambda *args: (tag,) + args

Id = make_term("id")
Num = make_term("num")
Var = make_term("var")
Const = make_term("const")
Block = make_term("block")
Proc = make_term("proc")
Assign = make_term(":=")
Call = make_term("call")
Read = make_term("read")
Write = make_term("write")
Begin = make_term("begin")
If = make_term("if")
While = make_term("while")
Unop = make_term("unop")
Binop = make_term("binop")
Nop = make_term("nop")

Line = make_term("line")
Tab = make_term("tab")
