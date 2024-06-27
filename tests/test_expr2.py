from __future__ import annotations

import unittest

from qadence2_expressions.expr.expr2 import (
    Expression,
    Support,
    value,
    symbol,
    hermitian_operator,
)


class TestExpression(unittest.TestCase):

    def test_consturctor(self) -> None:
        self.assertEqual(Expression.value(1), Expression(Expression.Token.VALUE, 1))
        self.assertEqual(
            Expression.symbol("x"), Expression(Expression.Token.SYMBOL, "x")
        )
        self.assertEqual(
            Expression.function("sin", 3.14),
            Expression(Expression.Token.FN, "sin", 3.14),
        )
        self.assertEqual(
            Expression.quantum_operator(
                Expression.symbol("X"), Support(1), is_hermitian=True
            ),
            Expression(
                Expression.Token.QUANTUM_OP,
                Expression.symbol("X"),
                Support(1),
                is_hermitian=True,
            ),
        )

    def test_subspace_propagation(self) -> None:
        a = symbol("a")
        b = symbol("b")
        X = hermitian_operator("X")

        self.assertEqual(value(1).get_subspace(), None)
        self.assertEqual(a.get_subspace(), None)
        self.assertEqual(X().get_subspace(), Support())
        self.assertEqual(X(1).get_subspace(), Support(1))
        self.assertEqual(X(1, 2).get_subspace(), Support(1, 2))
        self.assertEqual(
            X(target=(1,), control=(0,)).get_subspace(),
            Support(control=(0,), target=(1,)),
        )

        expr = Expression.add(value(1), a)
        self.assertEqual(expr.get_subspace(), None)

        term1 = Expression.mul(a, X(1))
        term2 = Expression.mul(b, X(2))
        expr = Expression.add(term1, term2)
        self.assertEqual(expr.get_subspace(), Support(1, 2))
