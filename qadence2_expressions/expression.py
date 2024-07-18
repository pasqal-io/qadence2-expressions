from __future__ import annotations

from functools import cached_property
from re import sub
from typing import Any

from .support import Support


class Expression:
    class Tag:
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
        if isinstance(x, int):
            return cls(cls.Tag.VALUE, float(x))
        return cls(cls.Tag.VALUE, x)

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
    def symbol(cls, identifier: str, **attributes: Any) -> Expression:
        """Create a symbol from the identifier"""
        return cls(cls.Tag.SYMBOL, identifier, **attributes)

    @classmethod
    def function(cls, name: str, *args: Any) -> Expression:
        """
        Symbolic representation of a function. The `name` indicates the function
        identifier, the remaining arguments are used as the function arguments.

            Expression.function("sin", 1.57) => sin(1.57)
        """
        return cls(cls.Tag.FN, cls.symbol(name), *args)

    @classmethod
    def quantum_operator(
        cls, expr: Expression, support: Support, **attributes: Any
    ) -> Expression:
        """Promote an expression to a quantum operator acting on the indicated  support.
        The properties indicate behaviours for evaluation like:
            - `is_hermitian` [bool]
            - `is_dagger` [bool]
        """
        return cls(cls.Tag.QUANTUM_OP, expr, support, **attributes)

    @classmethod
    def add(cls, *args: Any) -> Expression:
        """
        Define an addition expression indication the sum of its arguments.

            Expression.add(a, b, c) == a + b + c
        """
        return cls(cls.Tag.ADD, *args)

    @classmethod
    def mul(cls, *args: Any) -> Expression:
        """
        Define an multiplication expression indication the product of its arguments.

            Expression.mul(a, b, c) == a * b * c
        """

        return cls(cls.Tag.MUL, *args)

    @classmethod
    def kron(cls, *args: Any) -> Expression:
        """
        Define an Krockener product expression indication the non-commutative
        (order preserving) multiplication of its arguments.
        """

        return cls(cls.Tag.KRON, *args)

    @classmethod
    def pow(cls, base: Expression, power: Expression) -> Expression:
        """
        Define a power expression.

            Expression.power(a, b) == a**b
        """

        return cls(cls.Tag.POW, base, power)

    # Predicates
    @property
    def is_value(self) -> bool:
        return self.head == Expression.Tag.VALUE

    @property
    def is_zero(self) -> bool:
        return self.head == Expression.Tag.VALUE and self[0] == 0

    @property
    def is_one(self) -> bool:
        return self.head == Expression.Tag.VALUE and self[0] == 1

    @property
    def is_symbol(self) -> bool:
        return self.head == Expression.Tag.SYMBOL

    @property
    def is_function(self) -> bool:
        return self.head == Expression.Tag.FN

    @property
    def is_quantum_operator(self) -> bool:
        return self.head == Expression.Tag.QUANTUM_OP

    @property
    def is_addition(self) -> bool:
        return self.head == Expression.Tag.ADD

    @property
    def is_multiplication(self) -> bool:
        return self.head == Expression.Tag.MUL

    @property
    def is_kronecker_product(self) -> bool:
        return self.head == Expression.Tag.KRON

    @property
    def is_power(self) -> bool:
        return self.head == Expression.Tag.POW

    @cached_property
    def subspace(self) -> Support | None:
        if self.is_value or self.is_symbol:
            return None

        if self.is_quantum_operator:
            return self[1]  # type: ignore

        subspaces = []
        for arg in self.args:
            sp = arg.subspace
            if sp:
                subspaces.append(sp)

        if subspaces:
            total_subspace = subspaces[0]
            for subspace in subspaces[1:]:
                total_subspace = total_subspace.join(subspace)
            return total_subspace  # type: ignore

        return None

    @cached_property
    def max_index(self) -> int:
        if self.is_value or self.is_symbol:
            return -1

        if self.is_quantum_operator:
            return self.subspace.max_index  # type: ignore

        return max(map(lambda arg: arg.max_index, self.args))  # type: ignore

    # Helper functions.
    def get(self, attribute: str, default: Any | None = None) -> Any:
        """
        Return the value of the indicated expression `attribute` if present or
        the `default` otherwise. Default value is `None`.
        """
        return self.attrs.get(attribute, default)

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

        subspace = self.subspace
        if subspace:
            return Expression.quantum_operator(self, subspace)

        return self

    def __getitem__(self, index: int | slice) -> Any:
        """Access expression `expr` arguments straight from expr[i]."""
        return self.args[index]

    def __hash__(self) -> int:
        if self.is_addition or self.is_multiplication:
            return hash((self.head, frozenset(self.args)))

        return hash((self.head, self.args))

    def __repr__(self) -> str:
        args = ", ".join(map(repr, self.args))
        return f"{self.head}({args})"

    def __str__(self) -> str:
        return visualize_expression(self)

    def _repr_pretty_(self, p, _cycle) -> None:  # type: ignore
        """Provide a friendly representation when using IPython/Jupyter notebook."""
        p.text(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expression):
            return NotImplemented

        lhs_args = (
            set(self.args) if self.is_addition or self.is_multiplication else self.args
        )
        rhs_args = (
            set(other.args)
            if other.is_addition or other.is_multiplication
            else other.args
        )

        return (
            self.head == other.head
            and lhs_args == rhs_args
            and self.attrs == other.attrs
        )

    # Algebraic operations
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
            return Expression.value(self[0] + other[0])

        if self.is_addition and other.is_addition:
            args = (*self.args, *other.args)
        elif self.is_addition:
            args = (*self.args, other)
        elif other.is_addition:
            args = (self, *other.args)
        else:
            args = (self, other)

        # ⚠️ Warning: Ideally, this step should not perform the evaluation of the
        # the expression. However, we want to provide a friendly intercation to
        # the users, and the inacessibility of Python's evaluation (without writing
        # our on REPL) forces to add the evaluation at this point.
        return evaluate_addition(Expression.add(*args))

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

        # Null multiplication shortcut.
        if self.is_zero or other.is_zero:
            return Expression.zero()

        # Identity multiplication shortcut.
        if self.is_one:
            return other
        if other.is_one:
            return self

        # Numerical values are multiplied right away.
        if self.is_value and other.is_value:
            return Expression.value(self[0] * other[0])

        # Distributive rule
        if self.is_addition and not (other.is_power and self == other[0]):
            return sum(term * other for term in self.args)  # type: ignore

        if other.is_addition and not (self.is_power and self[0] == other):
            return sum(self * term for term in other.args)  # type: ignore

        if self.is_multiplication and other.is_multiplication:
            args = (*self.args, *other.args)
        elif self.is_multiplication:
            args = (*self.args, other)
        elif other.is_multiplication:
            args = (self, *other.args)
        else:
            args = (self, other)

        # ⚠️ Warning: Ideally, this step should not perform the evaluation of the
        # the expression. However, we want to provide a friendly intercation to
        # the users, and the inacessibility of Python's evaluation (without writing
        # our on REPL) forces to add the evaluation at this point.
        return evaluate_multiplication(Expression.mul(*args))

    def __rmul__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, complex | float | int):
            return Expression.value(other) * self

        return NotImplemented

    def __pow__(self, other: object) -> Expression:
        """Power involving quantum operators always promote expression to quantum operators."""

        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        if isinstance(other, complex | float | int):
            return self ** Expression.value(other)

        # Numerical values are computed right away.
        if self.is_value and other.is_value:
            return Expression.value(self[0] ** other[0])

        # Null power shortcut.
        if other.is_zero:
            return Expression.one()

        # Identity power shortcut.
        if other.is_one:
            return self

        # Power of power is an simple operation and can be evaluated here.
        # Whenever a quantum operator is present, the expression is promoted to
        # a quantum operator.
        if self.is_power:
            return Expression.pow(self[0], self[1] * other).as_quantum_operator()

        return Expression.pow(self, other).as_quantum_operator()

    def __rpow__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, complex | float | int):
            return Expression.value(other) ** self

        return NotImplemented

    def __neg__(self) -> Expression:
        return -1 * self

    def __sub__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        return self + (-other)

    def __rsub__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        return (-self) + other

    def __truediv__(self, other: object) -> Expression:
        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        return self * (other**-1)

    def __rtruediv__(self, other: object) -> Expression:
        if not isinstance(other, complex | float | int):
            return NotImplemented

        return other * (self**-1)

    def __kron__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented

        if not (
            (
                self.is_zero
                or self.is_one
                or self.is_quantum_operator
                or self.is_kronecker_product
            )
            or (
                other.is_zero
                or other.is_one
                or other.is_quantum_operator
                or other.is_kronecker_product
            )
        ):
            raise SyntaxError(f"__kron__ cannot be used with {self} and {other}")

        # Null multiplication shortcut.
        if self.is_zero or other.is_zero:
            return Expression.zero()

        # Identity multiplication shortcut.
        if self.is_one:
            return other

        if other.is_one:
            return self

        # ⚠️ Warning: Ideally, this step should not perform the evaluation of the
        # the expression. However, we want to provide a friendly intercation to
        # the users, and the inacessibility of Python's evaluation (without writing
        # our on REPL) forces to add the evaluation at this point.
        return evaluate_kron(Expression.kron(self, other))


