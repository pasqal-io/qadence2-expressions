from __future__ import annotations

from qadence2_expressions import (
    X,
    Y,
    Z,
    parameter,
    replace,
    value,
)


def test_replace_symbol_by_symbol() -> None:
    a = parameter("a")
    b = parameter("b")

    expr0 = 2 * a + b
    expr1 = replace(expr0, {b: a})
    assert expr1 == 3 * a


def test_replace_symbol_by_valuel() -> None:
    a = parameter("a")
    b = parameter("b")

    expr0 = 2 * a + b
    expr1 = replace(expr0, {a: value(2), b: value(-1)})
    assert expr1 == value(3)


def test_replace_symbol_by_expression() -> None:
    a = parameter("a")
    b = parameter("b")

    expr0 = 2 + a
    expr1 = replace(expr0, {a: a + b})
    expr2 = replace(expr1, {b: a})
    expr3 = 2 * (1 + a)
    assert expr2 == expr3


def test_replace_expression_by_expression() -> None:
    expr0 = 2j * Y() + X() * Z()
    expr1 = replace(expr0, {X() * Z(): -2j * Y()})
    assert expr1 == value(0)
