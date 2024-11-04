from __future__ import annotations

from qadence2_expressions import (
    Expression,
    function,
    promote,
)


def sin(x: Expression | complex | float | int) -> Expression:
    return function("sin", promote(x))


def cos(x: Expression | complex | float | int) -> Expression:
    return function("cos", promote(x))


# Exponential function as power.
def exp(x: Expression | complex | float | int) -> Expression:
    return Expression.symbol("E") ** promote(x)


def log(x: Expression | complex | float | int) -> Expression:
    expr = function("log", promote(x))
    # Logarithms of operators are also operators and need to be arranged as such.
    return expr.as_quantum_operator()


# Using square root as power makes symbolic simplifications easier.
def sqrt(x: Expression | complex | float | int) -> Expression:
    return promote(x) ** 0.5
