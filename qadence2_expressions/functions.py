from __future__ import annotations

from .constructors import function, value
from .expression import Expression


def sin(x: Expression | complex | float | int) -> Expression:
    if not isinstance(x, Expression):
        x = value(x)
    return function("sin", x)


def cos(x: Expression | complex | float | int) -> Expression:
    if not isinstance(x, Expression):
        x = value(x)
    return function("cos", x)


# Exponential function as power.
def exp(x: Expression | complex | float | int) -> Expression:
    return Expression.symbol("E") ** x


def log(x: Expression | complex | float | int) -> Expression:
    if not isinstance(x, Expression):
        x = value(x)
    return function("log", x)
