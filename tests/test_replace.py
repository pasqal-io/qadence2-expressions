from __future__ import annotations

# from qadence2_expressions import QSymbol, Symbol, replace


# def test_replace_symbol_by_symbol() -> None:
#     a = Symbol("a")
#     b = Symbol("b")

#     expr0 = 2 * a + b
#     expr1 = replace(expr0, {b: a})
#     assert expr1 == 3 * a


# def test_replace_symbol_by_valuel() -> None:
#     a = Symbol("a")
#     b = Symbol("b")

#     expr0 = 2 * a + b
#     expr1 = replace(expr0, {a: 2, b: -1})
#     assert expr1 == 3


# def test_replace_symbol_by_expression() -> None:
#     a = Symbol("a")
#     b = Symbol("b")

#     expr0 = 2 + a
#     expr1 = replace(expr0, {a: a + b})
#     expr2 = replace(expr1, {b: a})
#     expr3 = 2 * (1 + a)
#     assert expr2 == expr3


# def test_replace_expression_by_expression() -> None:
#     X = QSymbol("X")
#     Y = QSymbol("Y")
#     Z = QSymbol("Z")

#     expr0 = 2j * Y + X * Z
#     expr1 = replace(expr0, {X * Z: -2j * Y})
#     assert expr1 == 0
