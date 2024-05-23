from __future__ import annotations

from qadence2_expressions import QSymbol, Symbol, collect_operators
from qadence2_expressions.expr import Expr, Operator


def test_collect_operators():
    a = Symbol("a")
    X = QSymbol("X")
    Y = QSymbol("Y")

    h1 = X(0)
    assert collect_operators(h1) == {X(0): 1}

    h2 = (X(0) * X(1) - 2 * Y()) / 2
    assert collect_operators(h2) == {Expr(Operator.NONCOMMUTE, Y()): -1, X(0) * X(1): 0.5}


    