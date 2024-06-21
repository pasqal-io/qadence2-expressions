from __future__ import annotations

import unittest

from qadence2_expressions.expr.expr2 import (
    Expression,
    ExprType,
    Operator,
    value,
    symbol,
)


class TestExpression(unittest.TestCase):
    def test_value(self) -> None:
        self.assertEqual(value(3), Expression(ExprType.VALUE, 3))
        self.assertEqual(value(-2), Expression(ExprType.VALUE, -2))
        self.assertEqual(value(1j), Expression(ExprType.VALUE, 1j))

    def test_symbol(self) -> None:
        a = symbol("a")
        self.assertEqual(a, Expression(ExprType.SYMBOL, "a"))

    def test_addition_value(self) -> None:
        self.assertEqual(Expression.zero() + 1, value(1))
        self.assertEqual(2 + value(3), value(5))

    def test_addition_symbol(self) -> None:
        a = symbol("a")

        self.assertEqual(0 + a, a)
        self.assertEqual(Expression.zero() + a, a)
        self.assertEqual(1 + a, Expression(Operator.PLUS, value(1), a))

    def test_addition_reduction(self) -> None:
        a = symbol("a")

        self.assertEqual(a + a, Expression(Operator.PLUS, a, a))

    def test_multiplication_value(self) -> None:
        self.assertEqual(0 * value(1), Expression.zero())
        self.assertEqual(1 * value(2), value(2))

    def test_multiplication_symbol(self) -> None:
        a = symbol("a")

        self.assertEqual(0 * a, Expression.zero())
        self.assertEqual(1 * a, a)
        self.assertEqual(-2 * a, Expression(Operator.TIMES, value(-2), a))

    def test_negation(self) -> None:
        a = symbol("a")

        self.assertEqual(-a, Expression(Operator.TIMES, value(-1), a))
        self.assertEqual(-value(2), value(-2))

    def test_subtraction_value(self) -> None:
        self.assertEqual(3 - value(3), value(0))
        self.assertEqual(2 - value(3), value(-1))

    def test_subtraction_symbol(self) -> None:
        a = symbol("a")

        self.assertEqual(0 - a, -a)
        self.assertEqual(a - 0, a)
        self.assertEqual(a - 2, Expression(Operator.PLUS, a, value(-2)))
        self.assertEqual(
            3 - a,
            Expression(
                Operator.PLUS, value(3), Expression(Operator.TIMES, value(-1), a)
            ),
        )

    def test_power_value(self) -> None:
        self.assertEqual(value(2) ** 3, value(8))
        self.assertEqual(2 ** value(4), value(16))
        self.assertEqual((2 ** value(2)) ** value(3), value(64))
        self.assertEqual(2 ** value(2) ** value(3), value(256))

    def test_power_symbol(self) -> None:
        a = symbol("a")
        b = symbol("b")

        self.assertEqual(a**2, Expression(Operator.POWER, a, value(2)))
        self.assertEqual(1j**a, Expression(Operator.POWER, value(1j), a))
        self.assertEqual(a**b, Expression(Operator.POWER, a, b))

    def test_division_value(self) -> None:
        self.assertEqual(3 / value(2), value(1.5))
        self.assertEqual(3 / value(3), value(1))

    def test_division_symbol(self) -> None:
        a = symbol("a")
        b = symbol("b")

        self.assertEqual(2 / a, 2 * a ** -1)
        self.assertEqual(a / value(2), a * 0.5)
        self.assertEqual(a / b, a * b ** -1)
        self.assertEqual(a / a, value(1))


if __name__ == "__main__":
    unittest.main()
