from __future__ import annotations

from qadence2_expressions.core.constructors import (
    symbol,
    unitary_hermitian_operator,
    value,
)
from qadence2_expressions.core.expression import Expression
from qadence2_expressions.core.support import Support


def test_constructor() -> None:
    assert value(1) == Expression(Expression.Tag.VALUE, 1)
    assert Expression.symbol("x") == Expression(Expression.Tag.SYMBOL, "x")
    assert Expression.function("sin", 3.14) == Expression(
        Expression.Tag.FN, Expression.symbol("sin"), 3.14
    )
    assert Expression.quantum_operator(
        Expression.symbol("X"), Support(1), is_hermitian=True
    ) == Expression(
        Expression.Tag.QUANTUM_OP,
        Expression.symbol("X"),
        Support(1),
        is_hermitian=True,
    )


def test_addition() -> None:
    a = symbol("a")
    X = unitary_hermitian_operator("X")

    assert value(2) + 3 == value(5)
    assert a + 0 == a
    assert 0 + a == a
    assert a + 2 == Expression.add(value(2), a)
    assert a + a == Expression.mul(value(2), a)
    assert X() + 2 + a == Expression.add(value(2), a, X())


def test_negation() -> None:
    a = symbol("a")
    X = unitary_hermitian_operator("X")

    assert -value(2) == value(-2)
    assert -a == Expression.mul(value(-1), a)
    assert -X(1) == Expression.mul(value(-1), X(1))
    assert -X(2) * X(1) == Expression.mul(value(-1), Expression.kron(X(1), X(2)))


def test_subtraction() -> None:
    a = symbol("a")
    X = unitary_hermitian_operator("X")

    assert value(2) - value(3) == value(-1)
    assert a - 2 == Expression.add(value(-2), a)
    assert 2 - a == Expression.add(value(2), Expression.mul(value(-1), a))
    assert a - a == value(0)
    assert X(1) - X(1) == value(0)


def test_multiplication() -> None:
    a = symbol("a")
    X = unitary_hermitian_operator("X")

    assert 3 * value(2) == value(6)
    assert a * 2 == Expression.mul(value(2), a)
    assert X(1) * a * 2 == Expression.mul(value(2), a, X(1))
    assert X(1) * a * X(2) * 2 == Expression.mul(value(2), a, Expression.kron(X(1), X(2)))


def test_power() -> None:
    a = symbol("a")

    assert value(2) ** 3 == value(8)
    assert a**0 == Expression.one()
    assert a**1 == a
    assert a**2 == Expression.pow(a, value(2))
    assert 2**a == Expression.pow(value(2), a)


def test_division() -> None:
    a = symbol("a")

    assert 3 / value(2) == value(1.5)
    assert 1 / a == Expression.pow(a, value(-1))
    assert a / a == value(1)
    assert a / 2 == Expression.mul(value(0.5), a)


def test_kron() -> None:
    X = unitary_hermitian_operator("X")
    term = Expression.kron(X(1), X(2), X(4))

    # Push term from the right.
    assert term.__kron__(X(3)) == Expression.kron(X(1), X(2), X(3), X(4))

    # Push term from the left.
    assert X(3).__kron__(term) == Expression.kron(X(1), X(2), X(3), X(4))

    # Join `kron` expressions.
    term1 = Expression.kron(X(1), X(4))
    term2 = Expression.kron(X(2), X(3))

    assert term1.__kron__(term2) == Expression.kron(X(1), X(2), X(3), X(4))
    assert term2.__kron__(term1) == Expression.kron(X(1), X(2), X(3), X(4))


def test_commutativity() -> None:
    a = symbol("a")
    b = symbol("b")
    X = unitary_hermitian_operator("X")
    Y = unitary_hermitian_operator("Y")

    assert a * b - b * a == value(0)
    assert X(1) * Y(1) - Y(1) * X(1) == Expression.add(
        Expression.kron(X(1), Y(1)),
        Expression.mul(value(-1), Expression.kron(Y(1), X(1))),
    )
    assert X(1) * Y(2) - Y(2) * X(1) == value(0)


def test_operators_multiplication() -> None:
    X = unitary_hermitian_operator("X")
    Y = unitary_hermitian_operator("Y")

    assert X() * X() == value(1)
    assert X(1) * X(1) == value(1)
    assert X(1) * Y(2) * X(1) == Y(2)
    assert (X(1) * Y(2)) * (X(1) * Y(2)) == value(1)


def test_subspace_propagation() -> None:
    a = symbol("a")
    b = symbol("b")
    X = unitary_hermitian_operator("X")

    assert value(1).subspace is None
    assert a.subspace is None
    assert X().subspace == Support()
    assert X(1).subspace == Support(1)
    assert X(1, 2).subspace == Support(1, 2)
    assert X(target=(1,), control=(0,)).subspace == Support(control=(0,), target=(1,))

    expr = Expression.add(value(1), a)
    assert expr.subspace is None

    term1 = Expression.mul(a, X(1))
    term2 = Expression.mul(b, X(2))
    expr = Expression.add(term1, term2)
    assert expr.subspace == Support(1, 2)
