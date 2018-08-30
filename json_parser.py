# JSON parser

from lib.dsl_parse import *

token = lambda tag: to(1, lambda x: (tag, x))
token_num = to(1, lambda x: ("num", float(x)))
ws = seq(some(one_of(" \t\r\n")), to(0, lambda: None))
operator = seq(quote(one_of("[{]}:,")), token("op"))
int_part = alt(seq(range_of("1", "9"), many(digit)), a("0"))
frac = seq(a("."), some(digit))
exp = seq(one_of("eE"), opt(one_of("-+")), some(digit))
number = seq(quote(opt(a("-")), int_part, opt(frac), opt(exp)), token_num)
uhex = alt(digit, range_of("a", "f"), range_of("A", "F"))
uXXXX = seq(a("u"), uhex, uhex, uhex, uhex)
escaped = seq(a("\\"), alt(one_of('"\\/bfnrt'), uXXXX))
string = seq(
  a('"'), quote(many(alt(escaped, non(one_of('"\\'))))), a('"'), token("str")
)
keyword = seq(quote(alt(a("false"), a("null"), a("true"))), token("kw"))
tokens = seq(many(alt(ws, operator, string, number, keyword)), end)

tag = lambda t: seq(push(eat(lambda x: x[0] == t)), to(1, lambda x: x[1]))
KEYWORDS = dict(false=False, true=True, null=None)
kw = seq(tag("kw"), to(1, lambda x: KEYWORDS[x]))
op = lambda n: eat(lambda x: x[0] == "op" and x[1] == n)
value = lambda x: value(x)
array = group(op("["), opt(list_of(value, op(","))), op("]"))
member = group(tag("str"), op(":"), value)
obj = seq(op("{"), group(opt(list_of(member, op(",")))), op("}"), to(1, dict))
value = alt(tag("num"), tag("str"), kw, obj, array)
json = alt(obj, array)

def scan(source):
  s = Stream(source)
  if not tokens(s):
    return []
  return [x for x in s.out if x is not None]

def parse(source):
  s = Stream(scan(source))
  return s.out[0] if json(s) else []

source = """
{ "Object":{"Zoom": 1104.360027711047, "Property1":{"Property2":{"Color":[0,153,255,0]},"Width":40}} }
"""

print(parse(source))
