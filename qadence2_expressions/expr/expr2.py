from __future__ import annotations

from typing import Any, Callable

from .qubit_support import Support


class Operator:
    PLUS = "Plus"
    TIMES = "Times"
    POWER = "Power"
    NONCOMMUTE = "NonCommute"


class ExprType:
    SYMBOL = "Symbol"
    VALUE = "Value"
    CALL = "Call"
    QUANTUM = "QuantumOp"


class Expression:
    def __init__(self, head: str, *args: Any) -> None:
        self.head = head
        self.args = args

    def __repr__(self) -> str:
        args = ", ".join(map(str, self.args))
        return f"{self.head}({args})"

    def __hash__(self) -> int:
        if self.head in [Operator.PLUS, Operator.TIMES]:
            return hash((self.head, frozenset(self.args)))

        return hash((self.head, self.args))

    @classmethod
    def zero(cls) -> Expression:
        return Expression(ExprType.VALUE, 0)

    @classmethod
    def one(cls) -> Expression:
        return Expression(ExprType.VALUE, 1)

    @classmethod
    def value(cls, val: complex | float | int) -> Expression:
        return Expression(ExprType.VALUE, val)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Expression):
            return NotImplemented

        # Compare expressions of the same type
        if self.head == value.head:
            return (
                set(self.args) == set(value.args)
                if self.head in [Operator.PLUS, Operator.TIMES]
                else self.args == value.args
            )

        return False

    def __add__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        # Promote numerical types to expressions
        if isinstance(other, complex | float | int):
            return self + Expression.value(other)

        # Zero is the identity of addition.
        if other == Expression.zero():
            return self

        if self == Expression.zero():
            return other

        # complex | float | int values are added right away.
        if self.head == other.head and self.head == ExprType.VALUE:
            return Expression.value(self.args[0] + other.args[0])

        if self.head == other.head and self.head == Operator.PLUS:
            # TODO: Add sum reduction
            args = (*self.args, *other.args)
            return Expression(Operator.PLUS, *args)

        if self.head == Operator.PLUS:
            # TODO: Add sum reduction
            args = (*self.args, other)
            return Expression(Operator.PLUS, *args)

        if other.head == Operator.PLUS:
            # TODO: Add sum reduction
            args = (self, *other.args)
            return Expression(Operator.PLUS, *args)

        return Expression(Operator.PLUS, self, other)

    def __radd__(self, other: object) -> Expression:
        return self + other

    def __mul__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        # Promote numerical types to expressions
        if isinstance(other, complex | float | int):
            return self * Expression.value(other)

        # Multiplication by zero.
        if self == Expression.zero() or other == Expression.zero():
            return Expression.zero()

        # One is indentity for multimplication.
        if other == Expression.one():
            return self

        if self == Expression.one():
            return other

        # complex | float | int values are multiplied right away.
        if self.head == other.head and self.head == ExprType.VALUE:
            return Expression.value(self.args[0] * other.args[0])

        if self.head == other.head and self.head == Operator.TIMES:
            # TODO: Add multiplication reduction
            args = (*self.args, *other.args)
            return Expression(Operator.TIMES, *args)

        if self.head == Operator.TIMES:
            # TODO: Add multiplication reduction
            args = (*self.args, other)
            return Expression(Operator.TIMES, *args)

        if other.head == Operator.TIMES:
            # TODO: Add multiplication reduction
            args = (self, *other.args)
            return Expression(Operator.TIMES, *args)

        return Expression(Operator.TIMES, self, other)

    def __rmul__(self, other: object) -> Expression:
        return self * other

    def __neg__(self) -> Expression:
        return -1 * self

    def __sub__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        return self + (-other)

    def __rsub__(self, other: object) -> Expression:
        return (-self) + other

    def __pow__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        if isinstance(other, complex | float | int):
            return self ** Expression.value(other)

        if (
            isinstance(other, Expression)
            and self.head == other.head
            and other.head == ExprType.VALUE
        ):
            return Expression.value(self.args[0] ** other.args[0])

        if isinstance(other, complex | float | int):
            return Expression(Operator.POWER, self, Expression.value(other))

        return Expression(Operator.POWER, self, other)

    def __rpow__(self, other: object) -> Expression:
        if not isinstance(other, complex | float | int):
            return NotImplemented

        return Expression.value(other) ** self


#
#
def symbol(identfier: str) -> Expression:
    return Expression(ExprType.SYMBOL, identfier)


def value(val: complex | float | int) -> Expression:
    return Expression.value(val)


def function(name: str, *args: Any) -> Expression:
    return Expression(ExprType.CALL, name, *args)


def qsymbol(name: str) -> Callable:
    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        return Expression(
            ExprType.QUANTUM, name, Support(*indices, target=target, control=control)
        )

    return core