def evaluate_addition(expr: Expression) -> Expression:
    if not expr.is_addition:
        return expr

    numerical_value = Expression.zero()
    general_terms: dict[Expression, Expression] = dict()

    for term in expr.args:
        if term.is_value:
            numerical_value = numerical_value + term

        elif term.is_multiplication and term[0].is_value:
            coef = term[0]
            elem = term[1] if len(term.args) == 2 else Expression.mul(*term[1:])
            general_terms[elem] = general_terms.get(elem, Expression.zero()) + coef

        else:
            general_terms[term] = (
                general_terms.get(term, Expression.zero()) + Expression.one()
            )

    args = tuple(elem * coef for elem, coef in general_terms.items())

    if not numerical_value.is_zero:
        args = (numerical_value, *args)

    return args[0] if len(args) == 1 else Expression.add(*args)


def evaluate_multiplication(expr: Expression) -> Expression:
    if not expr.is_multiplication:
        return expr

    numerical_value = Expression.one()
    quantum_operators = Expression.one()
    general_terms: dict[Expression, Expression] = dict()

    for term in expr.args:
        if term.is_value:
            numerical_value = numerical_value * term

        elif term.is_quantum_operator or term.is_kronecker_product:
            quantum_operators = quantum_operators.__kron__(term)

        elif term.is_power:
            base, power = term[:2]
            general_terms[base] = general_terms.get(base, Expression.zero()) + power

        else:
            general_terms[term] = (
                general_terms.get(term, Expression.zero()) + Expression.one()
            )

    if numerical_value.is_zero or quantum_operators.is_zero:
        return Expression.zero()

    args = tuple(
        base**power for base, power in general_terms.items() if not power.is_zero
    )

    if not quantum_operators.is_one:
        args = (*args, quantum_operators)

    if not numerical_value.is_one or len(args) == 0:
        args = (numerical_value, *args)

    return args[0] if len(args) == 1 else Expression.mul(*args)


