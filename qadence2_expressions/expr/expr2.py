from __future__ import annotations

from typing import Any, Callable

from qadence2_expressions.expr.qubit_support import Support

# TODO:
#   - [] Implement evaluate_addition
#   - [] Implement evaluare_multiplication
#   - [] Implement evaluate_kronecker_product
#   - [] Implement evaluate_kron_op (for operator-operator)


class Expression:
    class Token:
        # Identifiers:
        VALUE = "Value"
        SYMBOL = "Symbol"
        FN = "Function"
        QUANTUM_OP = "QuantumOperator"

        # Operations:
        ADD = "Add"
        MUL = "Multiply"
        KRON = "KroneckerProduct"
        POW = "Power"

    def __init__(self, head: str, *args: Any, **attributes: Any) -> None:
        self.head = head
        self.args = args
        self.attrs = attributes

    # Constructors
    @classmethod
    def value(cls, x: complex | float | int) -> Expression:
        """Promote a numerical value (comples, float, int) to an expression."""
        return cls(cls.Token.VALUE, x)

    @classmethod
    def zero(cls) -> Expression:
        return cls.value(0)

    @classmethod
    def one(cls) -> Expression:
        """
        The value(1) is used to represent both the concrete number 1 and the
        identity operator.
        """
        return cls.value(1)

    @classmethod
    def symbol(cls, identifier: str) -> Expression:
        """Create a symbol from the identifier"""
        return cls(cls.Token.SYMBOL, identifier)

    @classmethod
    def function(cls, name: str, *args: Any) -> Expression:
        """
        Symbolic representation of a function. The `name` indicates the function
        identifier, the remaining arguments are used as the function arguments.

            Expression.function("sin", 1.57) => sin(1.57)
        """
        return cls(cls.Token.FN, name, *args)

    @classmethod
    def quantum_operator(
        cls, expr: Expression, support: Support, **properties
    ) -> Expression:
        """Promote an expression to a quantum operator acting on the indicated  support.
        The properties indicate behaviours for evaluation like:
            - `is_hermitian` [bool]
            - `is_dagger` [bool]
        """
        return cls(cls.Token.QUANTUM_OP, expr, support, **properties)

    @classmethod
    def add(cls, *args: Any) -> Expression:
        """
        Define an addition expression indication the sum of its arguments.

            Expression.add(a, b, c) == a + b + c
        """
        return cls(cls.Token.ADD, *args)

    @classmethod
    def mul(cls, *args: Any) -> Expression:
        """
        Define an multiplication expression indication the product of its arguments.

            Expression.mul(a, b, c) == a * b * c
        """

        return cls(cls.Token.MUL, *args)

    @classmethod
    def kron(cls, *args: Any) -> Expression:
        """
        Define an Krockener product expression indication the non-commutative
        (order preserving) multiplication of its arguments.
        """

        return cls(cls.Token.KRON, *args)

    @classmethod
    def pow(cls, base: Expression, power: Expression) -> Expression:
        """
        Define a power expression.

            Expression.power(a, b) == a**b
        """

        return cls(cls.Token.POW, base, power)

    # Predicates
    @property
    def is_value(self) -> bool:
        return self.head == Expression.Token.VALUE

    @property
    def is_zero(self) -> bool:
        return self.head == Expression.Token.VALUE and self.args[0] == 0

    @property
    def is_one(self) -> bool:
        return self.head == Expression.Token.VALUE and self.args[0] == 1

    @property
    def is_symbol(self) -> bool:
        return self.head == Expression.Token.SYMBOL

    @property
    def is_function(self) -> bool:
        return self.head == Expression.Token.FN

    @property
    def is_quantum_operator(self) -> bool:
        return self.head == Expression.Token.QUANTUM_OP

    @property
    def is_addition(self) -> bool:
        return self.head == Expression.Token.ADD

    @property
    def is_multiplication(self) -> bool:
        return self.head == Expression.Token.MUL

    @property
    def is_kronecker_product(self) -> bool:
        return self.head == Expression.Token.KRON

    @property
    def is_power(self) -> bool:
        return self.head == Expression.Token.POW

    # Helper functions.
    def get_attr(self, attribute: str, default: Any | None = None) -> Any:
        """
        Return the value of the indicated expression `attribute` if present or
        the `default` otherwise. Default value is `None`.
        """
        return self.attrs.get(attribute, default)

    def subspace(self) -> Support | None:
        if self.is_value or self.is_symbol:
            return None

        if self.is_quantum_operator:
            return self.args[1]

        subspaces = []
        for arg in self.args:
            sp = arg.subspace()
            if sp:
                subspaces.append(sp)

        if subspaces:
            total_subspace = subspaces[0]
            for subspace in subspaces[1:]:
                total_subspace = total_subspace.join(subspace)
            return total_subspace

        return None

    def as_quantum_operator(self) -> Expression:
        """
        Promotes and expression to a quantum operator.

        When a function receives a quantum operator as input, the function itself must be turned
        into a quantum operator in order to preserve commutation properties. For instance,

        >>> exp(2) * exp(3)
        exp(5)
        >>> exp(X(1)) * exp(Y(1))
        exp(X(1)) exp(Y(1))
        """

        subspace = self.subspace()
        if subspace:
            return Expression.quantum_operator(self, subspace)

        return self

    # Python magic methods
    def __repr__(self) -> str:
        args = ", ".join(map(repr, self.args))
        return f"{self.head}({args})"

    def __hash__(self) -> int:
        if self.is_addition or self.is_multiplication:
            return hash((self.head, frozenset(self.args)))

        return hash((self.head, self.args))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expression):
            return NotImplemented

        return (
            self.head == other.head
            and self.args == other.args
            and self.attrs == other.attrs
        )

    def __add__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        # Promote numerial values to Expression.
        if isinstance(other, complex | float | int):
            return self + Expression.value(other)

        # Addition identity: a + 0 = 0 + a = a
        if self.is_zero:
            return other

        if other.is_zero:
            return self

        # Numerical values are added right away
        if self.is_value and other.is_value:
            return Expression.value(self.args[0] + other.args[0])

        if self.is_addition and other.is_addition:
            args = (*self.args, *other.args)
        elif self.is_addition:
            args = (*self.args, other)
        elif other.is_addition:
            args = (self, *other.args)
        else:
            args = (self, other)

        # return evaluate_addition(Expression.add(*args))
        return Expression.add(*args)

    def __radd__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, complex | float | int):
            return Expression.value(other) + self

        return NotImplemented

    def __mul__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        # Promote numerical values to Expression.
        if isinstance(other, complex | float | int):
            return self * Expression.value(other)

        # Null multiplication.
        if self.is_zero or other.is_zero:
            return Expression.zero()

        # Multiplication identity: a * 1 = 1 * a = a.
        if self.is_one:
            return other
        if other.is_one:
            return self

        # Numerical values are multiplied right away.
        if self.is_value and other.is_value:
            return Expression.value(self.args[0] * other.args[0])

        if self.is_multiplication and other.is_multiplication:
            args = (*self.args, *other.args)
        elif self.is_multiplication:
            args = (*self.args, other)
        elif other.is_multiplication:
            args = (self, *other.args)
        else:
            args = (self, other)

        # return evaluate_multiplication(Expression.mul(*args))
        return Expression.mul(*args)

    def __rmul__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, complex | float | int):
            return Expression.value(other) * self

        return NotImplemented

    def __pow__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        if isinstance(other, complex | float | int):
            return self ** Expression.value(other)

        # Null power.
        if other.is_zero:
            return Expression.one()

        # Identity power.
        if other.is_one:
            return self

        # Power of power.
        if self.is_power:
            return Expression.pow(self.args[0], self.args[1] * other)

        return Expression.pow(self, other).as_quantum_operator()

    def __rpow__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, complex | float | int):
            return Expression.value(other) ** self

        return NotImplemented

    def __kron__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented

        # Identity multiplication.
        if self.is_one:
            return other

        if other.is_one:
            return self

        if self.is_quantum_operator and other.is_quantum_operator:
            return self.__kron_op__(other)

        if self.is_kronecker_product and other.is_quantum_operator:
            return self.__insertr__(other)

        if self.is_quantum_operator and other.is_kronecker_product:
            return other.__insertl__(self)

        if self.is_kronecker_product and other.is_kronecker_product:
            return other.__kron_join__(self)

        raise SyntaxError(f"__kron__ cannot be used with {self} and {other}")

    def __kron_op__(self, other: object) -> Expression:
        """Performs the Kronecker product between two quantum operators."""
        return Expression.kron(self, other)

    def __insertr__(self, term: Expression) -> Expression:
        """Insert a new quantum operator term into a Kronecker product expression from the right."""

        if not (self.is_kronecker_product or term.is_quantum_operator):
            raise SyntaxError(
                "Only defined for Kronecker product and quantum operator."
            )

        args = self.args
        for i in range(len(args) - 1, -1, -1):
            ii = i + 1

            if args[i].subspace() == term.subspace():  # type: ignore
                result = args[i].__kron_op__(term)

                if result.is_one:
                    args = (*args[:i], *args[ii:])

                elif result.is_kronecker_product:
                    args = (*args[:i], *result.args, *args[ii:])

                else:
                    args = (*args[:i], result, *args[ii:])

                break

            if (
                args[i].subspace() < term.subspace()  # type: ignore
                or args[i].subspace().overlap_with(term.subspace())  # type: ignore
            ):
                args = (*args[:ii], term, *args[ii:])
                break

            if i == 0:
                args = (term, *args)

        if not args:
            return Expression.one()

        return args[0] if len(args) == 1 else Expression.kron(*args)

    def __insertl__(self, term: Expression) -> Expression:
        """Insert a new quantum operator term into a Kronecker product expression from the left."""

        if not (self.is_kronecker_product or term.is_quantum_operator):
            raise SyntaxError(
                "Only defined for Kronecker product and quantum operator."
            )

        args = self.args
        for i, arg in enumerate(args):

            if arg.subspace() == term.subspace():  # type: ignore
                ii = i + 1

                result = term.__kron_op__(arg)

                if result.is_one:
                    args = (*args[:i], *args[ii:])

                elif result.is_kronecker_product:
                    args = (*args[:i], *result.args, *args[ii:])

                else:
                    args = (*args[:i], result, *args[ii:])

                break

            if (
                arg.subspace() > term.subspace()  # type: ignore
                or arg.subspace().overlap_with(term.subspace())  # type: ignore
            ):
                args = (*args[:i], term, *args[i:])
                break

            if i == len(args) - 1:
                args = (term, *args)

        if not args:
            return Expression.one()

        return args[0] if len(args) == 1 else Expression.kron(*args)

    def __kron_join__(self, other: Expression) -> Expression:
        if not (self.is_kronecker_product or other.is_kronecker_product):
            raise SyntaxError("Operation only defined")

        result = self
        for term in other.args:
            result = result.__insertr__(term)

        return result


def value(x: complex | float | int) -> Expression:
    """Promotes a numerical value to an expression."""
    return Expression.value(x)


def symbol(identifier: str) -> Expression:
    """Defines a new symbol."""
    if identifier == "e":
        raise SyntaxError("The name `exp` is protected")
    return Expression.symbol(identifier)


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
    ):
        return Expression.quantum_operator(
            Expression.symbol(name),
            Support(*indices, target=target, control=control),
            is_hermitian=True,
            is_unitary=True,
        )

    return core
