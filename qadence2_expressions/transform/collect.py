from __future__ import annotations

from ..expr import Expr, Operator, QSymbol


def collect_operators(expr: object) -> dict:
    """Collect the coefficients of noncommutative expression, e.g.

    Z(1) + 2 * Z(1) * Z (2) - X(3)  --> {Z(1): 1, Z(1) * Z (2): 2, Z(3): -1}
    """

    acc: dict = dict()
    collect_operators_core(expr, acc)
    return acc


def collect_operators_core(expr: object, acc: dict) -> None:
    if isinstance(expr, QSymbol):
        acc[expr] = acc.get(expr, 0) + 1

    if isinstance(expr, Expr) and expr.head == Operator.NONCOMMUTE:
        acc[expr] = acc.get(expr, 0) + 1

    if (
        isinstance(expr, Expr)
        and expr.head == Operator.TIMES
        and isinstance(expr.args[-1], Expr)
        and expr.args[-1].head == Operator.NONCOMMUTE
    ):
        key = expr.args[-1]
        value = expr.args[0] if len(expr.args[:-1]) == 1 else Expr(Operator.TIMES, *expr.args[:-1])
        acc[key] = acc.get(key, 0) + value

    if isinstance(expr, Expr) and expr.head == Operator.PLUS:
        for arg in expr.args:
            collect_operators_core(arg, acc)
