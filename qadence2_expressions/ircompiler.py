from __future__ import annotations

from qadence2_ir import (
    AST,
    AbstractIRBuilder,
    AllocQubits,
    Attributes,
    irc_factory,
)

from .environment import (
    get_grid_options,
    get_grid_scale,
    get_grid_type,
    get_number_qubits,
    get_qpu_directives,
    get_qubits_positions,
    get_settings,
)
from .expression import Expression


class IRBuilder(AbstractIRBuilder[Expression]):
    @staticmethod
    def set_register(input_obj: Expression) -> AllocQubits:
        num_qubits_in_expr = input_obj.max_index + 1
        pos: list[tuple[int, int]] | list[int] = get_qubits_positions() or []  # type: ignore
        num_qubits_available = get_number_qubits()

        if pos and num_qubits_in_expr > num_qubits_available:
            raise ValueError(
                "The expression requires more qubits than are allocated in the register."
            )

        num_qubits = max(num_qubits_in_expr, num_qubits_available)

        grid_type = get_grid_type()
        grid_scale = get_grid_scale()
        options = get_grid_options() or {}

        return AllocQubits(
            num_qubits,
            pos,
            grid_type=grid_type,
            grid_scale=grid_scale,
            options=options,
        )

    @staticmethod
    def set_directives(input_obj: Expression) -> Attributes:
        return get_qpu_directives() or {}

    @staticmethod
    def settings(input_obj: Expression) -> Attributes:
        return get_settings() or {}

    @staticmethod
    def parse_sequence(input_obj: Expression) -> AST:
        if input_obj.is_value:
            return AST.numeric(input_obj[0])

        if input_obj.is_symbol:
            size = input_obj.get("size", 1)
            trainable = input_obj.get("trainable", False)
            attrs = {
                k: v
                for k, v in input_obj.attrs.items()
                if k not in ["size", "trainable"]
            }
            return AST.input_variable(input_obj[0], size, trainable, **attrs)

        if input_obj.is_function:
            name = input_obj[0]
            args = []
            for arg in input_obj[1:]:
                args.append(IRBuilder.parse_sequence(arg))
            return AST.callable(name, *args)

        if input_obj.is_quantum_operator:
            expr = input_obj[0]
            target = input_obj[1].target
            control = input_obj[1].control

            expression_exclusive_attributes = [
                "is_hermitian",
                "is_unitary",
                "is_projector",
                "join",
            ]
            attrs = {
                k: v
                for k, v in input_obj.attrs.items()
                if k not in expression_exclusive_attributes
            }

            if expr.is_symbol:
                return AST.quantum_op(expr[0], target, control, **attrs)

            elif expr.is_function:
                name = expr[0][0]
                args = []
                for arg in expr[1:]:
                    args.append(IRBuilder.parse_sequence(arg))
                return AST.quantum_op(name, target, control, *args, **attrs)

            else:
                raise SyntaxError("Quantum operator not ready to convert to IR")

        if input_obj.is_power:
            base = IRBuilder.parse_sequence(input_obj[0])
            power = IRBuilder.parse_sequence(input_obj[1])
            return AST.binary_op("pow", base, power)

        if input_obj.is_addition or input_obj.is_multiplication:
            op = "add" if input_obj.is_addition else "mul"
            acc = IRBuilder.parse_sequence(input_obj[0])
            for term in input_obj[1:]:
                rhs = IRBuilder.parse_sequence(term)
                acc = AST.binary_op_comm(op, acc, rhs)
            return acc

        if input_obj.is_kronecker_product:
            args = [IRBuilder.parse_sequence(arg) for arg in input_obj.args]
            return AST.sequence(*args)

        raise NotImplementedError(
            f"Expression {repr(input_obj)} is not convertible to IR"
        )


irc = irc_factory(IRBuilder)