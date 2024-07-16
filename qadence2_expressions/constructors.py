from __future__ import annotations

from typing import Any, Callable

from .environment import Environment
from .expression import Expression
from .support import Support


def value(x: complex | float | int) -> Expression:
    """Promotes a numerical value to an expression."""
    return Expression.value(x)


def symbol(identifier: str, **attributes: Any) -> Expression:
    if identifier in Environment.protected:
        raise SyntaxError(f"'{identifier}' is protected.")
    return Expression.symbol(identifier, **attributes)


def parameter(name: str) -> Expression:
    return symbol(name)


def variable(name: str) -> Expression:
    return symbol(name, trainable=True)


def time_parameter(name: str) -> Expression:
    return symbol(name, time_parameter=True)


def time_variable(name: str) -> Expression:
    return symbol(name, trainable=True, time_parameter=True)


def array_parameter(name: str, size: int) -> Expression:
    return symbol(name, size=size)


def array_variable(name: str, size: int) -> Expression:
    return symbol(name, trainable=True, size=size)


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
    name: str, *args: Any, join: Callable | None = None, **attributes: Any
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
            **attributes,
        )

    return core
