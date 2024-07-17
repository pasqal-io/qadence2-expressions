from __future__ import annotations

from typing import Callable

from .constructors import (
    function,
    parametric_operator,
    projector,
    promote,
    unitary_hermitian_operator,
    value,
)
from .expression import Expression


# Pauli operators
X = unitary_hermitian_operator("X")
Y = unitary_hermitian_operator("Y")
Z = unitary_hermitian_operator("Z")

# Logic operators
NOT = unitary_hermitian_operator("NOT")

# Default projectors
Z0 = projector("Z", "0")
Z1 = projector("Z", "1")
Xp = projector("X", "+")
Xm = projector("X", "-")


# Rotations
def RX(angle: Expression | float) -> Callable:
    return parametric_operator("RX", promote(angle), join=_join_rotation)


def RY(angle: Expression | float) -> Callable:
    return parametric_operator("RY", promote(angle), join=_join_rotation)


def RZ(angle: Expression | float) -> Callable:
    return parametric_operator("RZ", promote(angle), join=_join_rotation)


def _join_rotation(lhs: Expression, rhs: Expression) -> Expression:
    total_angle = lhs[1] + rhs[1]
    if total_angle.is_zero:
        return value(1)
    return function(lhs[0], total_angle)


# Analog operations
def NativeDrive(
    duration: Expression | float,
    amplitude: Expression | float,
    detuning: Expression | float,
    phase: Expression | float,
) -> Callable:
    return parametric_operator(
        "NativeDrive",
        promote(duration),
        promote(amplitude),
        promote(detuning),
        promote(phase),
        instruction_name="dyn_pulse",
    )


def FreeEvolution(duration: Expression | float) -> Callable:
    return parametric_operator(
        "FreeEvolution", promote(duration), instruction_name="dyn_wait"
    )
