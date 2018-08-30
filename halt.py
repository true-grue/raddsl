# Halting Problem
# https://www.reddit.com/r/dailyprogrammer/comments/1euacb/052213_challenge_125_intermediate_halt_its/

from random import randint
from halt_parser import parse
from lib.dsl_match import *

A = let(A=id)
B = let(B=id)

make_term = lambda tag: lambda *args: [tag] + list(args)

And = make_term("AND")
Or = make_term("OR")
Xor = make_term("XOR")
Not = make_term("NOT")
Mov = make_term("MOV")
Set = make_term("SET")
Random = make_term("RANDOM")
Jmp = make_term("JMP")
Jz = make_term("JZ")
Halt = make_term("HALT")

def store(data, addr, val):
  data[addr] = val & 1

store_instr = alt(
  seq(And(A, B), to(lambda v: store(v.MEM, v.A, v.MEM[v.A] & v.MEM[v.B]))),
  seq(Or(A, B), to(lambda v: store(v.MEM, v.A, v.MEM[v.A] | v.MEM[v.B]))),
  seq(Xor(A, B), to(lambda v: store(v.MEM, v.A, v.MEM[v.A] ^ v.MEM[v.B]))),
  seq(Not(A), to(lambda v: store(v.MEM, v.A, ~v.MEM[v.A]))),
  seq(Mov(A, B), to(lambda v: store(v.MEM, v.A, v.MEM[v.B]))),
  seq(Set(A, B), to(lambda v: store(v.MEM, v.A, v.B))),
  seq(Random(A), to(lambda v: store(v.MEM, v.A, randint(0, 1))))
)

sim = repeat(rule(
  [let(MEM=id), let(PROG=id), let(PC=id), let(COUNT=id)],
  to(lambda v: v.PROG[v.PC]), alt(
    seq(store_instr, to(lambda v: v.PC + 1)),
    seq(Jmp(A), to(lambda v: v.A)),
    seq(Jz(A, B), to(lambda v: v.PC + 1 if v.MEM[v.B] else v.A)),
    seq(Halt(), to(lambda v: None))
  ),
  let(PC1=non(None)), guard(lambda v: v.COUNT <= 100000),
  to(lambda v: [v.MEM, v.PROG, v.PC1, v.COUNT + 1])
))

def simulate(src):
  ast = parse(src)
  t = Tree([[0] * 32, ast[1:], 0, 1])
  sim(t)
  return t.out

source = """
6
NOT 0
JZ 5 0
OR 0 1
NOT 0
JMP 1
HALT
"""

count = simulate(source)[3]
if count > 100000:
  print("Unable to determine if application halts.")
else:
  print("Program halts! %d instructions executed." % count)
