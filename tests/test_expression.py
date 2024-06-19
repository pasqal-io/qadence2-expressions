from __future__ import annotations

from qadence2_expressions import Symbol
from qadence2_expressions.expr import Expr, Operator


def test_symbol_arithimetic() -> None:
    a = Symbol("a")

    assert a + 0 == a
    assert a + a == 2 * a
    assert a - a == 0

    assert a * 0 == 0
    assert a * 1 == a
    assert a * a == a**2
    assert a / a == 1

    assert a**0 == 1
    assert a**1 == a
    assert 2**a == Expr(Operator.POWER, 2, a)


def test_expression_default_simplifications() -> None:
    a = Symbol("a")
    b = Symbol("b")

    assert (2 * a) * (3 * a) == 6 * a**2
    assert a / (2 * a) == 0.5
    assert (a + b) * (a - b) == a**2 - b**2
    assert (a + b) * (a + b) == a**2 + 2 * a * b + b**2


def test_expression_power_sum_not_expand() -> None:
    a = Symbol("a")
    b = Symbol("b")

    assert (a + b) * (a + b) == a**2 + 2 * a * b + b**2
    assert (a + b) ** 2 != a**2 + 2 * a * b + b**2


def test_expression_power_sum_simplification() -> None:
    a = Symbol("a")
    b = Symbol("b")

    lhs = (a + b) * (a + b) ** 0.5 / (a + b) ** 2
    rhs = (a + b) ** -0.5
    assert lhs == rhs
