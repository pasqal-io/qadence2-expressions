from __future__ import annotations

from functools import reduce

from .core.expression import Expression


def collect_operators(polynomial: Expression) -> dict[Expression, Expression]:
    """Collect the coefficients of noncommutative terms in a polynomial expression.

    Example:
    ```
    >>> expr = Z(1) + 2 * Z(1) * Z (2) - X(3)
    >>> collect_operators(expr)
    {Z[1]: 1, Z[1] * Z[2]: 2, Z[3]: -1}
    """
    return _collect_operators_core({}, polynomial)


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
