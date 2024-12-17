from __future__ import annotations

import pytest

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


def test_piecewise_drive() -> None:
    drive = PiecewiseDrive(
        array_parameter("duration", size=2),
        array_parameter("amplitude", size=3),
        array_parameter("detuning", size=3),
    )
    assert drive().is_quantum_operator


def test_piecewise_drive_validation() -> None:
    # N duration requires N+1 amplitude and detuning
    with pytest.raises(ValueError):
        drive = PiecewiseDrive(
            array_parameter("duration", size=1),
            array_parameter("amplitude", size=3),
            array_parameter("detuning", size=3),
        )

    # Amplitude and detuning must be equal
    with pytest.raises(ValueError):
        drive = PiecewiseDrive(
            array_parameter("duration", size=2),
            array_parameter("amplitude", size=3),
            array_parameter("detuning", size=4),
        )


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
