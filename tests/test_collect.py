from __future__ import annotations

from qadence2_expressions import (
    X,
    Y,
    collect_operators,
    parameter,
    value,
)


def test_collect_single_operator() -> None:
    h = X(0)
    assert collect_operators(h) == {X(0): value(1)}


def test_collect_multiple_operators() -> None:
    a = parameter("a")

    h = (a * X(0) * X(1) - 2 * Y()) / 2

    assert collect_operators(h) == {
        Y(): value(-1),
        X(0) * X(1): a * 0.5,
    }
