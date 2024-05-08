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
            _, symbol, sequence = instructions
            return native_operator(sequence, symbol.name)
        else:
            return native_operator(instructions)

    elif isinstance(expr_or_symbol, QSymbol):
        native = getattr(pyq, expr_or_symbol.name)
        if expr_or_symbol.params != ():
            if len(expr_or_symbol.params) > 1:
                raise NotImplementedError(
                    "Gates with more than one parameter not supported."
                )
            symbol = expr_or_symbol.params[0]
            return native(expr_or_symbol.support, symbol.name)
        else:
            return native(*expr_or_symbol.support)
    elif isinstance(expr_or_symbol, (Symbol, int)):
        return expr_or_symbol

    else:
        raise NotImplementedError(f"Not supported operation: {expr_or_symbol}")


if __name__ == "__main__":
    x = QSymbol("X")(1)
    rx = QSymbol("RX", Symbol("theta"))(0)
    cnot = QSymbol("CNOT")(0, 1)
    pyqcirc = parse_expression(Symbol("a") * (rx * x * cnot))
    print(pyqcirc(pyq.zero_state(2), {"theta": torch.rand(1), "a": torch.rand(1)}))
