from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from .environment import Environment
from .expression import Expression
from .support import Support
from .utils import Numeric


def with_repr(repr_func: Callable) -> Callable:
    """Decorator to give a dynamic __repr__ to a function based on its arguments."""

    class CallableWithRepr:
        def __init__(
            self,
            func: Callable,
            *args: Any,
            **kwargs: Any,
        ) -> None:
            self.func: Callable = func
            self.args = args
            self.kwargs = kwargs

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            # Call the original function with provided arguments
            return self.func(*args, **kwargs)

        def __repr__(self) -> str:
            # Generate a custom repr using the provided repr_func
            return str(repr_func(self.func, *self.args, **self.kwargs))

    @wraps(repr_func)
    def decorator(func: Callable) -> Callable:
        # Return a wrapped CallableWithRepr instance
        return lambda *args, **kwargs: CallableWithRepr(func(*args, **kwargs), *args, **kwargs)

    return decorator


def value(x: Numeric) -> Expression:
    """Create a numerical expression from the value `x`.

    Args:
        x (complex | float | int): Any numerical value.

    Returns:
        Expression: An expression of type value.

    Raises:
        TypeError: If the argument is non-numerical.
    """
    if not isinstance(x, Numeric):
        raise TypeError(
            "Input to 'value' constructor must be of type 'complex', 'float' or 'int'. "
            f"Got {type(x)}."
        )

    return Expression.value(x)


def promote(x: Expression | Numeric) -> Expression:
    """Type cast inputs as value type expressions.

    Args:
        x (Expression | complex | float | int): A valid expression or numerical value.
         Numerical values are converted into `Value(x)` expressions.

    Returns:
        Expression: A value type or expression.
    """

    return value(x) if not isinstance(x, Expression) else x


def symbol(identifier: str, **attributes: Any) -> Expression:
    """Create a new symbol from the `identifier` if not protected.

    Args:
        identifier (str): Symbol's name.

    Kwargs:
        attributes (Any): Keywords used as flags for compilation.

    Returns:
        Expression: A symbol type expression.

    Raises:
        SyntaxError: If argument is expression protected.
    """

    if identifier in Environment.protected:
        raise SyntaxError(f"'{identifier}' is protected.")

    return Expression.symbol(identifier, **attributes)


def parameter(name: str) -> Expression:
    """A non-trainable input.

    Args:
        name (str): Parameter's name.

    Returns:
        Expression: A parameter as a symbol expression.
    """

    return symbol(name)


def variable(name: str) -> Expression:
    """A trainable input.

    Args:
        name (str): Variable's name.

    Returns:
        Expression: A variable as a trainable symbol expression.
    """

    return symbol(name, trainable=True)


def array_parameter(name: str, size: int) -> Expression:
    """A non-trainable list of inputs.

    Args:
        name (str): Array of parameters name.
        size (int): Array size.

    Returns:
        Expression: An array of parameters as sized symbol expression.
    """

    return symbol(name, size=size)


def array_variable(name: str, size: int) -> Expression:
    """A trainable list of inputs.

    Args:
        name (str): Array of variables name.
        size (int): Array size.

    Returns:
        Expression: An array of variables as sized symbol expression.
    """

    return symbol(name, trainable=True, size=size)


def function(name: str, *args: Any) -> Expression:
    """Symbolic representation of a function.

    Args:
        name (str): Function's name.
        args (Any): Remaining function arguments.

    Returns:
        Expression: A function expression.
    """

    return Expression.function(name, *args)


@with_repr(lambda func, name: f"HermitianOperator(name='{name}')")
def unitary_hermitian_operator(name: str) -> Callable:
    """An unitary Hermitian operator.

    A Hermitian operator is a function that takes a list of indices
    (or a target and control tuples) and return an Expression with
    hermitian and unitary properties.

    Args:
        name (str): The operator's name.

    Returns:
        Callable: A function to create a quantum operator expression.

    Example:
    ```
    >>> A = unitary_hermitian_operator("A")
    >>> A(i) * A(i)
    1
    >>> A(i) * A(j)  ; for i≠j
    A(i) * A(j)
    ```
    """

    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        return Expression.quantum_operator(
            Expression.symbol(name),
            support=Support(*indices, target=target, control=control),
            is_hermitian=True,
            is_unitary=True,
        )

    return core


@with_repr(lambda func, base, index: f"Projector(base='{base}', index='{index}')")
def projector(base: str, index: str) -> Callable:
    """A projector operator.

    A projector is a function that takes a list of indices
    (or a target and control tuples) and return an Expression with
    the orthogonality property.

    Args:
        base (str): The computational basis to project on.
        index (str): The index in the basis to project on.

    Returns:
        Callable: A function to create a quantum operator expression.

    Example:
    ```
    >>> P0 = projector("Z", "0")
    >>> P1 = projector("Z", "1")
    >>> P0 * P0
    P0
    >>> P0 * P1
    0
    ```
    """

    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        return Expression.quantum_operator(
            symbol(f"{base}{{{index}}}"),
            support=Support(*indices, target=target, control=control),
            base=base,
            is_projector=True,
            is_hermitian=True,
        )

    return core


@with_repr(lambda func, name: f"ParametricOperator(name='{name}')")
def parametric_operator(
    name: str, *args: Any, join: Callable | None = None, **attributes: Any
) -> Callable:
    """A parametric operator.

    A parametric operator takes a list of positional arguments and
    generates a function that takes a list of indices
    (or a target and control tuples) and return an Expression.

    The `join` function is used to combine arguments of two parametric
    operators of the same kind acting on the same qubit support.

    Args:
        name (str): The operator's name.
        args (Any): The remaining operator arguments.
        join (Callable): A function to join parameter arguments.
        attributes (Any): Keywords used for compilation.

    Returns:
        Callable: A function to create a quantum operator.
    """

    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        return Expression.quantum_operator(
            function(name, *args),
            support=Support(*indices, target=target, control=control),
            join=join,
            **attributes,
        )

    return core
