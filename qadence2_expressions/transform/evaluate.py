from __future__ import annotations

from typing import Iterable

from ..expr import Expr, Numeric, Numerical, Operator
from . import functions as fun


def prod(iterable: Iterable) -> Numeric | Numerical:
    """ "Equivalement of `sum` but for multiplication."""

    acc = 1
    for el in iterable:
        acc = acc * el
    return acc


def evaluate(value: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(value, Expr):
        args = [evaluate(elem) for elem in value.args]
        match value.head:
            case Operator.TIMES | Operator.NONCOMMUTE:
                return prod(args)
            case Operator.PLUS:
                return sum(args)
            case Operator.POWER:
                return args[0] ** args[1]
            case Operator.CALL:
                return getattr(fun, args[0])(*args[1:])  # type: ignore
            case _:
                raise NotImplementedError(f"Operator {value.head} not implemented.")

    return value
