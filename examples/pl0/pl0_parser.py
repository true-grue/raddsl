# PL/0

from raddsl.parse import *
import pl0_ast as ast

token = lambda tag: to(1, lambda x: (tag, x))
token_num = to(1, lambda x: ("num", int(x)))
ws = seq(some(space), to(0, lambda: None))
name = seq(quote(letter, many(alnum)), token("id"))
num = seq(quote(some(digit)), token_num)
OPERATORS = """
; , ( ) + -  * / = # < <= > >= := ? ! .
odd begin end if then while do call var const procedure
""".split()
operator = seq(quote(match(OPERATORS)), token("op"))
tokens = seq(many(alt(ws, operator, num, name)), end)

tag = lambda t: push(eat(lambda x: x[0] == t))
ident = tag("id")
number = tag("num")
op = lambda n: eat(lambda x: x == ("op", n))
expression = lambda x: expression(x)
factor = alt(ident, number, seq(op("("), expression, op(")")))
term = seq(group(list_of(factor, push(alt(op("*"), op("/"))))), ast.expr)
expression = seq(
  maybe(push(alt(op("+"), op("-"))), None),
  group(list_of(term, push(alt(op("+"), op("-"))))), ast.negate, ast.expr
)
condition = alt(
  seq(push(op("odd")), expression, ast.unop),
  seq(
    expression,
    push(alt(op("="), op("#"), op("<"), op("<="), op(">"), op(">="))),
    expression, ast.binop
  )
)
statement = lambda x: statement(x)
statement = alt(
  seq(ident, op(":="), expression, ast.assign),
  seq(op("call"), ident, ast.call),
  seq(op("?"), ident, ast.read),
  seq(op("!"), ident, ast.write),
  seq(op("begin"), group(list_of(statement, op(";"))), op("end"), ast.begin),
  seq(op("if"), condition, op("then"), statement, ast.if_stmt),
  seq(op("while"), condition, op("do"), statement, ast.while_stmt),
  ast.nop
)
const = seq(
  op("const"), group(list_of(group(ident, op("="), number), op(","))),
  op(";"), ast.const
)
var = seq(op("var"), group(list_of(ident, op(","))), op(";"), ast.var)
block = lambda x: block(x)
procedure = seq(op("procedure"), ident, op(";"), block, op(";"), ast.proc)
block = seq(group(opt(const), opt(var), many(procedure), statement), ast.block)
program = seq(block, op("."))

def scan(src):
  s = Stream(src)
  return [x for x in s.out if x] if tokens(s) else []

def parse(src):
  s = Stream(scan(src))
  return s.out[0] if program(s) else []
