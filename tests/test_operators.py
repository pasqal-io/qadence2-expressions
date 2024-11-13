from __future__ import annotations

from typing import List

from qadence2_expressions import (
    RX,
    sqrt,
    value,
    variable,
)


def test_idempotency_unitary_hermitian_operators(unitary_hermitian_operators: List) -> None:
    for operator in unitary_hermitian_operators:
        assert operator() * operator() == value(1)


def test_int_power_unitary_hermitian_operators(unitary_hermitian_operators: List) -> None:
    for operator in unitary_hermitian_operators:
        assert operator() ** 2 == value(1)
        assert operator() ** 3 == operator()


def test_fractional_power_unitary_hermitian_operators(unitary_hermitian_operators: List) -> None:
    for operator in unitary_hermitian_operators:
        # Simplify only acting on same subspace.
        assert sqrt(operator()) * sqrt(operator()) == operator()
        assert sqrt(operator(0)) * sqrt(operator(1)) == sqrt(operator(0)) * sqrt(operator(1))


def test_parametric_opertor() -> None:
    theta = variable("theta")
    assert RX(theta / 2)() * RX(theta / 2)() == RX(theta)()
