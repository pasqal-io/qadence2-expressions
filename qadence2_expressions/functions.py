from __future__ import annotations

from qadence2_expressions import (
    Expression,
    function,
    promote,
    Numeric,
)


def sin(x: Expression | Numeric) -> Expression:
    return function("sin", promote(x))


def cos(x: Expression | Numeric) -> Expression:
    return function("cos", promote(x))


# Exponential function as power.
def exp(x: Expression | Numeric) -> Expression:
    return Expression.symbol("E") ** promote(x)


def log(x: Expression | Numeric) -> Expression:
    expr = function("log", promote(x))
    # Logarithms of operators are also operators and need to be arranged as such.
    return expr.as_quantum_operator()


# Using square root as power makes symbolic simplifications easier.
def sqrt(x: Expression | Numeric) -> Expression:
    return promote(x) ** 0.5
