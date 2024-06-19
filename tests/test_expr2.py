from __future__ import annotations

from qadence2_expressions.expr.expr2 import (
    Expression,
    ExprType,
    Operator,
    value,
    symbol,
)


def test_value() -> None:
    assert value(3) == Expression(ExprType.VALUE, 3)
    assert value(-2) == Expression(ExprType.VALUE, -2)
    assert value(1j) == Expression(ExprType.VALUE, 1j)


def test_symbol() -> None:
    a = symbol("a")
    assert a == Expression(ExprType.SYMBOL, "a")


def test_addition_value() -> None:
    assert Expression.zero() + 1 == value(1)
    assert 2 + value(3) == value(5)


def test_addition_symbol() -> None:
    a = symbol("a")

    assert 0 + a == a
    assert Expression.zero() + a == a
    assert 1 + a == Expression(Operator.PLUS, value(1), a)


def test_addition_reduction() -> None:
    a = symbol("a")

    assert a + a == Expression(Operator.PLUS, a, a)


def test_multiplication_value() -> None:
    assert 0 * value(1) == Expression.zero()
    assert 1 * value(2) == value(2)


def test_multiplication_symbol() -> None:
    a = symbol("a")

    assert 0 * a == Expression.zero()
    assert 1 * a == a
    assert -2 * a == Expression(Operator.TIMES, value(-2), a)


def test_negation() -> None:
    a = symbol("a")

    assert -a == Expression(Operator.TIMES, value(-1), a)
    assert -value(2) == value(-2)


def test_subtraction_value() -> None:
    assert 3 - value(3) == value(0)
    assert 2 - value(3) == value(-1)


def test_subtraction_symbol() -> None:
    a = symbol("a")

    assert 0 - a == -a
    assert a - 0 == a
    assert a - 2 == Expression(Operator.PLUS, a, value(-2))
    assert 3 - a == Expression(
        Operator.PLUS, value(3), Expression(Operator.TIMES, value(-1), a)
    )


def test_power() -> None:
    a = symbol("a")
    b = symbol("b")

    assert value(2) ** 3 == value(8)
    assert 2 ** value(4) == value(16)
    assert a**2 == Expression(Operator.POWER, a, value(2))
    assert 1j**a == Expression(Operator.POWER, value(1j), a)
    assert a**b == Expression(Operator.POWER, a, b)