def evaluate_kron(expr: Expression) -> Expression:
    lhs = expr[0]
    for rhs in expr[1:]:
        if lhs.is_quantum_operator and rhs.is_quantum_operator:
            lhs = evaluate_kronop(lhs, rhs)

        elif lhs.is_quantum_operator and rhs.is_kronecker_product:
            lhs = evaluate_kronleft(lhs, rhs)

        elif lhs.is_kronecker_product and rhs.is_quantum_operator:
            lhs = evaluate_kronright(lhs, rhs)

        elif lhs.is_kronecker_product and rhs.is_kronecker_product:
            lhs = evaluate_kronjoin(lhs, rhs)

        else:
            raise NotImplementedError

    return lhs  # type: ignore


def evaluate_kronleft(lhs: Expression, rhs: Expression) -> Expression:
    """
    Evaluate the Kronecker product between a LHS=quantum operators and a RHS=Kronecker product.
    """
    if not (lhs.is_quantum_operator or rhs.is_kronecker_product):
        raise SyntaxError(
            "Only defined for a quantum operator and a Kronecker product."
        )

    args = rhs.args
    for i, rhs_arg in enumerate(args):
        if rhs_arg.subspace == lhs.subspace:  # type: ignore
            ii = i + 1

            result = evaluate_kronop(lhs, rhs_arg)

            if result.is_one:
                args = (*args[:i], *args[ii:])

            elif result.is_kronecker_product:
                args = (*args[:i], *result.args, *args[ii:])

            else:
                args = (*args[:i], result, *args[ii:])

            break

        if (
            rhs_arg.subspace > lhs.subspace  # type: ignore
            or rhs_arg.subspace.overlap_with(lhs.subspace)  # type: ignore
        ):
            args = (*args[:i], lhs, *args[i:])
            break

        if i == len(args) - 1:
            args = (lhs, *args)

    if not args:
        return Expression.one()

    return args[0] if len(args) == 1 else Expression.kron(*args)  # type: ignore


