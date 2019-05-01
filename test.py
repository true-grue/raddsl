from doctest import run_docstring_examples
import jsn
import calc
import fmt
import simp

run_docstring_examples(jsn.json_parse, vars(jsn))
run_docstring_examples(calc.calc, vars(calc))
run_docstring_examples(fmt.ast_to_text, vars(fmt))
run_docstring_examples(simp.simplify, vars(simp))
