from __future__ import annotations

from typing import Iterable

from .core.expression import Expression


def prod(exprs: Iterable[Expression]) -> Expression:
    acc = Expression.one()
    for expr in exprs:
        acc = acc * expr
    return acc


def evaluate(expr: Expression) -> Expression:
    if expr.is_multiplication or expr.is_kronecker_product:
        return prod(evaluate(arg) for arg in expr.args)

    if expr.is_addition:
        return sum(evaluate(arg) for arg in expr.args)  # type: ignore

    if expr.is_power:
        return evaluate(expr[0]) ** evaluate(expr[1])

    if expr.is_quantum_operator and not (expr[0].is_symbol or expr[0].is_function):
        return Expression.quantum_operator(evaluate(expr[0]), expr[1], **expr.attrs)

    return expr


def replace(expr: Expression, rules: dict[Expression, Expression]) -> Expression:
    return evaluate(replace_core(expr, rules))


def replace_core(expr: Expression, rules: dict[Expression, Expression]) -> Expression:
    if expr in rules:
        return rules[expr]

    if expr.is_value or expr.is_symbol:
        return expr

    if expr.is_function:
        name = expr[0][0]
        args = tuple(replace_core(arg, rules) for arg in expr[1:])
        return Expression.function(name, *args)

    if expr.is_quantum_operator:
        support = expr[1]
        operator = replace_core(expr[0], rules)
        return Expression.quantum_operator(operator, support, **expr.attrs)

    args = tuple(replace_core(arg, rules) for arg in expr.args)
    return Expression(expr.head, *args, **expr.attrs)
