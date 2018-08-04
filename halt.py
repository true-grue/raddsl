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

store_instr = lambda M: alt(
  rule(And(A, B), to(lambda v: store(M, v.A, M[v.A] & M[v.B]))),
  rule(Or(A, B), to(lambda v: store(M, v.A, M[v.A] | M[v.B]))),
  rule(Xor(A, B), to(lambda v: store(M, v.A, M[v.A] ^ M[v.B]))),
  rule(Not(A), to(lambda v: store(M, v.A, ~M[v.A]))),
  rule(Mov(A, B), to(lambda v: store(M, v.A, M[v.B]))),
  rule(Set(A, B), to(lambda v: store(M, v.A, v.B))),
  rule(Random(A), to(lambda v: store(M, v.A, randint(0, 1))))
)

sim = repeat(rule(
  [let(MEM=id), let(PROG=id), let(PC=id), let(COUNT=id)],
  to(lambda v: v.PROG[v.PC]), scope(lambda v: alt(
    seq(store_instr(v.MEM), to(lambda v: v.PC + 1)),
    seq(Jmp(A), to(lambda v: v.A)),
    seq(Jz(A, B), to(lambda v: v.PC + 1 if v.MEM[v.B] else v.A)),
    seq(Halt(), to(lambda v: None))
  )),
  let(PC1=non(None)), guard(lambda v: v.COUNT < 100000),
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

print("Program halts! %d instructions executed." % simulate(source)[3])
