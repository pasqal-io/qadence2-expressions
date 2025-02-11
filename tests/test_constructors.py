from __future__ import annotations

import pytest

from qadence2_expressions import (
    Expression,
    Support,
    array_parameter,
    array_variable,
    function,
    parameter,
    parametric_operator,
    projector,
    symbol,
    unitary_hermitian_operator,
    value,
    variable,
)


def test_constructor() -> None:
    assert array_parameter("arr_par", size=5) == Expression(
        Expression.Tag.SYMBOL, "arr_par", size=5
    )
    assert array_variable("arr_var", size=5) == Expression(
        Expression.Tag.SYMBOL, "arr_var", size=5, trainable=True
    )
    assert value(1) == Expression(Expression.Tag.VALUE, 1)
    with pytest.raises(TypeError):
        value("Non-numerical type.")  # type: ignore [arg-type]
    assert symbol("x") == Expression(Expression.Tag.SYMBOL, "x")
    with pytest.raises(SyntaxError):
        symbol("E")
    assert parameter("phi") == Expression(Expression.Tag.SYMBOL, "phi")
    assert projector("Z", "0")(0) == Expression(
        Expression.Tag.QUANTUM_OP,
        Expression.symbol("Z{0}"),
        Support(0),
        base="Z",
        is_projector=True,
        is_hermitian=True,
    )
    assert variable("psi") == Expression(Expression.Tag.SYMBOL, "psi", trainable=True)

    assert function("sin", 3.14) == Expression(Expression.Tag.FN, Expression.symbol("sin"), 3.14)
    assert unitary_hermitian_operator("X")(1) == Expression(
        Expression.Tag.QUANTUM_OP,
        Expression.symbol("X"),
        Support(1),
        is_hermitian=True,
        is_unitary=True,
    )
    assert parametric_operator("RX", 3.14)(1) == Expression(
        Expression.Tag.QUANTUM_OP, Expression.function("RX", 3.14), Support(1), join=None
    )
