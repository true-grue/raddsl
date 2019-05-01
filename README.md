# raddsl — a toolset for rapid prototyping of [DSL compilers](http://composition.al/blog/2017/04/30/what-isnt-a-high-performance-dsl/)

Two combinator-based libraries (eDSLs) written in Python:

1. *parse.py* for syntax analysis: PEG, scannerless parsing, selective memoization, Pratt parser.
1. *rewrite.py* for AST transformations: strategic term rewriting.

Ideas are taken from:

1. Schorre, D. V. "Meta ii a syntax-oriented compiler writing language." Proceedings of the 1964 19th ACM national conference. ACM, 1964.
1. Carr, C. Stephen, David A. Luther, and Sherian Erdmann. The Tree-Meta Compiler-Compiler System: A Meta Compiler System for the Univac 1108 and the General Electric 645. No. TR-4-12. UTAH UNIV SALT LAKE CITY DEPT OF COMPUTER SCIENCE, 1969.
1. Pratt, Vaughan R. "Top Down Operator Precedence." POPL. Vol. 73. 1973.
1. Redziejowski, Roman R. "Mouse: from parsing expressions to a practical parser." Concurrency Specification and Programming Workshop. 2009.
1. Becket, Ralph, and Zoltan Somogyi. "DCGs+ memoing= packrat parsing but is it worth it?." International Symposium on Practical Aspects of Declarative Languages. Springer, Berlin, Heidelberg, 2008.
1. Warren, David HD. "Logic programming and compiler writing." Software: Practice and Experience 10.2 (1980): 97-125.
1. Visser, Eelco. "Program transformation with Stratego/XT." Domain-specific program generation. Springer, Berlin, Heidelberg, 2004. 216-238.
