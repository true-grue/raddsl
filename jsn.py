# JSON parser

from lib.raddsl_parse import *

t_op = to(1, lambda x: ("op", x))
t_num = to(1, lambda x: ("num", float(x)))
t_str = to(1, lambda x: ("str", x))
ws = many(space)
OPERATORS = "[ { ] } : , false true null".split()
operator = seq(cite(match(OPERATORS)), t_op)
int_part = alt(seq(range_of("1", "9"), many(digit)), a("0"))
frac = seq(a("."), some(digit))
exp = seq(one_of("eE"), opt(one_of("-+")), some(digit))
number = seq(cite(opt(a("-")), int_part, opt(frac), opt(exp)), t_num)
uhex = alt(digit, range_of("a", "f"), range_of("A", "F"))
uXXXX = seq(a("u"), uhex, uhex, uhex, uhex)
escaped = seq(a("\\"), alt(one_of('"\\/bfnrt'), uXXXX))
string = seq(a('"'), cite(many(alt(non(one_of('"\\')), escaped))),
             a('"'), t_str)
token = memo(seq(ws, alt(operator, string, number)))


def op(o): return seq(token, guard(lambda x: x == ("op", o)), drop)
def ty(t): return seq(token, guard(lambda x: x[0] == t), to(1, lambda x: x[1]))
def value(x): return value(x)


true = seq(op("true"), to(0, lambda: True))
false = seq(op("false"), to(0, lambda: False))
null = seq(op("null"), to(0, lambda: None))
array = group(op("["), opt(list_of(value, op(","))), op("]"))
member = group(ty("str"), op(":"), value)
obj = seq(op("{"), group(opt(list_of(member, op(",")))), op("}"), to(1, dict))
value = alt(ty("num"), ty("str"), true, false, null, obj, array)
main = seq(alt(obj, array), ws, end)


def json_parse(text):
    """
    >>> d = json_parse('{ "Object":{"Zoom": false, "Property1":{"Property2":{"Color":[0,153,255,0]},"Width":40}} }')
    >>> d == {'Object': {'Zoom': False, 'Property1': {'Property2': {'Color': [0.0, 153.0, 255.0, 0.0]}, 'Width': 40.0}}}
    True
    """
    s = State(text)
    return s.out[0] if main(s) else None
