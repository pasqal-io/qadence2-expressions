from __future__ import annotations

from qadence2_expressions import QSymbol, Symbol, collect_operators
from qadence2_expressions.core import Expr, Operator


def test_collect_single_operator() -> None:
    X = QSymbol("X")
    h = X(0)
    assert collect_operators(h) == {X(0): 1}


def test_collect_multiple_operators() -> None:
    a = Symbol("a")
    X = QSymbol("X")
    Y = QSymbol("Y")

    h = (a * X(0) * X(1) - 2 * Y()) / 2

    assert collect_operators(h) == {
        Expr(Operator.NONCOMMUTE, Y()): -1,
        X(0) * X(1): a * 0.5,
    }
