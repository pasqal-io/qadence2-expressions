from __future__ import annotations

from qadence2_expressions import (
    CZ,
    H,
    NOT,
    RX,
    SWAP,
    X,
    Y,
    Z,
    value,
    variable,
)


def test_unitary_hermitian_operators() -> None:
    assert H() * H() == value(1)
    assert X() * X() == value(1)
    assert Y() * Y() == value(1)
    assert Z() * Z() == value(1)
    assert CZ() * CZ() == value(1)
    assert NOT() * NOT() == value(1)
    assert SWAP() * SWAP() == value(1)


def test_parametric_opertor() -> None:
    theta = variable("theta")
    assert RX(theta / 2)() * RX(theta / 2)() == RX(theta)()
