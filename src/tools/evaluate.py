from ..core import Expr, Operator
from . import functions as fun


def prod(iterable):
    acc = 1
    for el in iterable:
        acc = acc * el
    return acc


def evaluate(value):
    if isinstance(value, Expr):
        args = [evaluate(elem) for elem in value.args]
        match value.head:
            case Operator.TIMES | Operator.NONCOMMUTE:
                return prod(args)
            case Operator.ADD:
                return sum(args)
            case Operator.POWER:
                return args[0] ** args[1]
            case Operator.CALL:
                return getattr(fun, args[0])(*args[1:])
            case _:
                raise NotImplementedError(f"Operator {value.head} not implemented.")

    return value
