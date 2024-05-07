from __future__ import annotations

import pyqtorch as pyq
import torch

from qadence2_expressions import QSymbol, Symbol
from qadence2_expressions.expr import Expr


def parse_instruction(instruction: QSymbol) -> pyq.Primitive:
    native = getattr(pyq, instruction.name)
    if instruction.params != ():
        return native(instruction.support, instruction.params[0].name)
    else:
        return native(*instruction.support)


def parse_expression(expr: Expr) -> pyq.QuantumCircuit:
    instructions = list(map(parse_instruction, expr.args))
    return pyq.QuantumCircuit(2, instructions)


if __name__ == "__main__":
    x = QSymbol("X")(1)
    rx = QSymbol("RX", Symbol("theta"))(0)
    cnot = QSymbol("CNOT")(0, 1)
    pyqcirc = parse_expression(rx * x * cnot)
    print(pyqcirc(pyq.zero_state(2), {"theta": torch.rand(1)}))
