# Halting Problem
# https://www.reddit.com/r/dailyprogrammer/comments/1euacb/052213_challenge_125_intermediate_halt_its/

from raddsl.parse import *

ws = many(space)
number = seq(ws, quote(some(digit)), to(1, int))
name = seq(ws, quote(some(letter)))
instr = group(name, many(number))
program = seq(number, many(instr))

def parse(src):
  s = Stream(src)
  return s.out if program(s) else []
