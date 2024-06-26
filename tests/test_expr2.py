from __future__ import annotations

import unittest

from qadence2_expressions.expr.expr2 import (
    Expression,
    hermitian_operator,
    symbol,
    value,
)


class TestExpression(unittest.TestCase):
    # == Tests with regular symbols and values. ==

    def test_value(self) -> None:
        self.assertEqual(value(3), Expression.value(3))
        self.assertEqual(value(-2), Expression.value(-2))
        self.assertEqual(value(1j), Expression.value(1j))

    def test_symbol(self) -> None:
        a = symbol("a")
        self.assertEqual(a, Expression.symbol("a"))

    def test_addition_value(self) -> None:
        self.assertEqual(Expression.zero() + 1, value(1))
        self.assertEqual(2 + value(3), value(5))

    def test_addition_symbol(self) -> None:
        a = symbol("a")

        self.assertEqual(0 + a, a)
        self.assertEqual(Expression.zero() + a, a)
        self.assertEqual(1 + a, Expression.add(value(1), a))

    def test_multiplication_value(self) -> None:
        self.assertEqual(0 * value(1), Expression.zero())
        self.assertEqual(1 * value(2), value(2))

    def test_multiplication_symbol(self) -> None:
        a = symbol("a")

        self.assertEqual(0 * a, Expression.zero())
        self.assertEqual(1 * a, a)
        self.assertEqual(-2 * a, Expression.mul(value(-2), a))

    def test_multiplication_reduction(self) -> None:
        a = symbol("a")
        b = symbol("b")

        self.assertEqual(a * a, a**2)
        self.assertEqual(a * b * a, a**2 * b)

    def test_negation(self) -> None:
        a = symbol("a")

        self.assertEqual(-a, Expression.mul(value(-1), a))
        self.assertEqual(-value(2), value(-2))

    def test_subtraction_value(self) -> None:
        self.assertEqual(3 - value(3), value(0))
        self.assertEqual(2 - value(3), value(-1))

    def test_subtraction_symbol(self) -> None:
        a = symbol("a")

        self.assertEqual(0 - a, -a)
        self.assertEqual(a - 0, a)
        self.assertEqual(a - 2, Expression.add(a, value(-2)))
        self.assertEqual(
            3 - a,
            Expression.add(value(3), Expression.mul(value(-1), a)),
        )

    def test_power_value(self) -> None:
        self.assertEqual(value(2) ** 3, value(8))
        self.assertEqual(2 ** value(4), value(16))
        self.assertEqual((2 ** value(2)) ** value(3), value(64))
        self.assertEqual(2 ** value(2) ** value(3), value(256))

    def test_power_symbol(self) -> None:
        a = symbol("a")
        b = symbol("b")

        self.assertEqual(a**0, value(1))
        self.assertEqual(a**1, a)
        self.assertEqual(a**2, Expression.pow(a, value(2)))
        self.assertEqual(1j**a, Expression.pow(value(1j), a))
        self.assertEqual(a**b, Expression.pow(a, b))

    def test_division_value(self) -> None:
        self.assertEqual(3 / value(2), value(1.5))
        self.assertEqual(3 / value(3), value(1))

    def test_division_symbol(self) -> None:
        a = symbol("a")
        b = symbol("b")

        self.assertEqual(2 / a, 2 * a**-1)
        self.assertEqual(a / value(2), a * 0.5)
        self.assertEqual(a / b, a * b**-1)
        self.assertEqual(a / a, value(1))

    def test_commutativity(self) -> None:
        a = symbol("a")
        b = symbol("b")

        self.assertEqual(a * b + b * a, 2 * a * b)
        self.assertEqual(a * b - b * a, value(0))

    # == Tests with quantum operator and parametric quantum operators. ==

    def test_addition_hermitian_operator(self) -> None:
        X = hermitian_operator("X")

        self.assertEqual(X() + X(), Expression.mul(value(2), X()))
        self.assertEqual(X(1) + X(2), Expression.add(X(1), X(2)))

    def test_multiplication_hermitian_operator(self) -> None:
        X = hermitian_operator("X")
        Y = hermitian_operator("Y")

        # Non-commutative
        self.assertEqual(X() * Y(), Expression.kron(X(), Y()))
        self.assertEqual(Y() * X(), Expression.kron(Y(), X()))

        # Unitary
        self.assertEqual(X(1) * X(1), value(1))

        # Operators must be ordered by support.
        self.assertEqual(X(1) * X(2), Expression.kron(X(1), X(2)))
        self.assertEqual(X(2) * X(1), Expression.kron(X(1), X(2)))

        # However, possition must be preserved when there is overlaps.
        self.assertEqual(X(2) * X(1, 2), Expression.kron(X(2), X(1, 2)))

        # Hermitian property.
        self.assertEqual(X(1) * Y(2) * X(1), Y(2))
        self.assertEqual((X(1) * Y(2)) * (X(1) * Y(2)), value(1))


if __name__ == "__main__":
    unittest.main()
