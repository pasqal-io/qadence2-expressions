from ..expr import Expr, QSymbol, Operator


def collect_operators(expr) -> dict:
    acc = {}
    collect_operators_core(expr, acc)
    return acc


def collect_operators_core(expr, acc: dict):

    if isinstance(expr, QSymbol):
        acc[expr] = acc.get(expr, 0) + 1

    if isinstance(expr, Expr) and expr.head == Operator.NONCOMMUTE:
        acc[expr] = acc.get(expr, 0) + 1

    if (
        isinstance(expr, Expr)
        and expr.head == Operator.TIMES
        and isinstance(expr.args[-1], Expr)
        and expr.args[-1].head == Operator.NONCOMMUTE
    ):
        key = expr.args[-1]
        value = (
            expr.args[0]
            if len(expr.args[:-1]) == 1
            else Expr(Operator.TIMES, *expr.args[:-1])
        )
        acc[key] = acc.get(key, 0) + value

    if isinstance(expr, Expr) and expr.head == Operator.ADD:
        for arg in expr.args:
            collect_operators_core(arg, acc)
