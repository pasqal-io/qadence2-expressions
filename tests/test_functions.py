from __future__ import annotations

from qadence2_expressions import (
    Expression,
    Support,
    cos,
    exp,
    log,
    parameter,
    sin,
    unitary_hermitian_operator,
    variable,
)

phi = parameter("phi")
psi = variable("psi")
X = unitary_hermitian_operator("X")


def test_sin() -> None:
    expr = phi + 3.14
    assert sin(expr) == Expression(
        Expression.Tag.FN,
        Expression.symbol("sin"),
        Expression.add(Expression.symbol("phi"), Expression.value(3.14))
    )


def test_cos() -> None:
    expr = psi - X(1)
    assert cos(expr) == Expression(
        Expression.Tag.FN,
        Expression.symbol("cos"),
        Expression.add(
            Expression.symbol("psi", trainable=True),
            Expression.mul(
                Expression.value(-1),
                Expression.quantum_operator(
                    Expression.symbol("X"),
                    Support(1),
                    is_hermitian=True,
                    is_unitary=True
                )
            )
        )
    )


def test_exp() -> None:
    expr = -2 * phi * X(1) + X(3)
    assert exp(expr) == Expression.quantum_operator(
        Expression.pow(
            Expression.symbol("E"),
            Expression.add(
                Expression.mul(
                    Expression.value(-2),
                    Expression.symbol("phi"),
                    Expression.quantum_operator(
                        Expression.symbol("X"),
                        Support(1),
                        is_hermitian=True,
                        is_unitary=True
                    )
                ),
                Expression.quantum_operator(
                    Expression.symbol("X"),
                    Support(3),
                    is_hermitian=True,
                    is_unitary=True,
                ),
            )
        ),
        Support(1, 3),  # Checking the full support is inferred correctly.
    )


def test_log() -> None:
    expr = psi * X(4)
    assert log(expr) == Expression(
        Expression.Tag.FN,
        Expression.symbol("log"),
        Expression.mul(
            Expression.symbol("psi", trainable=True),
            Expression.quantum_operator(
                Expression.symbol("X"),
                Support(4),
                is_hermitian=True,
                is_unitary=True,
            )
        )
    )
