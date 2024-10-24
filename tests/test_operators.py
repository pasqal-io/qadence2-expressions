from __future__ import annotations

from qadence2_expressions import (
    RX,
    variable,
)


def test_parametric_opertor() -> None:
    theta = variable("theta")
    assert RX(theta / 2)() * RX(theta / 2)() == RX(theta)()
