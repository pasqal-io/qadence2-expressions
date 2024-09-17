from __future__ import annotations


from qadence2_expressions import (
    parameter,
    RX,
    compile_to_model,
)

from qadence2_ir.types import (
    Alloc,
    AllocQubits,
    Assign,
    Call,
    Load,
    Model,
    QuInstruct,
    Support,
)


def test_ir_compilation() -> None:
    theta = parameter("theta")
    expr = RX(theta / 2)(0)
    model = compile_to_model(expr)

    goal = Model(
        register=AllocQubits(num_qubits=1),
        inputs={'theta': Alloc(1, trainable=False)},
        instructions=[
            Assign('%0', Call('mul', 0.5, Load('theta'))),
            QuInstruct('rx', Support(target=(0,)), Load('%0')),
        ],
    )

    assert model == goal
