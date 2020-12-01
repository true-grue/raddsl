import doctest
import jsn
import calc
import fmt
import simp
import pp

for m in jsn, calc, fmt, simp, pp:
    doctest.testmod(m)
