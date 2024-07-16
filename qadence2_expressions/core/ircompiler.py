from __future__ import annotations

from typing import Any

from .expression import Expression
from .primitives import get_grid_scale, get_grid_type, get_qubits_positions

from qadence_ir.ir import *


def irc(expr: Expression) -> Model:
    return Model(
        register=qubits_allocation(expr),
        inputs=extract_inputs(expr),
        instructions=extract_instructions(expr),
    )


def qubits_allocation(expr: Expression) -> AllocQubits:
    pos = get_qubits_positions() or []
    num_qubits = expr.max_index + 1

    if pos and num_qubits > len(pos):
        raise ValueError(
            "The expression requires more qubits than are allocated in the register."
        )

    num_qubits = max(num_qubits, len(pos))

    grid_type = get_grid_type()
    grid_scale = get_grid_scale()

    return AllocQubits(num_qubits, pos, grid_type=grid_type, grid_scale=grid_scale)  # type: ignore


def extract_inputs(expr: Expression) -> dict[str, Alloc]:
    inputs: dict[str, Alloc] = dict()
    _extract_inputs_core(expr, inputs)
    return inputs


def _extract_inputs_core(expr: Expression, inputs: dict[str, Alloc]) -> None:
    if expr.is_symbol:
        inputs[expr[0]] = Alloc(expr.get("size", 1), expr.get("trainable", False))

    elif expr.is_addition or expr.is_multiplication or expr.is_kronecker_product:
        for arg in expr.args:
            _extract_inputs_core(arg, inputs)

    elif expr.is_function:
        for arg in expr[1:]:
            _extract_inputs_core(arg, inputs)

    elif expr.is_quantum_operator and expr[0].is_function:
        fn = expr[0]
        for arg in fn[1:]:
            _extract_inputs_core(arg, inputs)


def extract_instructions(expr: Expression) -> list[QuInstruct | Assign]:
    acc: list[QuInstruct | Assign] = []

    if expr.is_quantum_operator or expr.is_kronecker_product:
        _extract_quantum_instructions(expr, {}, acc)

    else:
        _extract_classical_instructions(expr, {}, acc)

    return acc


def _extract_quantum_instructions(
    expr: Expression, mem: dict, acc: list, count: int = 0
) -> tuple[Any, int]:
    if expr.is_quantum_operator and expr[0].is_symbol:
        sym = expr[0]
        operator_name = sym[0].lower()
        support = Support(target=expr[1].target, control=expr[1].control)
        acc.append(QuInstruct(operator_name, support))

    elif expr.is_quantum_operator and expr[0].is_function:
        fn = expr[0]
        operator_name = fn[0][0].lower()
        support = Support(target=expr[1].target, control=expr[1].control)
        args = []
        for arg in fn[1:]:
            term, count = _extract_classical_instructions(arg, mem, acc, count)
            args.append(term)
        acc.append(QuInstruct(operator_name, support, *args))

    elif expr.is_kronecker_product:
        for term in expr.args:
            _, count = _extract_quantum_instructions(term, mem, acc, count)

    return None, count


def _extract_classical_instructions(
    expr: Expression, mem: dict, acc: list, count: int = 0
) -> tuple[Any, int]:
    if expr in mem:
        return mem[expr], count

    if expr.is_value:
        return expr[0], count

    if expr.is_symbol:
        return Load(expr[0]), count

    if expr.is_power:
        base, count = _extract_classical_instructions(expr[0], mem, acc, count)
        power, count = _extract_classical_instructions(expr[1], mem, acc, count)

        label = f"%{count}"
        acc.append(Assign(label, Call("pow", base, power)))
        count += 1

    elif expr.is_multiplication:
        lhs, count = _extract_classical_instructions(expr[0], mem, acc, count)
        rhs, count = _extract_classical_instructions(expr[1], mem, acc, count)

        label = f"%{count}"
        acc.append(Assign(label, Call("mul", lhs, rhs)))
        count += 1
        for arg in expr[2:]:
            lhs = Load(label)
            rhs, count = _extract_classical_instructions(arg, mem, acc, count)
            label = f"%{count}"
            acc.append(Assign(label, Call("mul", lhs, rhs)))
            count += 1

    elif expr.is_addition:
        lhs, count = _extract_classical_instructions(expr[0], mem, acc, count)
        rhs, count = _extract_classical_instructions(expr[1], mem, acc, count)

        label = f"%{count}"
        acc.append(Assign(label, Call("add", lhs, rhs)))
        count += 1
        for arg in expr[2:]:
            lhs = Load(label)
            rhs, count = _extract_classical_instructions(arg, mem, acc, count)
            label = f"%{count}"
            acc.append(Assign(label, Call("add", lhs, rhs)))
            count += 1

    elif expr.is_function:
        fn_name = expr[0][0]
        args = []
        for arg in expr[1:]:
            term, count = _extract_classical_instructions(arg, mem, acc, count)
            args.append(term)
        label = f"%{count}"
        acc.append(Assign(label, Call(fn_name, *args)))
        count += 1

    mem[expr] = Load(label)
    return Load(label), count
