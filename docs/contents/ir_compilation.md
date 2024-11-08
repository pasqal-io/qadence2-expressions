# Intermediate Representation compilation

Qadence 2 expression package provides compilation functionality to target Qadence 2 Intermediate Representation (IR) defined [here](https://github.com/pasqal-io/qadence2-ir). Please note that the IR follows [SSA form](https://en.wikipedia.org/wiki/Static_single-assignment_form) for classical computations.


In following is a pure digital program with local possibly parametrized gates compiled to the IR model.


```python exec="on" source="material-block" result="json" session="compilation"
from qadence2_expressions import *

a = parameter('a')
b = parameter('b')

phi = variable("phi")

expr = RX(a * phi / 2)(2) * Z(1) * RY(b * phi / 2)(0)

reset_ir_options()
ir = compile_to_model(expr)

print(f"{ir}")  # markdown-exec: hide
```

Similar example with interleaved global gates.

```python exec="on" source="material-block" result="json" session="compilation"
expr = RX(a * phi / 2)(2) * CZ() * RY(b * phi / 2)(0)

ir = compile_to_model(expr)

print(str(ir))  # markdown-exec: hide
```

Options can be set at any point to supplement the model to be recompiled.

```python exec="on" source="material-block" result="json" session="compilation"
set_qubits_positions([(-2, 1), (0, 0), (3, 1)])
set_grid_type("triangular")

ir = compile_to_model(expr)

print(str(ir))  # markdown-exec: hide
```

Pure analog programs can be constructed using `NativeDrive` and `FreeEvolution` operations that leave their concrete definitions and implementations to the backend. They can accept arbitrary combinations of single valued or arrays of parameters.

```python exec="on" source="material-block" result="json" session="compilation"
set_qubits_positions([(-1,0), (-1, 1), (1, 0), (1, 1)])
set_grid_type("triangular")

t = variable("t")
omega = array_variable("omega", 4)
detuning = array_variable("detuning", 3)
phase = parameter("phase")

expr = (
    NativeDrive(t / 2, omega, detuning, phase)()
    * FreeEvolution(2.5)()
    * NativeDrive(t / 2, omega, -detuning, phase)()
)

ir = compile_to_model(expr)

print(str(ir))  # markdown-exec: hide
```
