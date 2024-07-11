from __future__ import annotations

from typing import Any, Callable

from .expression import Expression
from .support import Support


class Environmet:
    protected: set[str] = {"e"}


def value(x: complex | float | int) -> Expression:
    """Promotes a numerical value to an expression."""
    return Expression.value(x)


def exp(x: Expression | complex | float | int) -> Expression:
    return Expression.symbol("e") ** x


def symbol(identifier: str, **attributes: Any) -> Expression:
    if identifier in Environmet.protected:
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
            Expression.symbol(f"{base}{{{index}}}"),
            Support(*indices, target=target, control=control),
            base=base,
            is_projector=True,
            is_hermitian=True,
        )

    return core


def parametric_operator(name: str, join: Callable) -> Callable:
    def wrapper(*args) -> Callable:
        def core(support: Support) -> Expression:
            return Expression.quantum_operator(
                Expression.function(name, *args),
                support,
                join=join
            )
        return core
    return wrapper


# Pauli operators
X = unitary_hermitian_operator("X")
Y = unitary_hermitian_operator("Y")
Z = unitary_hermitian_operator("Z")

# Default projectors
Z0 = projector("Z", "0")
Z1 = projector("Z", "1")
Xp = projector("X", "+")
Xm = projector("X", "-")
