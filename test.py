from doctest import run_docstring_examples
from json_parser import json_parse
from calc import calc

run_docstring_examples(json_parse, globals())
run_docstring_examples(calc, globals())
