from __future__ import annotations

from .constructors import function, promote
from .expression import Expression


def sin(x: Expression | complex | float | int) -> Expression:
    return function("sin", promote(x))


def cos(x: Expression | complex | float | int) -> Expression:
    return function("cos", promote(x))


# Exponential function as power.
def exp(x: Expression | complex | float | int) -> Expression:
    return Expression.symbol("E") ** promote(x)


def log(x: Expression | complex | float | int) -> Expression:
    return function("log", promote(x))
