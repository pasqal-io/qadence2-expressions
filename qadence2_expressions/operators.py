from __future__ import annotations

from typing import Callable

from .core.constructors import (
    function,
    parametric_operator,
    projector,
    promote,
    unitary_hermitian_operator,
    value,
)
from .core.expression import Expression

# Pauli operators
X = unitary_hermitian_operator("X")
Y = unitary_hermitian_operator("Y")
Z = unitary_hermitian_operator("Z")

# Standard gates
CZ = unitary_hermitian_operator("CZ")

# Logic operators
NOT = unitary_hermitian_operator("NOT")

# Digital operators
SWAP = unitary_hermitian_operator("SWAP")
H = unitary_hermitian_operator("H")  # Hadamard gate

# Default projectors
Z0 = projector("Z", "0")
Z1 = projector("Z", "1")
Xp = projector("X", "+")
Xm = projector("X", "-")


# Rotations
def RX(angle: Expression | float) -> Callable:
    param_op: Callable = parametric_operator("RX", promote(angle), join=_join_rotation)
    return param_op


def RY(angle: Expression | float) -> Callable:
    param_op: Callable = parametric_operator("RY", promote(angle), join=_join_rotation)
    return param_op


def RZ(angle: Expression | float) -> Callable:
    param_op: Callable = parametric_operator("RZ", promote(angle), join=_join_rotation)
    return param_op


def _join_rotation(
    lhs_fn: Expression, rhs_fn: Expression, is_lhs_dagger: bool, is_rhs_dagger: bool
) -> Expression:
    lhs_sign = 1 - 2 * is_lhs_dagger
    rhs_sign = 1 - 2 * is_rhs_dagger

    total_angle = lhs_sign * lhs_fn[1] + rhs_sign * rhs_fn[1]
    if total_angle.is_zero:
        return value(1)
    return function(lhs_fn[0][0], total_angle)


# Analog operations
def NativeDrive(
    duration: Expression | float,
    amplitude: Expression | float,
    detuning: Expression | float,
    phase: Expression | float,
) -> Callable:
    param_op: Callable = parametric_operator(
        "NativeDrive",
        promote(duration),
        promote(amplitude),
        promote(detuning),
        promote(phase),
        instruction_name="dyn_pulse",
    )
    return param_op


def FreeEvolution(duration: Expression | float) -> Callable:
    param_op: Callable = parametric_operator(
        "FreeEvolution", promote(duration), instruction_name="dyn_wait"
    )
    return param_op
