from ..expr import Expr, Operator
from .evaluate import evaluate


def replace_core(value, rules: dict):
    if isinstance(value, Expr):
        return rules.get(value) or Expr(
            value.head, *tuple(replace_core(elem, rules) for elem in value.args)
        )
    return rules.get(value) or rules.get(Expr(Operator.NONCOMMUTE, value)) or value


def replace(expr, rules: dict):
    return evaluate(replace_core(expr, rules))
