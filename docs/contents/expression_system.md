# Expression system

Qadence 2 Expression system is designed to create expressive, self-contained and abstract symbolic expressions to represent quantum programs in the digital-analog paradigm. These expressions can be transpiled later with concretized and specific data types, such as `numpy`, `pytorch` and `jax` for execution on targeted backends.

The Expression system defines syntactic rules to generate symbolic quantum expressions, that can contain parametric expressions for **parameters** (static, `FeatureParameter`) and **variables** (dynamic, `VariationalParameter`) to be used for training purposes. Expression composition can be seamlessly applied to quantum operators for digital, analog and digital-analog computations. It also supports arithmetic operations for both classical and quantum expressions as well as reduction, simplification and replacement methods.


## Symbolic manipulation

In these examples, basic arithmetic expressions on symbols (parameters) are evaluated to illustrate simplifications and reductions.

```python exec="on" source="material-block" result="json" session="expressions"
from qadence2_expressions import *

a = parameter('a')
b = parameter('b')

print(f"a + a \u2192 {a + a}")  # markdown-exec: hide
print(f"a - a \u2192 {a - a}")  # markdown-exec: hide
print(f"a / a \u2192 {a / a}")  # markdown-exec: hide
print(f"a + b \u2192 {a + b}")  # markdown-exec: hide
print(f"a / (2*b) \u2192 {a / (2*b)}")  # markdown-exec: hide
print(f"a ** 0 \u2192 {a ** 0}")  # markdown-exec: hide
print(f"a ** 1 \u2192 {a ** 1}")  # markdown-exec: hide
print(f"2 ** (a + b' \u2192 {2 ** (a + b)}")  # markdown-exec: hide
```

Products of sums are expanded


```python exec="on" source="material-block" result="json" session="expressions"
(a + b) * (a + b)

print(f"\u2192 {(a + b) * (a + b)}")  # markdown-exec: hide
```

But exponentiations of sums are not as power simplifications take precedence.

```python exec="on" source="material-block" result="json" session="expressions"
(a + b) * (a + b) ** 2 / (a + b)

print(f"\u2192 {(a + b) * (a + b) ** 2 / (a + b)}\n")  # markdown-exec: hide
```

## Quantum operators

Standard quantum operators are defined as Python `Callable` that accept a qubit support as argument. Please note that the support can either be a single `int` for single qubit operations or a tuple of qubit indices for operations that span across multiple qubits or nothing to create global operations that span across the whole register (denoted by the `*` wildcard).

```python exec="on" source="material-block" result="json" session="expressions"
X(2) * Y() * Z(1,2)

print(f"\u2192 {X(2) * Y() * Z(1,2)}")  # markdown-exec: hide
```

(Multi-)Controlled operators need to be provided with non-overlapping tuples for control and target qubits. The notation convention is to display target indices first followed by control indices in increasing ordering.

```python exec="on" source="material-block" result="json" session="expressions"
NOT(control=(1,), target=(2,)) * NOT(target=(1,3), control=(2,4))

print(f"\u2192 {NOT(control=(1,), target=(2,)) * NOT(target=(1,3), control=(2,4))}")  # markdown-exec: hide
```

Quantum operators can be parametrized and expressions expanded.

```python exec="on" source="material-block" result="json" session="expressions"
X() * (cos(a) * X() + 1j * sin(a) * Y()) / 2

print(f"\u2192 {X() * (cos(a) * X() + 1j * sin(a) * Y()) / 2}")  # markdown-exec: hide
```

Global and local operators can be combined.

```python exec="on" source="material-block" result="json" session="expressions"
X(1) * (cos(a) * X() + 1j * sin(a) * Y()) * Z(1) / 2

print(f"\u2192 {X(1) * (cos(a) * X() + 1j * sin(a) * Y()) * Z(1) / 2}")  # markdown-exec: hide
```

Custom operators can be created as functions or based on other operators. For instance, the `CNOT`:

```python exec="on" source="material-block" result="json" session="expressions"
CNOT = lambda ctrl, tgt: NOT(target=(tgt,), control=(ctrl,))
Y(4) * X(3) * Y(5,4) * CNOT(1,2) * Z(3)

print(f"\u2192 {Y(4) * X(3) * Y(5,4) * CNOT(1,2) * Z(3)}")  # markdown-exec: hide
```

Or the number operator. Expansion rules still hold.

```python exec="on" source="material-block" result="json" session="expressions"
N = lambda k: (1 - Z(k)) / 2

sum(a * X(i) - b * Z(i) + N(i) * N(i + 1) for i in range(1))
print(f"\u2192 {sum(a * X(i) - b * Z(i) + N(i) * N(i + 1) for i in range(1))}")  # markdown-exec: hide
```

Parametric operators need to get passed a parameter as first argument, then the qubit support. This ensures syntactic consistency across operators. Unitarity still holds.

```python exec="on" source="material-block" result="json" session="expressions"
phi = variable("phi")

RX(phi / 2)(1) * RX(phi / 2)(1).dag
print(f"\u2192 {RX(phi / 2)(1) * RX(phi / 2)(1).dag}")  # markdown-exec: hide
```

Arithmetic operations still hold for operator parameters defined over the same support.

```python exec="on" source="material-block" result="json" session="expressions"
RX(phi / 2)(1) * RX(- phi / 2)(1)

print(f"\u2192 {RX(phi / 2)(1) * RX(- phi / 2)(1)}")  # markdown-exec: hide
```

As opposed to:

```python exec="on" source="material-block" result="json" session="expressions"
RX(phi / 2)(1) * RX(phi / 2)(2).dag

print(f"\u2192 {RX(phi / 2)(1) * RX(phi / 2)(2).dag}")  # markdown-exec: hide
```
