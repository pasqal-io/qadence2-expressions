# This module should be implemented using Hy!!

import numpy as engine  # To be replaced with config and dynamic import.

from ..expr import Expr, Numeric, Numerical, Operator


def sin(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, Numerical):
        return getattr(engine, sin.__name__)(x)
    return Expr(Operator.CALL, sin.__name__, x)


def cos(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, Numerical):
        return getattr(engine, cos.__name__)(x)
    return Expr(Operator.CALL, cos.__name__, x)


def exp(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, Numerical):
        return getattr(engine, exp.__name__)(x)
    return Expr(Operator.CALL, exp.__name__, x)


def log(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, Numerical):
        return getattr(engine, log.__name__)(x)
    return Expr(Operator.CALL, log.__name__, x)
