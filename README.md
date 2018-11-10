# raddsl

raddsl is a toolset for rapid prototyping of [DSL compilers](http://composition.al/blog/2017/04/30/what-isnt-a-high-performance-dsl/).

It consists of two combinator-based libraries (embedded DSLs) written in Python:

1. *parse.py* for lexical and syntax analysis (PEG, Pratt parser).
1. *rewrite.py* for AST transformations and code generation (strategic term rewriting).

raddsl is inspired by:

* [META II](https://en.wikipedia.org/wiki/META_II)
* [TREE-META](https://en.wikipedia.org/wiki/TREE-META)
* [Prolog](https://www.era.lib.ed.ac.uk/bitstream/handle/1842/6648/Warren1978.pdf)
* [Pratt Parser](https://en.wikipedia.org/wiki/Pratt_parser)
* [Stratego](https://en.wikipedia.org/wiki/Stratego/XT)

See *examples* folder for some examples of use of raddsl. See also:

* [Uzh compiler](https://github.com/true-grue/uzh).
* [PigletC compiler](https://github.com/true-grue/PigletC).

[Moscow Python Conf++ slides (in Russian)](http://sovietov.com/txt/dsl_python_conf.pdf)
