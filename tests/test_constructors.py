from __future__ import annotations

import pytest

from qadence2_expressions.core.constructors import (
    function,
    parameter,
    symbol,
    unitary_hermitian_operator,
    value,
    variable,
)
from qadence2_expressions.core.expression import Expression
from qadence2_expressions.core.support import Support


def test_constructor() -> None:
    assert value(1) == Expression(Expression.Tag.VALUE, 1)
    with pytest.raises(TypeError):
        value("Non-numerical type.")  # type: ignore [arg-type]
    assert symbol("x") == Expression(Expression.Tag.SYMBOL, "x")
    with pytest.raises(SyntaxError):
        symbol("E")
    assert parameter("phi") == Expression(Expression.Tag.SYMBOL, "phi")
    assert variable("phi") == Expression(Expression.Tag.SYMBOL, "phi")

    assert function("sin", 3.14) == Expression(Expression.Tag.FN, Expression.symbol("sin"), 3.14)
    assert unitary_hermitian_operator("X")(1) == Expression(
        Expression.Tag.QUANTUM_OP,
        Expression.symbol("X"),
        Support(1),
        is_hermitian=True,
        is_unitary=True,
    )
