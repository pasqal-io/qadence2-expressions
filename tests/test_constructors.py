from __future__ import annotations

from pytest import raises

from qadence2_expressions.core.constructors import (
    function,
    symbol,
    unitary_hermitian_operator,
    value,
)


from qadence2_expressions.core.expression import Expression
from qadence2_expressions.core.support import Support


def test_constructor() -> None:
    assert value(1) == Expression(Expression.Tag.VALUE, 1)
    with raises(TypeError):
        value("Non-numerical type")
    assert symbol("x") == Expression(Expression.Tag.SYMBOL, "x")
    assert function("sin", 3.14) == Expression(
        Expression.Tag.FN, Expression.symbol("sin"), 3.14
    )
    assert unitary_hermitian_operator("X")(1) == Expression(
        Expression.Tag.QUANTUM_OP,
        Expression.symbol("X"),
        Support(1),
        is_hermitian=True,
        is_unitary=True,
    )
