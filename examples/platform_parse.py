from __future__ import annotations

import pyqtorch as pyq
import torch

from qadence2_expressions import QSymbol, Symbol
from qadence2_expressions.expr import Expr, Operator

OpMap = {
    Operator.ADD: pyq.Add,
    Operator.TIMES: pyq.Scale,
    Operator.NONCOMMUTE: pyq.Sequence,
}


def parse_expression(expr_or_symbol: Expr | QSymbol | Symbol) -> pyq.QuantumCircuit:
    if isinstance(expr_or_symbol, Expr):
        native_operator = OpMap[expr_or_symbol.head]
        instructions = list(map(parse_expression, expr_or_symbol.args))
        if expr_or_symbol.head == Operator.TIMES:
            _, param_name, sequence = instructions
            return native_operator(sequence, param_name.name)
        else:
            return native_operator(instructions)

    elif isinstance(expr_or_symbol, QSymbol):
        native = getattr(pyq, expr_or_symbol.name)
        if expr_or_symbol.params != ():
            return native(expr_or_symbol.support, expr_or_symbol.params[0].name)
        else:
            return native(*expr_or_symbol.support)
    elif isinstance(expr_or_symbol, (Symbol, int)):
        return expr_or_symbol

    else:
        raise TypeError(f"Not supported operation {expr_or_symbol}")


if __name__ == "__main__":
    x = QSymbol("X")(1)
    rx = QSymbol("RX", Symbol("theta"))(0)
    cnot = QSymbol("CNOT")(0, 1)
    pyqcirc = parse_expression(Symbol("a") * (rx * x * cnot))
    print(pyqcirc(pyq.zero_state(2), {"theta": torch.rand(1), "a": torch.rand(1)}))
