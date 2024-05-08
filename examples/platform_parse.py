from __future__ import annotations

from functools import reduce
from operator import mul

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


def hea(n_qubits: int) -> Expr:
    def idx():
        _idx = 0
        while True:
            yield _idx
            _idx += 1

    def get_idx():
        yield from idx()

    idx_generator = get_idx()
    return reduce(
        mul,
        [
            QSymbol(op, Symbol(p + str(next(idx_generator))))(qubit)
            for op, p in zip(["RX", "RY", "RX"], ["theta_" for _ in range(3)])
            for qubit in range(n_qubits)
        ]
        + [QSymbol("CNOT")(i % n_qubits, (i + 1) % n_qubits) for i in range(n_qubits)],
    )


def hea_example() -> None:
    ansatz = hea(2)
    pyqcirc = pyq.QuantumCircuit(2, parse_expression(ansatz))
    param_dict = {
        op.param_name: torch.rand(1, requires_grad=True)
        for op in pyqcirc.operations
        if isinstance(op, pyq.parametric.Parametric)
    }
    return pyqcirc(pyq.zero_state(2), param_dict)


def scale_example() -> None:
    x = QSymbol("X")(0)
    symbol_name = "scale"
    scale = Symbol(symbol_name)
    pyqscale = parse_expression(scale * x)
    return pyqscale(pyq.zero_state(1), {symbol_name: torch.rand(1)})


if __name__ == "__main__":
    print(scale_example())
    print(hea_example())
