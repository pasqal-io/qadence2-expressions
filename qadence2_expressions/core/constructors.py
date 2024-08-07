from __future__ import annotations

from typing import Any, Callable

from .environment import Environment
from .expression import Expression
from .support import Support


def value(x: complex | float | int) -> Expression:
    """Create a numerical expression from a value."""
    return Expression.value(x)


def promote(x: Expression | complex | float | int) -> Expression:
    """Promotes a numerical value to an expression."""

    if not isinstance(x, Expression):
        return value(x)
    return x


def symbol(identifier: str, **attributes: Any) -> Expression:
    """Create a new symbol from the `identfier` if it is not protected."""

    if identifier in Environment.protected:
        raise SyntaxError(f"'{identifier}' is protected.")
    return Expression.symbol(identifier, **attributes)


def parameter(name: str) -> Expression:
    """A non-trainable input."""

    return symbol(name)


def variable(name: str) -> Expression:
    """A trainable input."""

    return symbol(name, trainable=True)


def time_parameter(name: str) -> Expression:
    """A non-trainble parameter flagged as `time_paramater`.

    Some backends requires extra indications when a paremeter is used as time unit.
    """

    return symbol(name, time_parameter=True)


def time_variable(name: str) -> Expression:
    """A trainble parameter flagged as `time_paramater`.

    Some backends requires extra indications when a paremeter is used as time unit.
    """

    return symbol(name, trainable=True, time_parameter=True)


def array_parameter(name: str, size: int) -> Expression:
    """A non-trainable list of inputs."""

    return symbol(name, size=size)


def array_variable(name: str, size: int) -> Expression:
    """A non-trainable list of inputs."""

    return symbol(name, trainable=True, size=size)


def function(name: str, *args: Any) -> Expression:
    """Symbolic representation of function where `name` is the name of the function and the
    remaining arguments as the function arguments.
    """

    return Expression.function(name, *args)


def unitary_hermitian_operator(name: str) -> Callable:
    """An unitary Hermitian operator is a function that takes a list of indices (or a target and
    control tuples) and return an Expression with the following property:

        > A = unitary_hermitian_operator("A")
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
    """A projector is a function that takes a list of indices (or a target and control tuples) and
    return an Expression with the orthogonality property.

    >>> P0 = projector("Z", "0")
    >>> P1 = projector("Z", "1")
    >>> P0 * P0
    P0
    >>> P0 * P1
    0
    """

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
    """A parametric operator is takes a list of posistional arguments and an generates a function
    that takes a list of indices (or a target and control tuples) and return an Expression.

    The `join` function is used to comabine the argumens of two parameteric operator of the same
    kind when they act on the same qubits.
    """

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
