from __future__ import annotations

import pytest

from typing import Callable

from qadence2_expressions import (
    RX,
    sqrt,
    value,
    variable,
    NativeDrive,
    FreeEvolution,
    PiecewiseDrive,
    array_parameter,
)

## General tests


def test_idempotency_unitary_hermitian_operators(unitary_hermitian_operators: list) -> None:
    for operator in unitary_hermitian_operators:
        assert operator() * operator() == value(1)


def test_int_power_unitary_hermitian_operators(unitary_hermitian_operators: list) -> None:
    for operator in unitary_hermitian_operators:
        assert operator() ** 2 == value(1)
        assert operator() ** 3 == operator()


def test_fractional_power_unitary_hermitian_operators(unitary_hermitian_operators: list) -> None:
    for operator in unitary_hermitian_operators:
        # Simplify only acting on same subspace.
        assert sqrt(operator()) * sqrt(operator()) == operator()
        assert sqrt(operator(0)) * sqrt(operator(1)) == sqrt(operator(0)) * sqrt(operator(1))


def test_parametric_operator() -> None:
    theta = variable("theta")
    assert RX(theta / 2)() * RX(theta / 2)() == RX(theta)()


## Analog Operators


def test_native_drive() -> None:
    drive = NativeDrive(1.0, 1.0, 1.0, 0.0)
    assert drive().is_quantum_operator


@pytest.mark.parametrize("sizes", [(2, 3, 3), (1, 3, 3), (2, 3, 4)])
def test_piecewise_drive(sizes: tuple) -> None:

    def _get_drive(dur_size: int, amp_size: int, det_size: int) -> Callable:
        return PiecewiseDrive(
            array_parameter("duration", size=dur_size),
            array_parameter("amplitude", size=amp_size),
            array_parameter("detuning", size=det_size),
        )

    match sizes:
        case (2, 3, 3):
            drive = _get_drive(*sizes)
            assert drive().is_quantum_operator
        case (1, 3, 3) | (2, 3, 4):
            with pytest.raises(ValueError):
                drive = _get_drive(*sizes)


def test_analog_operator_combination() -> None:
    fe = FreeEvolution(1.0)

    nd = NativeDrive(1.0, 1.0, 1.0, 0.0)

    pd = PiecewiseDrive(
        array_parameter("duration", size=2),
        array_parameter("amplitude", size=3),
        array_parameter("detuning", size=3),
    )
    expr = fe() * nd(1, 2) * pd()

    assert expr.is_kronecker_product
