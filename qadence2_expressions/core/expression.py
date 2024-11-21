from __future__ import annotations

import warnings
from enum import Enum
from functools import cached_property, reduce
from re import sub
from typing import Any

from .support import Support
from .utils import Numeric


class Expression:
    """A symbolic representation of mathematical expressions.

    Besides arithmetic operations, the expression can contain classical functions such as sine,
    cosine, and logarithm, and abstract representations of quantum operators.

    Multiplication between quantum operators is stored as Kronecker products. Operators are ordered
    by qubit index, preserving the order when the qubit indices of two operators overlap. This
    ensures that operators acting on the same subspace are kept together, enhancing optimisation.
    """

    class Tag(Enum):
        """This auxiliar class allows the `Expression` to be represented as a tagged union."""

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

    def __init__(self, head: Expression.Tag, *args: Any, **attributes: Any) -> None:
        self.head = head
        self.args = args
        self.attrs = attributes

    # Constructors
    @classmethod
    def value(cls, x: Numeric) -> Expression:
        """Promote a numerical value (complex, float, int) to an expression.

        Args:
            x: A numerical value.

        Returns:
            A `Value(x)` expression.
        """

        return cls(cls.Tag.VALUE, float(x)) if isinstance(x, int) else cls(cls.Tag.VALUE, x)

    @classmethod
    def zero(cls) -> Expression:
        """Used to represent both, the numerical value `0` and the null operator.

        Returns:
            An `Value(0)` expression.
        """
        return cls.value(0)

    @classmethod
    def one(cls) -> Expression:
        """Used to represent both, the numerical value `1` and the identity operator.

        Returns:
            An `Value(1)` expression.
        """
        return cls.value(1)

    @classmethod
    def symbol(cls, identifier: str, **attributes: Any) -> Expression:
        """Create a symbol from the identifier.

        Args:
            identifier: A string used as the symbol name.

        Kwargs:
            Keyword arguments are used as flags for compilation steps.
            The valid flags are defined in Qadence2-IR.

        Returns:
            A `Symbol('identifier')` expression.
        """
        return cls(cls.Tag.SYMBOL, identifier, **attributes)

    @classmethod
    def function(cls, name: str, *args: Any) -> Expression:
        """
        Symbolic representation of a function. The `name` indicates the function identifier, the
        remaining arguments are used as the function arguments.

            Expression.function("sin", 1.57) => sin(1.57)

        Args:
            name: The function name.
            args: The arguments to be passed to the function.

        Returns:
            A `Function(Symbol('name'), args...)` expression.
        """
        return cls(cls.Tag.FN, cls.symbol(name), *args)

    @classmethod
    def quantum_operator(cls, expr: Expression, support: Support, **attributes: Any) -> Expression:
        """To turn an expression into a quantum operator, specify the support it acts on. Attributes
        like `is_projector` [bool], `is_hermitian` [bool], `is_unitary` [bool], `is_dagger` [bool],
        and `join` [callable] indicate how the operator behaves during evaluation.

        A parametric quantum operator is a function wrapped in a quantum operator. The `join`
        attribute is used to combine the arguments of two parametric operators.

        Args:
            expr: An expression that describes the operator. If `expr` is a symbol, it represents
                a generic gate like Pauli and Clifford gates. If `expr` is a function, it represents
                a parametric operator. Power expressions can be used to represent unitary evolution
                operators.
            support: The qubit indices to what the operator is applied.

        Kwargs:
            Keyword arguments are used primarily to symbolic evaluation. Examples of keywords are:
                - `is_projector` [bool]
                - `is_hermitian` [bool]
                - `is_unitary` [bool]
                - `is_dagger` [bool]
                - `join` [callable]

            The keyword, `join` is used with parametric operators. Whe two parametric operator of
            the same kind action on the same subspace are muliplied, the `join` is used to combine
            their arguments.

        Returns:
            An expression of type `QuantumOperator`.
        """

        return cls(cls.Tag.QUANTUM_OP, expr, support, **attributes)

    @classmethod
    def add(cls, *args: Expression) -> Expression:
        """In Expressions, addition is a variadic operation representing the sum of its arguments.

        Expression.add(a, b, c) == a + b + c
        """
        return cls(cls.Tag.ADD, *args)

    @classmethod
    def mul(cls, *args: Expression) -> Expression:
        """In Expressions, multiplication is a variadic operation representing the product of its
        arguments.

            Expression.mul(a, b, c) == a * b * c
        """

        return cls(cls.Tag.MUL, *args)

    @classmethod
    def kron(cls, *args: Expression) -> Expression:
        """In Expressions, the Kronecker product is a variadic operation representing the
        multiplication of its arguments applying commutative rules. When the qubit indices of two
        operators overlap, the order is preserved. Otherwise, the operators are ordered by index,
        with operators acting on the same qubits placed next to each other.

            Expression.kron(X(1), X(2), Y(1)) == X(1)Y(1) ⊗  X(2)
        """

        return cls(cls.Tag.KRON, *args)

    @classmethod
    def pow(cls, base: Expression, power: Expression) -> Expression:
        """Define a power expression.

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
        """Returns the total subspace coverage of an expression with quantum operators. If there are
        no quantum operators, the subspace is None. If controlled operators are present, it returns
        a controlled support if there is no overlap between targets and controls; otherwise, all
        indices are treated as targets.

        Example:
        ```python
        >>> value(1).subspace
        None
        >>> (X(1) + Y(2)).subspace
        [1 2]
        >>> (X(target=(1,), control=(0,)) + Y(2)).subspace
        [1 2|0]
        >>> (X(target=(1,), control=(2,)) + Y(2)).subspace
        [1 2]
        ```
        """

        if self.is_value or self.is_symbol:
            return None

        # By definition, a quantum operator is `QuantumOperator(Expression, Support)`.
        if self.is_quantum_operator:
            support: Support = self[1]
            return support

        # Collecting only non-null term's subspaces.
        subspaces = []
        for arg in self.args:
            sp = arg.subspace
            if sp:
                subspaces.append(sp)

        # Merge all the valid subspaces in the expression. Targets and controls that overlap will be
        # converted into target-only subspaces.
        if subspaces:
            total_subspace = subspaces[0]
            for subspace in subspaces[1:]:
                total_subspace = total_subspace.join(subspace)
            return total_subspace  # type: ignore

        return None

    @cached_property
    def max_index(self) -> int:
        """Returns the maximum qubit index present in the expression. An expression without quantum
        operators or covering all the qubits will return -1.

        Example:
        ```
        >>> value(2).max_index
        -1
        >>> (X() * Y(1)).max_index
        -1
        >>> (X(0, 2) * Y(1)).max_index
        2
        ```
        """

        if self.is_value or self.is_symbol:
            return -1

        if self.is_quantum_operator:
            return self.subspace.max_index  # type: ignore

        # Return the maximum index among all the terms.
        return max(map(lambda arg: arg.max_index, self.args))  # type: ignore

    # Helper functions.
    def get(self, attribute: str, default: Any | None = None) -> Any:
        """Retrieve the value of the chosen `attribute` if it exists, or return the `default` value
        if it doesn't.
        """
        return self.attrs.get(attribute, default)

    def as_quantum_operator(self) -> Expression:
        """Promotes and expression to a quantum operator.

        When a function takes a quantum operator as input, the function itself must be transformed
        into a quantum operator to preserve commutation properties. For instance,

        Example:
        ```
        >>> exp(2) * exp(3)
        exp(5)
        >>> exp(X(1)) * exp(Y(1))
        exp(X(1)) exp(Y(1))
        ```
        """

        subspace = self.subspace
        if subspace:
            return Expression.quantum_operator(self, subspace)

        return self

    @property
    def dag(self) -> Expression:
        """Returns the conjugated/dagger version of and expression."""

        if self.is_symbol or self.is_function:
            return self

        if self.is_value:
            return Expression.value(self[0].conjugate())

        if self.is_quantum_operator:
            if self.get("is_hermitian"):
                return self

            is_dagger = self.get("is_dagger", False) ^ True

            return Expression(
                self.head, self[0].dag, self[1], **{**self.attrs, "is_dagger": is_dagger}
            )

        if self.is_kronecker_product:
            return reduce(lambda acc, x: acc * x.dag, self.args[::-1], Expression.one())

        args = tuple(arg.dag for arg in self.args)
        return Expression(self.head, *args, **self.attrs)

    def __getitem__(self, index: int | slice) -> Any:
        """Makes the arguments of the expression directly accessible through `expression[i]`."""
        return self.args[index]

    def __hash__(self) -> int:
        if self.is_addition or self.is_multiplication:
            return hash((self.head, frozenset(self.args)))

        return hash((self.head, self.args))

    def __repr__(self) -> str:
        args = ", ".join(map(repr, self.args))
        attrs = ", ".join(f"{k}={v}" for k, v in self.attrs.items())

        return f"{self.head.value}({args}" + (f", {attrs}" if attrs else "") + ")"

    def __str__(self) -> str:
        return visualize_expression(self)

    def _repr_pretty_(self, p, _cycle) -> None:  # type: ignore
        """IPython method: Provide a friendly visualisation when using IPython/Jupyter notebook."""

        p.text(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expression):
            return NotImplemented

        lhs_args = set(self.args) if self.is_addition or self.is_multiplication else self.args
        rhs_args = set(other.args) if other.is_addition or other.is_multiplication else other.args

        return self.head == other.head and lhs_args == rhs_args and self.attrs == other.attrs

    # Algebraic operations
    def __add__(self, other: object) -> Expression:
        if not isinstance(other, Expression | Numeric):
            return NotImplemented

        # Promote numerial values to Expression.
        if isinstance(other, Numeric):
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
        # expression. However, we want to provide a friendly interaction to the users,
        # and the inaccessibility of Python's evaluation (without writing our own REPL)
        # forces to add the evaluation at this point.
        return evaluate_addition(Expression.add(*args))

    def __radd__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, Numeric):
            return Expression.value(other) + self

        return NotImplemented

    def __mul__(self, other: object) -> Expression:
        if not isinstance(other, Expression | Numeric):
            return NotImplemented

        # Promote numerical values to Expression.
        if isinstance(other, Numeric):
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
        # expression. However, we want to provide a friendly interaction to the users,
        # and the inaccessibility of Python's evaluation (without writing our own REPL)
        # forces to add the evaluation at this point.
        return evaluate_multiplication(Expression.mul(*args))

    def __rmul__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, Numeric):
            return Expression.value(other) * self

        return NotImplemented

    def __pow__(self, other: object) -> Expression:
        """Power involving quantum operators always promote expression to quantum operators."""

        if not isinstance(other, Expression | Numeric):
            return NotImplemented

        if isinstance(other, Numeric):
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

        # Power of power is a simple operation and can be evaluated here.
        if (
            self.is_quantum_operator
            and self.get("is_hermitian")
            and self.get("is_unitary")
            and isinstance(other, Expression)
            and other.is_value
            and other[0] == int(other[0])
        ):
            power = int(other[0]) % 2
            return self if power == 1 else Expression.one()

        # Power of power is an simple operation and can be evaluated here.
        # Whenever a quantum operator is present, the expression is promoted to
        # a quantum operator.
        if self.is_power:
            return Expression.pow(self[0], self[1] * other).as_quantum_operator()

        return Expression.pow(self, other).as_quantum_operator()

    def __rpow__(self, other: object) -> Expression:
        # Promote numerical types to expression.
        if isinstance(other, Numeric):
            return Expression.value(other) ** self

        return NotImplemented

    def __neg__(self) -> Expression:
        return -1 * self

    def __sub__(self, other: object) -> Expression:
        if not isinstance(other, Expression | Numeric):
            return NotImplemented

        return self + (-other)

    def __rsub__(self, other: object) -> Expression:
        if not isinstance(other, Expression | Numeric):
            return NotImplemented

        return (-self) + other

    def __truediv__(self, other: object) -> Expression:
        if not isinstance(other, Expression | Numeric):
            return NotImplemented

        return self * (other**-1)

    def __rtruediv__(self, other: object) -> Expression:
        if not isinstance(other, Numeric):
            return NotImplemented

        return other * (self**-1)  # type: ignore

    def __kron__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented

        if not (
            (self.is_zero or self.is_one or self.is_quantum_operator or self.is_kronecker_product)
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
        # expression. However, we want to provide a friendly interaction to the users,
        # and the inaccessibility of Python's evaluation (without writing our own REPL)
        # forces to add the evaluation at this point.
        return evaluate_kron(Expression.kron(self, other))

    def __matmul__(self, other: object) -> Expression:
        warnings.warn(
            "The `@` (`__matmul__`) operator will be deprecated. Use `*` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.__kron__(other)


def evaluate_addition(expr: Expression) -> Expression:
    if not expr.is_addition:
        return expr

    # Numerical values are combined in a single element.
    numerical_value_accumulator = Expression.zero()

    # Other expressions are kept in a dictionary `{"expr": coefficient}` to merge their numerical
    # coefficients.
    general_terms: dict[Expression, Expression] = dict()

    for term in expr.args:
        if term.is_value:
            numerical_value_accumulator += term

        elif term.is_multiplication and term[0].is_value:
            # Isolate the numerical coefficient from the other symbols.
            coef = term[0]
            elem = term[1] if len(term.args) == 2 else Expression.mul(*term[1:])

            general_terms[elem] = general_terms.get(elem, Expression.zero()) + coef

        else:
            general_terms[term] = general_terms.get(term, Expression.zero()) + Expression.one()

    # The final terms are recombined multipling each one by their respective coefficients.
    args = tuple(elem * coef for elem, coef in general_terms.items())

    if not numerical_value_accumulator.is_zero:
        args = (numerical_value_accumulator, *args)

    return args[0] if len(args) == 1 else Expression.add(*args)


def evaluate_multiplication(expr: Expression) -> Expression:
    if not expr.is_multiplication:
        return expr

    # Numerical values are combined in a single element.
    numerical_value_accumulator = Expression.one()

    # Quantum operators are kept in a separated Kronecker product since their evaluation has
    # distinct rules.
    quantum_operators = Expression.one()

    # Other expressions are kept in a dictionary `{"expr": power}` to merge their numerical
    # power.
    general_terms: dict[Expression, Expression] = dict()

    for term in expr.args:
        if term.is_value:
            numerical_value_accumulator = numerical_value_accumulator * term

        elif term.is_quantum_operator or term.is_kronecker_product:
            quantum_operators = quantum_operators.__kron__(term)

        elif term.is_power:
            base, power = term[:2]
            general_terms[base] = general_terms.get(base, Expression.zero()) + power

        else:
            general_terms[term] = general_terms.get(term, Expression.zero()) + Expression.one()

    if numerical_value_accumulator.is_zero or quantum_operators.is_zero:
        return Expression.zero()

    # The final terms are recombined exponentiating each one by their respective powers.
    args = tuple(base**power for base, power in general_terms.items() if not power.is_zero)

    if not quantum_operators.is_one:
        args = (*args, quantum_operators)

    if not numerical_value_accumulator.is_one or len(args) == 0:
        args = (numerical_value_accumulator, *args)

    return args[0] if len(args) == 1 else Expression.mul(*args)


def evaluate_kron(expr: Expression) -> Expression:
    """Evaluate Kronecker product expressions."""

    lhs = expr[0]
    for rhs in expr[1:]:
        # Single operators multiplication, A ⊗ B
        if lhs.is_quantum_operator and rhs.is_quantum_operator:
            lhs = evaluate_kronop(lhs, rhs)

        # Left associativity, A ⊗ (B ⊗ C ⊗ D) = (A ⊗ B ⊗ C ⊗ D)
        elif lhs.is_quantum_operator and rhs.is_kronecker_product:
            lhs = evaluate_kronleft(lhs, rhs)

        # Right associativity, (A ⊗ B ⊗ C) ⊗ D = (A ⊗ B ⊗ C ⊗ D)
        elif lhs.is_kronecker_product and rhs.is_quantum_operator:
            lhs = evaluate_kronright(lhs, rhs)

        # Combine two Kronecker products, (A ⊗ B) ⊗ (C ⊗ D) = (A ⊗ B ⊗ C ⊗ D)
        elif lhs.is_kronecker_product and rhs.is_kronecker_product:
            lhs = evaluate_kronjoin(lhs, rhs)

        else:
            raise NotImplementedError

    return lhs  # type: ignore


def evaluate_kronleft(lhs: Expression, rhs: Expression) -> Expression:
    """Left associativity of the Kronecker product.

    Evaluate the Kronecker product between a LHS=quantum operators and a RHS=Kronecker product.
    """

    if not (lhs.is_quantum_operator or rhs.is_kronecker_product):
        raise SyntaxError("Only defined for a quantum operator and a Kronecker product.")

    args = rhs.args

    # Using a insertion-sort-like to add the LHS term in the the RHS product.
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

        if rhs_arg.subspace > lhs.subspace or rhs_arg.subspace.overlap_with(lhs.subspace):
            args = (*args[:i], lhs, *args[i:])
            break

        if i == len(args) - 1:
            args = (lhs, *args)

    if not args:
        return Expression.one()

    return args[0] if len(args) == 1 else Expression.kron(*args)  # type: ignore


def evaluate_kronright(lhs: Expression, rhs: Expression) -> Expression:
    """Right associativity of the Kronecker product.

    Evaluate the Kronecker product between a LHS=quantum operators and a RHS=Kronecker product.
    """

    if not (lhs.is_kronecker_product or rhs.is_quantum_operator):
        raise SyntaxError("Only defined for a Kronecker product and a quantum operator.")

    args = lhs.args

    # Using a insertion-sort-like to add the RHS term in the the LHS product.
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

        if args[i].subspace < rhs.subspace or args[i].subspace.overlap_with(rhs.subspace):
            args = (*args[:ii], rhs, *args[ii:])
            break

        if i == 0:
            args = (rhs, *args)

    if not args:
        return Expression.one()

    return args[0] if len(args) == 1 else Expression.kron(*args)  # type: ignore


def evaluate_kronjoin(lhs: Expression, rhs: Expression) -> Expression:
    """Evaluate the Kronecker product between a LHS=quantum operators and a RHS=Kronecker
    product.
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
        raise SyntaxError("Operation only valid for LHS and RHS both quantum operators.")

    # Multiplication of unitary Hermitian operators acting on the the same subspace.
    if lhs == rhs and (lhs.get("is_hermitian") and lhs.get("is_unitary")):
        return Expression.one()

    # General multiplications of operators acting on the same subspace.
    if lhs.subspace == rhs.subspace:
        if lhs.get("is_projector") and rhs.get("is_projector"):
            return lhs if lhs[0] == rhs[0] else Expression.zero()

        if lhs[0].is_function and rhs[0].is_function and lhs[0][0] == rhs[0][0] and lhs.get("join"):
            res = lhs.get("join")(
                lhs[0], rhs[0], lhs.get("is_dagger", False), rhs.get("is_dagger", False)
            )
            return (  # type: ignore
                res
                if res.is_zero or res.is_one
                else Expression.quantum_operator(res, lhs[1], **lhs.attrs)
            )

        # Simplify the multiplication of unitary Hermitian operators with fractional
        # power, e.g., `√X() * √X() == X()`.
        if (
            lhs[0].is_power
            and rhs[0].is_power
            and lhs[0][0] == rhs[0][0]  # both are the same operator
            and (lhs[0][0].get("is_hermitian") and lhs[0][0].get("is_unitary"))
        ):
            return lhs[0][0] ** (lhs[0][1] + rhs[0][1])  # type: ignore

    # Order the operators by subspace.
    if lhs.subspace < rhs.subspace or lhs.subspace.overlap_with(  # type: ignore
        rhs.subspace  # type: ignore
    ):
        return Expression.kron(lhs, rhs)

    return Expression.kron(rhs, lhs)


