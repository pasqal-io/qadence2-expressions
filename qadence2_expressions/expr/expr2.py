from __future__ import annotations

from typing import Any, Callable

from .qubit_support import Support


class Expression:
    class Token:
        # Identifiers:
        VALUE = "Value"
        SYMBOL = "Symbol"
        CALL = "Call"
        QUANTUM_OP = "QuantumOperator"

        # Operations:
        ADD = "Add"
        MUL = "Multiply"
        POW = "Power"
        KRON = "KroneckerProduct"

    def __init__(self, head: str, *args: Any, **kwargs: Any) -> None:
        self.head = head
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        args = ", ".join(map(str, self.args))
        return f"{self.head}({args})"

    def __hash__(self) -> int:
        if self.is_addition() or self.is_multiplication():
            return hash((self.head, frozenset(self.args)))

        return hash((self.head, self.args))

    # Alternative constructors.
    @classmethod
    def zero(cls) -> Expression:
        return cls(Expression.Token.VALUE, 0)

    @classmethod
    def one(cls) -> Expression:
        return cls(Expression.Token.VALUE, 1)

    @classmethod
    def value(cls, val: complex | float | int) -> Expression:
        return cls(Expression.Token.VALUE, val)

    @classmethod
    def symbol(cls, name: str) -> Expression:
        return cls(Expression.Token.SYMBOL, name)

    @classmethod
    def call(cls, func_name: str, *args: Any) -> Expression:
        return cls(Expression.Token.CALL, func_name, *args)

    @classmethod
    def quantum_op(cls, name: str, support: Support, **properties: Any) -> Expression:
        return cls(Expression.Token.QUANTUM_OP, name, support, **properties)

    @classmethod
    def add(cls, *args: Any) -> Expression:
        return cls(Expression.Token.ADD, *args)

    @classmethod
    def mul(cls, *args: Any) -> Expression:
        return cls(Expression.Token.MUL, *args)

    @classmethod
    def pow(cls, base: Expression, power: Expression) -> Expression:
        return cls(Expression.Token.POW, base, power)

    @classmethod
    def kron(cls, *args: Any) -> Expression:
        return cls(Expression.Token.KRON, *args)

    # Boolean predicates.
    def is_zero(self) -> bool:
        return self == Expression.zero()
    
    def is_one(self) -> bool:
        return self == Expression.one()
    
    def is_value(self) -> bool:
        return self.head == Expression.Token.VALUE

    def is_symbol(self) -> bool:
        return self.head == Expression.Token.SYMBOL

    def is_call(self) -> bool:
        return self.head == Expression.Token.CALL

    def is_quantum_operator(self) -> bool:
        return self.head == Expression.Token.QUANTUM_OP

    def is_addition(self) -> bool:
        return self.head == Expression.Token.ADD

    def is_multiplication(self) -> bool:
        return self.head == Expression.Token.MUL

    def is_power(self) -> bool:
        return self.head == Expression.Token.POW

    def is_kronecker_product(self) -> bool:
        return self.head == Expression.Token.KRON

    # Python magic methods.
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Expression):
            return NotImplemented

        # Compare expressions of the same type
        if self.head == value.head:
            return (
                set(self.args) == set(value.args)
                if self.is_addition() or self.is_multiplication()
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
        if self.is_zero():
            return other

        if other.is_zero():
            return self

        # Numerical values are added right away.
        if self.is_value() and other.is_value():
            return Expression.value(self.args[0] + other.args[0])

        # Combine arguments when LHS and RHS are both addition expressions.
        elif self.is_addition() and other.is_addition():
            args = (*self.args, *other.args)

        # Append the RHS term to LHS when the LHS is an addition expression.
        elif self.is_addition():
            args = (*self.args, other)

        # Prepend the LHS to the RHS when RHS is an addition expression.
        elif other.is_addition():
            args = (self, *other.args)

        # General case.
        else:
            args = (self, other)

        # TODO: Find a smart way to toogle the arguments reduction.
        result = Expression.add(*args)
        return reduce_addition(result)

    def __radd__(self, other: object) -> Expression:
        return self + other

    def __mul__(self, other: object) -> Expression:
        """
        Gives high precedence to Kronecker multiplication over regular
        multiplications for symbols. Multiplication between values has higher
        precedence.
        """

        if not isinstance(other, Expression | complex | float | int):
            return NotImplemented

        # Promote numerical types to expressions
        if isinstance(other, complex | float | int):
            return self.__mul__(Expression.value(other))

        # Multiplication by zero.
        if self.is_zero() or other.is_zero():
            return Expression.zero()

        # One is indentity for multimplication.
        if self.is_one():
            return other

        if other.is_one():
            return self

        # Numerical values are multiplied right away.
        if self.is_value() and other.is_value():
            return Expression.value(self.args[0] * other.args[0])

        if (self.is_quantum_operator() or self.is_quantum_operator()) and (
            other.is_quantum_operator() or other.is_quantum_operator()
        ):
            return self @ other

        # Combine arguments when LHS and RHS are both multiplication expressions.
        if self.is_multiplication() and other.is_multiplication():
            args = [*self.args, *other.args]

        # Append the RHS term to LHS when the LHS is an multiplication expression.
        elif self.is_multiplication():
            args = [*self.args, other]

        # Prepend the LHS term to RHS when the RHS is an multiplication expression.
        elif other.is_multiplication():
            args = [self, *other.args]

        # General case.
        else:
            args = [self, other]

        # TODO: Find a smart way to toogle the arguments reduction.
        result = Expression.mul(*args)
        return reduce_multiplication(result)

    def __rmul__(self, other: object) -> Expression:
        if not isinstance(other, complex | float | int):
            return NotImplemented

        return self * other

    def __matmul__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented
        
        if self.is_one():
            return other
        
        if other.is_one():
            return self

        if self.is_quantum_operator() and other.is_quantum_operator():
            return self.__kron__(other)

        if self.is_kronecker_product() and other.is_quantum_operator():
            return self.__kronr__(other)

        if self.is_quantum_operator() and other.is_kronecker_product():
            return self.__kronl__(other)

        if self.is_kronecker_product() and other.is_kronecker_product():
            return self.__kron_join__(other)

        raise SyntaxError(
            "This operations is only defined for quantum operators and Kronecker product."
        )

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
        if isinstance(other, Expression) and self.is_value() and other.is_value():
            return Expression.value(self.args[0] ** other.args[0])

        if self.is_power():
            base, power = self.args[:2]
            return Expression.pow(base, power * other)

        return Expression.pow(self, other)

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

    # Helper methods.
    def __kron__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented

        if not (self.is_quantum_operator() or other.is_quantum_operator()):
            raise SyntaxError(
                "This operation is defined for both terms as QuantumOperators."
            )

        # Implement the identity for hermitian operators acting on same subspace.
        if self.kwargs.get("is_hermitian") and self == other:
            return Expression.one()

        self_support: Support = self.args[1]
        other_support: Support = other.args[1]

        # Return the Kronecker Product ordered by support
        if self_support < other_support or self_support.overlap_with(other_support):
            return Expression.kron(self, other)

        return Expression.kron(other, self)

    def __kronr__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented

        if not (self.is_kronecker_product() or other.is_quantum_operator()):
            raise SyntaxError(
                "This operation is defned for LHS = KronekerProduct and RHS = QuantumOperator."
            )

        lhs_args: tuple[Expression, ...] = self.args
        args = ()
        for i in range(len(lhs_args) - 1, -1, -1):
            ii = i + 1

            # Check if the supports overlap.
            if lhs_args[i].args[1].overlap_with(other.args[1]):
                res = lhs_args[i].__kron__(other)
                args = (
                    (*lhs_args[:i], *lhs_args[ii:])
                    if res == Expression.one()
                    else (*lhs_args[:i], res, *lhs_args[ii:])
                )
                break

            if i == 0:
                args = (other, *lhs_args)

        if not args:
            return Expression.one()

        return args[0] if len(args) == 1 else Expression.kron(*args)

    def __kronl__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented

        if not (self.is_quantum_operator() or other.is_kronecker_product()):
            raise SyntaxError(
                "This operation is defned for LHS = QuantumOperator and RHS = KronekerProduct."
            )

        rhs_args: tuple[Expression, ...] = other.args
        args = ()
        for i, term in enumerate(rhs_args):
            ii = i + 1

            # Check if the supports overlap.
            if self.args[1].overlap_with(term.args[1]):
                res = self.__kron__(term)
                args = (
                    (*rhs_args[:i], *rhs_args[ii:])
                    if res == Expression.one()
                    else (*rhs_args[:i], res, *rhs_args[ii:])
                )
                break

            if i == 0:
                args = (self, *rhs_args)

        if not args:
            return Expression.one()

        return args[0] if len(args) == 1 else Expression.kron(*args)

    def __kron_join__(self, other: object) -> Expression:
        if not isinstance(other, Expression):
            return NotImplemented

        if not (self.is_kronecker_product() or other.is_kronecker_product()):
            raise SyntaxError(
                "This operation is defned for both terms as KronekerProducts."
            )

        acc = self
        for term in other.args:
            if acc.is_one():
                acc = term
            elif term.is_one():
                continue
            elif acc.is_quantum_operator():
                acc = acc.__kron__(term)
            else:
                acc = acc.__kronr__(term)

        return acc


def reduce_addition(expr: Expression) -> Expression:
    if not expr.is_addition():
        raise SyntaxError("This function only apply to addition expressions.")

    numerical_value = Expression.zero()
    general_terms: dict[Expression, Expression] = {}

    for term in expr.args:
        match term.head:
            # Numerical types are comibined in a single term
            case Expression.Token.VALUE:
                numerical_value += term.args[0]

            # Multiplicative terms with numerical constants have theier coefficents combined.
            case Expression.Token.MUL:
                if term.args[0].is_value():
                    elem = (
                        term.args[1]
                        if len(term.args) == 2
                        else Expression.mul(*term.args[1:])
                    )
                    general_terms[elem] = (
                        general_terms.get(elem, Expression.zero()) + term.args[0]
                    )

                else:
                    general_terms[term] = (
                        general_terms.get(term, Expression.zero()) + Expression.one()
                    )

            case _:
                general_terms[term] = (
                    general_terms.get(term, Expression.zero()) + Expression.one()
                )

    expr_term = [
        term * coef for term, coef in general_terms.items() if coef != Expression.zero()
    ]

    if not expr_term:
        return numerical_value

    if numerical_value == Expression.zero():
        return expr_term[0] if len(expr_term) < 2 else Expression.add(*expr_term)

    return Expression.add(numerical_value, *expr_term)


def reduce_multiplication(expr: Expression) -> Expression:
    if not expr.is_multiplication():
        raise SyntaxError("This function only apply to multiplication expressions.")

    numerical_value = Expression.one()
    quantum_ops = Expression.one()
    general_terms: dict[Expression, Expression] = {}

    for term in expr.args:
        match term.head:
            # Numerical types are comibined in a single term
            case Expression.Token.VALUE:
                numerical_value *= term.args[0]

            # Accumulate quantum operators.
            case Expression.Token.QUANTUM_OP | Expression.Token.KRON:
                quantum_ops = term if not quantum_ops else quantum_ops @ term

            # Powered terms are added to the general term combining the powers.
            case Expression.Token.POW:
                base, power = term.args[:2]
                general_terms[base] = general_terms.get(base, Expression.zero()) + power

            case _:
                general_terms[term] = (
                    general_terms.get(term, Expression.zero()) + Expression.one()
                )

    expr_terms: list[Expression] = [
        b**p for b, p in general_terms.items() if p != Expression.zero()
    ]

    if quantum_ops != Expression.one():
        expr_terms.append(quantum_ops)

    if not expr_terms:
        return numerical_value

    if numerical_value == Expression.one():
        return expr_terms[0] if len(expr_terms) < 2 else Expression.mul(*expr_terms)

    return Expression.mul(numerical_value, *expr_terms)


# def reduce_noncommutative_multiplication(expr: Expression) -> Expression:
#     pass


# =====
# UTILS
# =====
def symbol(identfier: str) -> Expression:
    return Expression.symbol(identfier)


def value(val: complex | float | int) -> Expression:
    return Expression.value(val)


def function(name: str, *args: Any) -> Expression:
    return Expression.call(name, *args)


def hermitian_operator(name: str) -> Callable:
    def core(
        *indices: Any,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> Expression:
        support = Support(*indices, target=target, control=control)
        return Expression.quantum_op(name, support, is_hermitian=True)

    return core
