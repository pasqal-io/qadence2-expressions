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
    def __init__(self, head: str, *args: Any, **kwargs: Any) -> None:
        self.head = head
        self.args = args
        self.kwargs = kwargs

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

    def is_value(self) -> bool:
        return self.head == ExprType.VALUE

    def is_symbol(self) -> bool:
        return self.head == ExprType.SYMBOL

    def is_call(self) -> bool:
        return self.head == ExprType.CALL

    def is_quantumop(self) -> bool:
        return self.head == ExprType.QUANTUM

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
            return self.__add__(Expression.value(other))

        # Zero is the identity of addition.
        if other == Expression.zero():
            return self

        if self == Expression.zero():
            return other

        # Numerical values are added right away.
        if self.head == other.head and self.head == ExprType.VALUE:
            return Expression.value(self.args[0] + other.args[0])

        elif self.head == other.head and self.head == Operator.PLUS:
            args = (*self.args, *other.args)

        elif self.head == Operator.PLUS:
            args = (*self.args, other)

        elif other.head == Operator.PLUS:
            args = (self, *other.args)

        else:
            args = (self, other)

        # TODO: Find a smart way to toogle the arguments reduction.
        result = Expression(Operator.PLUS, *args)
        return reduce_addition(result)

    def __radd__(self, other: object) -> Expression:
        return self + other

    def __mul__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        # Promote numerical types to expressions
        if isinstance(other, complex | float | int):
            return self.__mul__(Expression.value(other))

        # Multiplication by zero.
        if self == Expression.zero() or other == Expression.zero():
            return Expression.zero()

        # One is indentity for multimplication.
        if other == Expression.one():
            return self

        if self == Expression.one():
            return other

        # Numerical values are multiplied right away.
        if self.head == other.head and self.head == ExprType.VALUE:
            return Expression.value(self.args[0] * other.args[0])

        if self.head == other.head and self.head == Operator.TIMES:
            args = [*self.args, *other.args]

        elif self.head == Operator.TIMES:
            args = [*self.args, other]

        elif other.head == Operator.TIMES:
            args = [self, *other.args]

        else:
            args = [self, other]

        # TODO: Find a smart way to toogle the arguments reduction.
        result = Expression(Operator.TIMES, *args)
        return reduce_multiplication(result)

    def __rmul__(self, other: object) -> Expression:
        if not isinstance(other, complex | float | int):
            return NotImplemented

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

        # Promote numerical types to expressions.
        if isinstance(other, complex | float | int):
            return self ** Expression.value(other)

        # Identity power: x^1 = x
        if other == Expression.one():
            return self

        # Numerical values are operatered right away.
        if (
            isinstance(other, Expression)
            and self.head == other.head
            and other.head == ExprType.VALUE
        ):
            return Expression.value(self.args[0] ** other.args[0])

        if self.head == Operator.POWER:
            base, power = self.args[:2]
            return Expression(Operator.POWER, base, power * other)

        return Expression(Operator.POWER, self, other)

    def __rpow__(self, other: object) -> Expression:
        if not isinstance(other, complex | float | int):
            return NotImplemented

        return Expression.value(other) ** self

    def __truediv__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        # Promote numerical values to expressions.
        if isinstance(other, complex | float | int):
            return self / Expression.value(other)

        return self * (other**-1)

    def __rtruediv__(self, other: object) -> Expression:
        return other * (self**-1)


def reduce_addition(expr: Expression) -> Expression:
    if expr.head != Operator.PLUS:
        raise SyntaxError("This function only apply to addition expressions.")

    numerical_value = Expression.zero()
    general_terms: dict[Expression, complex | float | int] = {}

    for term in expr.args:
        match term.head:
            # Numerical types are comibined in a single term
            case ExprType.VALUE:
                numerical_value += term.args[0]

            # Multiplicative terms with numerical constants have theier coefficents combined.
            case Operator.TIMES:
                if term.args[0].is_value():
                    elem = Expression(Operator.TIMES, *term.args[1:])
                    general_terms[elem] = general_terms.get(elem, 0) + term.args[0]

                else:
                    general_terms[term] = general_terms.get(term, 0) + 1

            case _:
                general_terms[term] = general_terms.get(term, 0) + 1

    expr_term = [term * coef for term, coef in general_terms.items()]

    if not expr_term:
        return numerical_value

    if numerical_value == Expression.zero():
        return (
            expr_term[0]
            if len(expr_term) < 2
            else Expression(Operator.PLUS, *expr_term)
        )

    return Expression(Operator.PLUS, numerical_value, *expr_term)


def reduce_multiplication(expr: Expression) -> Expression:
    if expr.head != Operator.TIMES:
        raise SyntaxError("This function only apply to multiplication expressions.")

    numerical_value = Expression.one()
    quantum_ops = []
    general_terms: dict[Expression, complex | float | int] = {}

    for term in expr.args:
        match term.head:
            # Numerical types are comibined in a single term
            case ExprType.VALUE:
                numerical_value *= term.args[0]

            # Single quantum operators are inserted in the order they appear.
            case ExprType.QUANTUM:
                quantum_ops.append(term)

            # Sequence of quantum operators are appended to preserve the order.
            case Operator.NONCOMMUTE:
                quantum_ops.extend(term.args)

            # Powered terms are added to the general term combining the powers.
            case Operator.POWER:
                base, power = term.args[:2]
                general_terms[base] = general_terms.get(base, 0) + power

            case _:
                general_terms[term] = general_terms.get(term, 0) + 1

    expr_terms: list[Expression] = [
        b**p for b, p in general_terms.items() if p != Expression.zero()
    ]

    if quantum_ops:
        # TODO: Implement `reduce_noncommute` for quantum operations.
        expr_terms.append(Expression(Operator.NONCOMMUTE, *quantum_ops))

    if not expr_terms:
        return numerical_value

    if numerical_value == Expression.one():
        return (
            expr_terms[0]
            if len(expr_terms) < 2
            else Expression(Operator.TIMES, *expr_terms)
        )

    return Expression(Operator.TIMES, numerical_value, *expr_terms)


# def reduce_noncommutative_multiplication(expr: Expression) -> Expression:
#     pass


# =====
# UTILS
# =====
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
