from __future__ import annotations

import unittest

from qadence2_expressions.expr.expr2 import (
    Expression,
    Support,
    value,
    symbol,
    unitary_hermitian_operator,
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
        X = unitary_hermitian_operator("X")

        self.assertEqual(value(1).subspace(), None)
        self.assertEqual(a.subspace(), None)
        self.assertEqual(X().subspace(), Support())
        self.assertEqual(X(1).subspace(), Support(1))
        self.assertEqual(X(1, 2).subspace(), Support(1, 2))
        self.assertEqual(
            X(target=(1,), control=(0,)).subspace(),
            Support(control=(0,), target=(1,)),
        )

        expr = Expression.add(value(1), a)
        self.assertEqual(expr.subspace(), None)

        term1 = Expression.mul(a, X(1))
        term2 = Expression.mul(b, X(2))
        expr = Expression.add(term1, term2)
        self.assertEqual(expr.subspace(), Support(1, 2))


    def test_kron_insert(self) -> None:
        X = unitary_hermitian_operator("X")
        term = Expression.kron(X(1), X(2), X(4))

        self.assertEqual(term.__insertr__(X(3)), Expression.kron(X(1), X(2), X(3), X(4)))
        self.assertEqual(term.__insertl__(X(3)), Expression.kron(X(1), X(2), X(3), X(4)))
   
    def test_kron_join(self) -> None:
        X = unitary_hermitian_operator("X")
        term1 = Expression.kron(X(1), X(4))
        term2 = Expression.kron(X(2), X(3))
        
        self.assertEqual(term1.__kron_join__(term2), Expression.kron(X(1), X(2), X(3), X(4)))
        self.assertEqual(term2.__kron_join__(term1), Expression.kron(X(1), X(2), X(3), X(4)))
  
    def test_kron(self) -> None:
        X = unitary_hermitian_operator("X")

        self.assertEqual(
            X(1).__kron__(X(4)).__kron__(X(3)).__kron__(X(2)),
            Expression.kron(X(1), X(2), X(3), X(4))
        )
