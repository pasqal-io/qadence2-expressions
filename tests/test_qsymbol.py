from __future__ import annotations

from typing import Any

from qadence2_expressions import QSymbol, Symbol, cos, sin
from qadence2_expressions.expr import Expr, Operator


def test_qsymbol_basics() -> None:
    X = QSymbol("X")
    Y = QSymbol("Y")

    # Hermitian property
    assert X.is_hermitian
    assert X * X == 1

    # Different subspaces
    assert X(1) * X(3) * X(2) == Expr(Operator.NONCOMMUTE, X(1), X(2), X(3))
    assert X(1) * Y(3) * X(2) == Expr(Operator.NONCOMMUTE, X(1), X(2), Y(3))

    # Same subspaces
    assert X(1) * Y(2) * X(1) == Expr(Operator.NONCOMMUTE, Y(2))

    # Subspace overlap
    assert X(1) * Y(1, 2) * X(1) == Expr(Operator.NONCOMMUTE, X(1), Y(1, 2), X(1))

    # Ordered support
    CNOT = QSymbol("CNOT", ordered_support=True)
    assert CNOT(1, 2) * CNOT(1, 2) == 1
    assert CNOT(1, 2) * CNOT(2, 1) == Expr(Operator.NONCOMMUTE, CNOT(1, 2), CNOT(2, 1))

    # Non Hermitian symbol
    def RX(theta: Any) -> QSymbol:
        return QSymbol("RX", theta, is_hermitian=False)

    assert RX(2) * RX(1) == Expr(Operator.NONCOMMUTE, RX(3))
    assert RX(1) * RX(1).dag == 1


def test_qsymbol_expr() -> None:
    a = Symbol("a")
    X = QSymbol("X")
    Y = QSymbol("Y")

    def RX(theta: Any) -> QSymbol:
        return QSymbol("RX", theta, is_hermitian=False)

    expr1 = 2 * RX(a)(0) + 1j * Y(3)
    expr2 = 2 * RX(a)(0).dag - 1j * Y(3)
    assert expr1.dag == expr2  # type: ignore

    expr3 = X * (cos(a) * X + 1j * sin(a) * Y) / 2
    expr4 = 0.5 * cos(a) + 0.5j * sin(a) * X * Y
    assert expr3 == expr4
