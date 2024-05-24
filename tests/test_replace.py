from __future__ import annotations

from qadence2_expressions import QSymbol, Symbol, replace


def test_replace() -> None:
    a = Symbol("a")
    b = Symbol("b")
    X = QSymbol("X")
    Y = QSymbol("Y")
    Z = QSymbol("Z")

    expr0 = 2 * a + b

    # replace symbol by symbol
    expr1 = replace(expr0, {b: a})
    assert expr1 == 3 * a

    # replace symbol by value
    expr2 = replace(expr0, {a: 2, b: -1})
    assert expr2 == 3

    # replace symbol by expression
    expr3 = 2 + a
    expr4 = replace(expr3, {a: a + b})
    expr5 = replace(expr4, {b: a})
    expr6 = 2 * (1 + a)
    assert expr5 == expr6

    expr7 = 2j * Y + X * Z
    expr8 = replace(expr7, {X * Z: -2j * Y})
    assert expr8 == 0
