from __future__ import annotations

from typing import Any, Callable, Literal

from .expression import Expression
from .support import Support


class Environment:
    protected: set[str] = {"E"}
    qubit_positions: list[tuple[int, int]] | None = None
    grid_type: Literal["linear", "square", "triangular"] | None = None
    grid_scale: float = 1.0


def set_qubits_positions(pos: list[tuple[int, int]]) -> None:
    Environment.qubit_positions = pos


def get_qubits_positions() -> list[tuple[int, int]] | None:
    return Environment.qubit_positions


def set_grid_type(grid: Literal["linear", "square", "triangular"]) -> None:
    Environment.grid_type = grid


def get_grid_type() -> Literal["linear", "square", "triangular"] | None:
    return Environment.grid_type


def set_grid_scale(s: float) -> None:
    Environment.grid_scale = s


def get_grid_scale() -> float:
    return Environment.grid_scale


def value(x: complex | float | int) -> Expression:
    """Promotes a numerical value to an expression."""
    return Expression.value(x)


def symbol(identifier: str, **attributes: Any) -> Expression:
    if identifier in Environment.protected:
        raise SyntaxError(f"'{identifier}' is protected.")
    return Expression.symbol(identifier, **attributes)


def function(name: str, *args: Any) -> Expression:
    """Symbolic representation of function where `name` is the name of the function
    and the remaining arguments as the function arguments."""
    return Expression.function(name, *args)


def unitary_hermitian_operator(name: str) -> Callable:
    """
    An unitary Hermitian operator is a function that takes a list of indices (or a
    target and control tuples) and return an Expression with the following property:

        > A = hermitian_operator("A")
        > A(i) * A(i)
        1
        > A(i) * A(j)  ; for i≠j
        A(i) * A(j)
    """

    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        return Expression.quantum_operator(
            Expression.symbol(name),
            Support(*indices, target=target, control=control),
            is_hermitian=True,
            is_unitary=True,
        )

    return core


def projector(base: str, index: str) -> Callable:
    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        return Expression.quantum_operator(
            symbol(f"{base}{{{index}}}"),
            Support(*indices, target=target, control=control),
            base=base,
            is_projector=True,
            is_hermitian=True,
        )

    return core


def parametric_operator(
    name: str, *args: Any, join: Callable | None = None
) -> Callable:
    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        return Expression.quantum_operator(
            function(name, *args),
            Support(*indices, target=target, control=control),
            join=join,
        )

    return core


# Exponential function as power.
def exp(x: Expression | complex | float | int) -> Expression:
    return Expression.symbol("E") ** x


# Pauli operators
X = unitary_hermitian_operator("X")
Y = unitary_hermitian_operator("Y")
Z = unitary_hermitian_operator("Z")

# Default projectors
Z0 = projector("Z", "0")
Z1 = projector("Z", "1")
Xp = projector("X", "+")
Xm = projector("X", "-")


# Rotations
def RX(angle: Expression | float) -> Callable:
    if isinstance(angle, float):
        angle = value(angle)
    return parametric_operator("RX", angle, join=_join_rotation)


def RY(angle: Expression | float) -> Callable:
    if isinstance(angle, float):
        angle = value(angle)
    return parametric_operator("RY", angle, join=_join_rotation)


def RZ(angle: Expression | float) -> Callable:
    if isinstance(angle, float):
        angle = value(angle)
    return parametric_operator("RZ", angle, join=_join_rotation)


def _join_rotation(lhs: Expression, rhs: Expression) -> Expression:
    total_angle = lhs[1] + rhs[1]
    if total_angle.is_zero:
        return value(1)
    return function(lhs[0], total_angle)


def sin(x: Expression | complex | float | int) -> Expression:
    if not isinstance(x, Expression):
        x = value(x)
    return function("sin", x)


def cos(x: Expression | complex | float | int) -> Expression:
    if not isinstance(x, Expression):
        x = value(x)
    return function("cos", x)
