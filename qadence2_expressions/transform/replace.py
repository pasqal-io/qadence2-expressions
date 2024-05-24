from __future__ import annotations

from ..expr import Expr, Numeric, Numerical, Operator
from .evaluate import evaluate


def replace_core(value: Numeric | Numerical, rules: dict) -> Numeric | Numerical:
    if isinstance(value, Expr):
        return rules.get(value) or Expr(
            value.head, *tuple(replace_core(elem, rules) for elem in value.args)
        )
    return rules.get(value) or rules.get(Expr(Operator.NONCOMMUTE, value)) or value


def replace(expr: Numeric | Numerical, rules: dict) -> Numeric | Numerical:
    return evaluate(replace_core(expr, rules))
