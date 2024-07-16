from __future__ import annotations

import unittest

from qadence2_expressions.constructors import (
    symbol,
    unitary_hermitian_operator,
    value,
)
from qadence2_expressions.expression import Expression
from qadence2_expressions.support import Support


class TestExpression(unittest.TestCase):
    def test_consturctor(self) -> None:
        self.assertEqual(value(1), Expression(Expression.Tag.VALUE, 1))
        self.assertEqual(Expression.symbol("x"), Expression(Expression.Tag.SYMBOL, "x"))
        self.assertEqual(
            Expression.function("sin", 3.14),
            Expression(Expression.Tag.FN, Expression.symbol("sin"), 3.14),
        )
        self.assertEqual(
            Expression.quantum_operator(
                Expression.symbol("X"), Support(1), is_hermitian=True
            ),
            Expression(
                Expression.Tag.QUANTUM_OP,
                Expression.symbol("X"),
                Support(1),
                is_hermitian=True,
            ),
        )

    def test_addition(self) -> None:
        a = symbol("a")
        X = unitary_hermitian_operator("X")

        self.assertEqual(value(2) + 3, value(5))
        self.assertEqual(a + 0, a)
        self.assertEqual(0 + a, a)
        self.assertEqual(a + 2, Expression.add(value(2), a))
        self.assertEqual(a + a, Expression.mul(value(2), a))
        self.assertEqual(X() + 2 + a, Expression.add(value(2), a, X()))

    def test_negation(self) -> None:
        a = symbol("a")
        X = unitary_hermitian_operator("X")

        self.assertEqual(-value(2), value(-2))
        self.assertEqual(-a, Expression.mul(value(-1), a))
        self.assertEqual(-X(1), Expression.mul(value(-1), X(1)))
        self.assertEqual(
            -X(2) * X(1), Expression.mul(value(-1), Expression.kron(X(1), X(2)))
        )

    def test_subtractions(self) -> None:
        a = symbol("a")
        X = unitary_hermitian_operator("X")

        self.assertEqual(value(2) - value(3), value(-1))
        self.assertEqual(a - 2, Expression.add(value(-2), a))
        self.assertEqual(2 - a, Expression.add(value(2), Expression.mul(value(-1), a)))
        self.assertEqual(a - a, value(0))
        self.assertEqual(X(1) - X(1), value(0))

    def test_multiplication(self) -> None:
        a = symbol("a")
        X = unitary_hermitian_operator("X")

        self.assertEqual(3 * value(2), value(6))
        self.assertEqual(a * 2, Expression.mul(value(2), a))
        self.assertEqual(X(1) * a * 2, Expression.mul(value(2), a, X(1)))
        self.assertEqual(
            X(1) * a * X(2) * 2,
            Expression.mul(value(2), a, Expression.kron(X(1), X(2))),
        )

    def test_power(self) -> None:
        a = symbol("a")

        self.assertEqual(value(2) ** 3, value(8))
        self.assertEqual(a**0, Expression.one())
        self.assertEqual(a**1, a)
        self.assertEqual(a**2, Expression.pow(a, value(2)))
        self.assertEqual(2**a, Expression.pow(value(2), a))

    def test_division(self) -> None:
        a = symbol("a")

        self.assertEqual(3 / value(2), value(1.5))
        self.assertEqual(1 / a, Expression.pow(a, value(-1)))
        self.assertEqual(a / a, value(1))
        self.assertEqual(a / 2, Expression.mul(value(0.5), a))

    def test_kron(self) -> None:
        X = unitary_hermitian_operator("X")
        term = Expression.kron(X(1), X(2), X(4))

        # Push term from the right.
        self.assertEqual(term.__kron__(X(3)), Expression.kron(X(1), X(2), X(3), X(4)))

        # Push term from the left.
        self.assertEqual(X(3).__kron__(term), Expression.kron(X(1), X(2), X(3), X(4)))

        # Join `kron` expressions.
        term1 = Expression.kron(X(1), X(4))
        term2 = Expression.kron(X(2), X(3))

        self.assertEqual(term1.__kron__(term2), Expression.kron(X(1), X(2), X(3), X(4)))
        self.assertEqual(term2.__kron__(term1), Expression.kron(X(1), X(2), X(3), X(4)))

    def test_commutativity(self) -> None:
        a = symbol("a")
        b = symbol("b")
        X = unitary_hermitian_operator("X")
        Y = unitary_hermitian_operator("Y")

        self.assertEqual(a * b - b * a, value(0))
        self.assertEqual(
            X(1) * Y(1) - Y(1) * X(1),
            Expression.add(
                Expression.kron(X(1), Y(1)),
                Expression.mul(value(-1), Expression.kron(Y(1), X(1))),
            ),
        )
        self.assertEqual(X(1) * Y(2) - Y(2) * X(1), value(0))

    def test_operators_multiplication(self) -> None:
        X = unitary_hermitian_operator("X")
        Y = unitary_hermitian_operator("Y")

        self.assertEqual(X() * X(), value(1))
        self.assertEqual(X(1) * X(1), value(1))
        self.assertEqual(X(1) * Y(2) * X(1), Y(2))
        self.assertEqual((X(1) * Y(2)) * (X(1) * Y(2)), value(1))

    def test_subspace_propagation(self) -> None:
        a = symbol("a")
        b = symbol("b")
        X = unitary_hermitian_operator("X")

        self.assertEqual(value(1).subspace, None)
        self.assertEqual(a.subspace, None)
        self.assertEqual(X().subspace, Support())
        self.assertEqual(X(1).subspace, Support(1))
        self.assertEqual(X(1, 2).subspace, Support(1, 2))
        self.assertEqual(
            X(target=(1,), control=(0,)).subspace,
            Support(control=(0,), target=(1,)),
        )

        expr = Expression.add(value(1), a)
        self.assertEqual(expr.subspace, None)

        term1 = Expression.mul(a, X(1))
        term2 = Expression.mul(b, X(2))
        expr = Expression.add(term1, term2)
        self.assertEqual(expr.subspace, Support(1, 2))
