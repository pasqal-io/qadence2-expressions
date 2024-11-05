from __future__ import annotations

from qadence2_expressions import (
    Expression,
    function,
    promote,
)
from qadence2_expressions.core.utils import Numeric


def sin(x: Expression | Numeric) -> Expression:
    return function("sin", promote(x))


def cos(x: Expression | Numeric) -> Expression:
    return function("cos", promote(x))


# Exponential function as power.
def exp(x: Expression | Numeric) -> Expression:
    return Expression.symbol("E") ** promote(x)


def log(x: Expression | Numeric) -> Expression:
    return function("log", promote(x))
