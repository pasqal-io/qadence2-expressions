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
    cos,
    parameter,
)


def test_ir_compilation() -> None:
    theta = parameter("theta")
    expr = Z() * RX(cos(theta / 2))(0)
    model = compile_to_model(expr)

    goal = Model(
        register=AllocQubits(num_qubits=1),
        inputs={"theta": Alloc(1, trainable=False)},
        instructions=[
            QuInstruct("z", Support.target_all()),
            Assign("%0", Call("mul", 0.5, Load("theta"))),
            Assign("%1", Call("cos", Load("%0"))),
            QuInstruct("rx", Support(target=(0,)), Load("%1")),
        ],
    )

    assert model == goal