def visualize_expression(expr: Expression) -> str:
    """Stringfy expressions."""

    if expr.is_value or expr.is_symbol:
        return str(expr[0])

    if expr.is_quantum_operator:
        dag = "\u2020" if expr.get("is_dagger") else ""
        if expr[0].is_symbol or expr[0].is_function:
            return f"{expr[0]}{dag}{expr[1]}"
        return f"{expr[0]}"

    if expr.is_function:
        args = ",\u2009".join(map(str, expr[1:]))
        return f"{expr[0]}({args})"

    if expr.is_multiplication:
        result = visualize_sequence(expr, "\u2009*\u2009")
        return sub(r"-1\.0(\s\*)?\s", "-", result)

    if expr.is_kronecker_product:
        return visualize_sequence(expr, "\u2009*\u2009")

    if expr.is_addition:
        result = visualize_sequence(expr, " + ", with_brackets=False)
        return sub(r"\s\+\s-(1\.0(\s\*)?\s)?", " - ", result)

    if expr.is_power:
        return visualize_sequence(expr, "\u2009^\u2009")

    return repr(expr)


def visualize_sequence(expr: Expression, operator: str, with_brackets: bool = True) -> str:
    """Stringfy the arguments of an expression `expr` with the designed `operator`.

    The `with_brackets` option wrap any argument that is either a multiplication or a sum.
    """

    if expr.is_value or expr.is_symbol or (expr.is_quantum_operator and expr[0].is_symbol):
        raise SyntaxError("Only a sequence of expressions is allowed.")

    if with_brackets:
        return operator.join(map(visualize_with_brackets, expr.args))

    return operator.join(map(str, expr.args))


def visualize_with_brackets(expr: Expression) -> str:
    """Stringfy addition and multiplication expression surrounded by brackets."""

    if expr.is_multiplication or expr.is_addition:
        return f"({str(expr)})"

    return str(expr)
