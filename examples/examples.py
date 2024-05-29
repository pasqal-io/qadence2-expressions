# %%
from __future__ import annotations

from IPython.lib.pretty import pretty

from qadence2_expressions import *  # ruff: noqa: F403
from qadence2_expressions.transform import collect_operators


def evaluate_single_expression(expr: str) -> None:
    inp = ""
    out = "# "
    sexpr = expr.split(" = ", 1)
    if len(sexpr) == 2:
        exec(expr, globals())  # pylint: disable=W0122
        print(f"{inp}{expr}")
        print(f"{out}{eval(sexpr[0].strip())}")  # pylint: disable=W0123
    elif len(sexpr) == 1:
        print(f"{inp}{expr}")
        print(f"{out}{pretty(eval(expr))}")  # pylint: disable=W0123
    print()


def evaluate_expressions(*exprs):
    for expr in exprs:
        evaluate_single_expression(expr)


# %%
# Basic symbol examples.
evaluate_expressions(
    "a = Symbol('a')",
    "b = Symbol('b')",
    "a + a",
    "a - a",
    "a / a",
    "a + b",
    "a / (2*b)",
    "a ** 0",
    "a ** 1",
    "2 ** (a + b)",
)


# %%
# Product of sums is automatically expanded.
evaluate_expressions("(a + b) * (a + b)")


# %%
# However, power of sums are not automatically expanded to prioritise power
# simplifications.
evaluate_expressions(
    "(a + b) * (a + b) ** 2 / (a + b)",
    "(a + b) ** b",
)


# %%
# Minimal replace function. This functions still under development and may not
# present the expected behaviour.
evaluate_expressions(
    "x = a + b",
    "y = a + 2 * cos(x) ** 2",
    "z = replace(y, {a: 2})",
    "replace(z, {b: 1.1415926535897931})",
    "replace(y, {a: 2*b, b: a})",
    "replace(y, {b+a: 2*b})",
    "replace(2 ** (a+b), {a: 2*b})",
)


# %%
# Quantum operators
evaluate_expressions(
    "X = QSymbol('X')",
    "Y = QSymbol('Y')",
    "Z = QSymbol('Z')",
    "Cnot = QSymbol('CNOT', ordered_support=True)",
    "Swap = QSymbol('SWAP')",
    "Rx = lambda angle : QSymbol('Rx', angle, is_hermitian=False)",
    "Ry = lambda angle : QSymbol('Ry', angle, is_hermitian=False)",
)


# %%
evaluate_expressions(
    "X * (cos(a) * X + 1j * sin(a) * Y) / 2",
    "X(1) * (cos(a) * X() + 1j * sin(a) * Y()) * Z(1) / 2",
    "Y(4) * X(3) * Y(5,4) * Cnot(1,2) * Z(3)",
    "h = 2 * Rx(a)(0) + 1j * Y(3)",
    "h.dag",
    "h = Y(2) * Rx(a)(3).dag * Ry(b)(0,2) * X(3)",
    "h.dag",
    "(X(2) * (cos(a) * X() + 1j * sin(a) * Y(2)) *Z(2) / 2).dag",
    "nn = lambda k, l: (1 - Z(k)) * (1 - Z(l)) / 4",
    "nn(a,b)",
    "nn(a,a) == (1 - Z(a)) / 2",
    "sum(cos(a) * X(i) - sin(a) * Y(i) - b * Z(i) for i in range(2))",
    "z = 2 * exp(X(1) + X(2))",
    "replace(z, {exp(X(1) + X(2)): exp(X(1)) * exp(X(2))})",
)


# %%
evaluate_expressions(
    "phi = Symbol('phi')",
    "h1 = Z(0) * Z(1)",
    "h2 = Z(1) * Z(2)",
    "h3 = cos(phi) * h1 + 1j * sin(phi) * h2",
    "collect_operators(h1 - h3 + Z(1))",
)


# %%
def valid_transformation(lhs, rhs) -> bool:
    lhs_coefs = set(collect_operators(lhs).items())
    rhs_coefs = set(collect_operators(rhs).items())
    # False if a operator appears on both sides with
    # the same coefficient.
    return not (lhs_coefs & rhs_coefs)


evaluate_expressions(
    "valid_transformation(h1, h1 - h2)",
    "valid_transformation(h1, h1 - h3)",
)


# %%
