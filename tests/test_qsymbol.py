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

    # Controlled support
    NOT = QSymbol("NOT")

    op1 = NOT(control=(1,), target=(2,))
    op2 = NOT(target=(2,), control=(1,))
    op3 = NOT(control=(2,), target=(1,))

    assert op1 * op2 == 1
    assert op1 * op3 == Expr(Operator.NONCOMMUTE, op1, op3)
