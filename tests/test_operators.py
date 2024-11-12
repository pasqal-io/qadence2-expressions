from __future__ import annotations

import pytest
from typing import Callable

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


@pytest.mark.parametrize("operator", [CZ, H, X, Y, Z, NOT, SWAP])
def test_idempotency_unitary_hermitian_operators(operator: Callable) -> None:
    assert operator() * operator() == value(1)


@pytest.mark.parametrize("operator", [CZ, H, X, Y, Z, NOT, SWAP])
def test_power_unitary_hermitian_operators(operator: Callable) -> None:
    assert operator() ** 2 == value(1)
    assert operator() ** 3 == operator()


def test_parametric_opertor() -> None:
    theta = variable("theta")
    assert RX(theta / 2)() * RX(theta / 2)() == RX(theta)()
