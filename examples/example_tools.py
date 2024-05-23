from __future__ import annotations

from IPython.lib.pretty import pretty


def evaluate_single_expression(expr: str) -> None:
    inp = ""
    out = "# "
    sexpr = expr.split(" = ", 1)
    if len(sexpr) == 2:
        exec(expr, globals())
        print(f"{inp}{expr}")
        print(f"{out}{eval(sexpr[0].strip())}")
    elif len(sexpr) == 1:
        print(f"{inp}{expr}")
        print(f"{out}{pretty(eval(expr))}")
    print()


def evaluate_expressions(*exprs):
    for expr in exprs:
        evaluate_single_expression(expr)