def evaluate_kronright(lhs: Expression, rhs: Expression) -> Expression:
    """
    Evaluate the Kronecker product between a LHS=quantum operators and a RHS=Kronecker product.
    """
    if not (lhs.is_kronecker_product or rhs.is_quantum_operator):
        raise SyntaxError(
            "Only defined for a Kronecker product and a quantum operator."
        )

    args = lhs.args
    for i in range(len(args) - 1, -1, -1):
        ii = i + 1

        if args[i].subspace == rhs.subspace:  # type: ignore
            result = evaluate_kronop(args[i], rhs)

            if result.is_one:
                args = (*args[:i], *args[ii:])

            elif result.is_kronecker_product:
                args = (*args[:i], *result.args, *args[ii:])

            else:
                args = (*args[:i], result, *args[ii:])

            break

        if args[i].subspace < rhs.subspace or args[i].subspace.overlap_with(
            rhs.subspace
        ):
            args = (*args[:ii], rhs, *args[ii:])
            break

        if i == 0:
            args = (rhs, *args)

    if not args:
        return Expression.one()

    return args[0] if len(args) == 1 else Expression.kron(*args)  # type: ignore


def evaluate_kronjoin(lhs: Expression, rhs: Expression) -> Expression:
    """
    Evaluate the Kronecker product between a LHS=quantum operators and a RHS=Kronecker product.
    """
    if not (lhs.is_kronecker_product or rhs.is_kronecker_product):
        raise SyntaxError("Only defined for LHS and RHS both Kronecker product.")

    result = lhs
    for term in rhs.args:
        result = evaluate_kron(Expression.kron(result, term))

    return result


def evaluate_kronop(lhs: Expression, rhs: Expression) -> Expression:
    """Evaluate the Kronecker product between two quantum operators."""
    if not (lhs.is_quantum_operator or rhs.is_quantum_operator):
        raise SyntaxError(
            "Operation only valid for LHS and RHS both quantum operators."
        )

    # Multiplication of unitary Hermitian operators acting on the the same subspace.
    if lhs == rhs and (lhs.get("is_hermitian") and lhs.get("is_unitary")):
        return Expression.one()

    # General multiplications of operators acting on the same subspace.
    if lhs.subspace == rhs.subspace:
        if lhs.get("is_projector") and rhs.get("is_projector"):
            return lhs if lhs[0] == rhs[0] else Expression.zero()

        if (
            lhs[0].is_function
            and rhs[0].is_function
            and lhs[0][0] == rhs[0][0]
            and lhs.get("join")
        ):
            res = lhs.get("join")(lhs[0], rhs[0])
            return (  # type: ignore
                res
                if res.is_zero or res.is_one
                else Expression.quantum_operator(res, lhs[1])
            )

    # Order the operators by subspace.
    if lhs.subspace < rhs.subspace or lhs.subspace.overlap_with(  # type: ignore
        rhs.subspace  # type: ignore
    ):
        return Expression.kron(lhs, rhs)

    return Expression.kron(rhs, lhs)


def visualize_expression(expr: Expression) -> str:
    if expr.is_value or expr.is_symbol:
        return str(expr[0])

    if expr.is_quantum_operator:
        return f"{expr[0]}{expr[1]}"

    if expr.is_function:
        args = ",\u2009".join(map(str, expr[1:]))
        return f"{expr[0]}({args})"

    if expr.is_multiplication:
        result = visualize_sequence(expr, "\u2009")
        return sub(r"-1\.0\s", "-", result)

    if expr.is_kronecker_product:
        return visualize_sequence(expr, "\u2008")

    if expr.is_addition:
        result = visualize_sequence(expr, " + ", with_brackets=False)
        return sub(r"\s\+\s-(1\.0\s)?", " - ", result)

    if expr.is_power:
        return visualize_sequence(expr, "\u2009^\u2009")

    return repr(expr)


def visualize_sequence(
    expr: Expression, operator: str, with_brackets: bool = True
) -> str:
    if (
        expr.is_value
        or expr.is_symbol
        or (expr.is_quantum_operator and expr[0].is_symbol)
    ):
        raise SyntaxError("Only sequence of expression are allowed.")

    if with_brackets:
        return operator.join(map(visualize_with_brackets, expr.args))

    return operator.join(map(str, expr.args))


def visualize_with_brackets(expr: Expression) -> str:
    if expr.is_multiplication or expr.is_addition:
        return f"({str(expr)})"

    return str(expr)
