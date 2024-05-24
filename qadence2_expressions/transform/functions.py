"""
This module provides basic implementation of functions as symbols to be extened.
"""

from __future__ import annotations

from typing import get_args

# Only for examples for the moment.
# TODO: Remove default backend for functions.
import numpy as backend

from ..expr import Expr, Numeric, Numerical, Operator


def sin(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, get_args(Numerical)):
        return getattr(backend, sin.__name__)(x)  # type: ignore
    return Expr(Operator.CALL, sin.__name__, x)


def cos(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, get_args(Numerical)):
        return getattr(backend, cos.__name__)(x)  # type: ignore
    return Expr(Operator.CALL, cos.__name__, x)


def exp(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, get_args(Numerical)):
        return getattr(backend, exp.__name__)(x)  # type: ignore
    return Expr(Operator.CALL, exp.__name__, x)


def log(x: Numeric | Numerical) -> Numeric | Numerical:
    if isinstance(x, get_args(Numerical)):
        return getattr(backend, log.__name__)(x)  # type: ignore
    return Expr(Operator.CALL, log.__name__, x)
