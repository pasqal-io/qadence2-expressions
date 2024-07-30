from __future__ import annotations

from functools import reduce

from .expression import Expression


def collect_operators(expr: Expression) -> dict[Expression, Expression]:
    """Collect the coefficients of noncommutative expression, e.g.

    Z(1) + 2 * Z(1) * Z (2) - X(3)  --> {Z(1): 1, Z(1) * Z (2): 2, Z(3): -1}
    """
    return _collect_operators_core({}, expr)


def _collect_operators_core(
    acc: dict[Expression, Expression], expr: Expression
) -> dict[Expression, Expression]:
    if expr.is_addition:
        return reduce(_collect_operators_core, expr.args, acc)

    if expr.is_quantum_operator or expr.is_kronecker_product:
        acc[expr] = acc.get(expr, Expression.zero()) + Expression.one()

    elif expr.is_multiplication and (expr[-1].is_quantum_operator or expr[-1].is_kronecker_product):
        coef = expr[0] if len(expr.args) == 2 else Expression.mul(*expr[:-1])
        term = expr[-1]
        acc[term] = acc.get(expr, Expression.zero()) + coef

    return acc
