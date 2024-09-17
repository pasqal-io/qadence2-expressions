from __future__ import annotations

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

from qadence2_expressions import (
    RX,
    Z,
    compile_to_model,
    parameter,
)


def test_ir_compilation() -> None:
    theta = parameter("theta")
    expr = Z() * RX(theta / 2)(0)
    model = compile_to_model(expr)

    goal = Model(
        register=AllocQubits(num_qubits=1),
        inputs={"theta": Alloc(1, trainable=False)},
        instructions=[
            QuInstruct("z", Support.target_all()),
            Assign("%0", Call("mul", 0.5, Load("theta"))),
            QuInstruct("rx", Support(target=(0,)), Load("%0")),
        ],
    )

    assert model == goal
