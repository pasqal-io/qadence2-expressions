from __future__ import annotations

from qadence2_expressions import QSymbol
from qadence2_expressions.expr import Expr, Operator


def test_qsymbol_hermitian() -> None:
    X = QSymbol("X")
    Y = QSymbol("Y")

    assert X.is_hermitian
    assert X * X == 1


def test_qsymbol_distinct_subspaces() -> None:
    X = QSymbol("X")
    Y = QSymbol("Y")

    assert X(1) * X(3) * X(2) == Expr(Operator.NONCOMMUTE, X(1), X(2), X(3))
    assert X(1) * Y(3) * X(2) == Expr(Operator.NONCOMMUTE, X(1), X(2), Y(3))


def test_qsymbol_subspace_overlap() -> None:
    X = QSymbol("X")
    Y = QSymbol("Y")

    assert X(1) * Y() * X(1) == Expr(Operator.NONCOMMUTE, X(1), Y(), X(1))
    assert X(1) * Y(1, 2) * X(1) == Expr(Operator.NONCOMMUTE, X(1), Y(1, 2), X(1))
    assert X(1) * Y(3, 2) * X(1) == Expr(Operator.NONCOMMUTE, Y(2, 3))


def test_qsymbol_target_control() -> None:
    NOT = QSymbol("NOT")

    op1 = NOT(control=(1,), target=(2,))
    op2 = NOT(target=(2,), control=(1,))
    op3 = NOT(control=(2,), target=(1,))

    assert op1 * op2 == 1
    assert op1 * op3 == Expr(Operator.NONCOMMUTE, op1, op3)
