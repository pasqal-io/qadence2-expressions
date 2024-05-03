from __future__ import annotations

from ..expr import Expr, Numeric, Numerical, Operator


def sin(x: Numeric | Numerical) -> Numeric | Numerical:
    return Expr(Operator.CALL, sin.__name__, x)


def cos(x: Numeric | Numerical) -> Numeric | Numerical:
    return Expr(Operator.CALL, cos.__name__, x)


def exp(x: Numeric | Numerical) -> Numeric | Numerical:
    return Expr(Operator.CALL, exp.__name__, x)


def log(x: Numeric | Numerical) -> Numeric | Numerical:
    return Expr(Operator.CALL, log.__name__, x)
