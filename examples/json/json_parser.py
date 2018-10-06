# JSON parser

from raddsl.parse import *

token = lambda tag: to(1, lambda x: (tag, x))
token_num = to(1, lambda x: ("num", float(x)))
ws = many(space)
OPERATORS = "[ { ] } : , false true null".split()
operator = seq(quote(match(OPERATORS)), token("op"))
int_part = alt(seq(range_of("1", "9"), many(digit)), a("0"))
frac = seq(a("."), some(digit))
exp = seq(one_of("eE"), opt(one_of("-+")), some(digit))
number = seq(quote(opt(a("-")), int_part, opt(frac), opt(exp)), token_num)
uhex = alt(digit, range_of("a", "f"), range_of("A", "F"))
uXXXX = seq(a("u"), uhex, uhex, uhex, uhex)
escaped = seq(a("\\"), alt(one_of('"\\/bfnrt'), uXXXX))
string = seq(a('"'), quote(many(alt(non(one_of('"\\')), escaped))),
  a('"'), token("str"))
tokens = seq(many(seq(ws, alt(operator, string, number))), ws, end)

op = lambda o: eat(lambda x: x == ("op", o))
tok = lambda t: seq(push(eat(lambda x: x[0] == t)), to(1, lambda x: x[1]))
true = seq(op("true"), to(0, lambda: True))
false = seq(op("false"), to(0, lambda: False))
null = seq(op("null"), to(0, lambda: None))
value = lambda x: value(x)
array = group(op("["), opt(list_of(value, op(","))), op("]"))
member = group(tok("str"), op(":"), value)
obj = seq(op("{"), group(opt(list_of(member, op(",")))), op("}"), to(1, dict))
value = alt(tok("num"), tok("str"), true, false, null, obj, array)
json = alt(obj, array)

def scan(src):
  s = Stream(src)
  return s.out if tokens(s) else []

def parse(src):
  s = Stream(scan(src))
  return s.out[0] if json(s) else []
