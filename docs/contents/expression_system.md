# Expression system

Qadence 2 Expression system is designed to create expressive, self-contained and abstract symbolic expressions to represent quantum programs in the digital-analog paradigm. These expressions can be transpiled later with concretized and specific data types, such as `numpy`, `pytorch` and `jax` for execution on targeted backends.

The Expression system defines syntactic rules to generate symbolic quantum expressions, that can contain parametric expressions for **parameters** (static, `FeatureParameter`) and **variables** (dynamic, `VariationalParameter`) to be used for training purposes. Expression composition can be seamlessly applied to quantum operators for digital, analog and digital-analog computations. It also supports arithmetic operations for both classical and quantum expressions as well as reduction, simplification and replacement methods.


# Symbolic manipulation

In these examples, basic arithmetic expressions on symbols (parameters) are evaluated to illustrate simplifications and reductions.

```python exec="on" source="material-block" html="1" session="getting_started"
from qadence2_expressions import *

a = parameter('a')
b = parameter('b')

a + a
print(f"{a + a}")  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="getting_started"
a - a
print(f"{a - a}")  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="getting_started"
a / a
print(f"{a / a}")  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="getting_started"
a + b
print(f"{a + b}")  # markdown-exec: hide
```


```python exec="on" source="material-block" html="1" session="getting_started"
a / (2*b)
print(f"{a / (2*b)}")  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="getting_started"
a ** 0
print(f"{a ** 0}")  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="getting_started"
a ** 1
print(f"{a ** 1}")  # markdown-exec: hide
```

```python exec="on" source="material-block" html="1" session="getting_started"
2 ** (a + b)
print(f"{2 ** (a + b)}")  # markdown-exec: hide
```

Products of sums are expanded

```python exec="on" source="material-block" html="1" session="getting_started"
(a + b) * (a + b)
print(f"{(a + b) * (a + b)}")  # markdown-exec: hide
```

But exponentiations of sums are not as power simplifications take precedence.

```python exec="on" source="material-block" html="1" session="getting_started"
(a + b) * (a + b) ** 2 / (a + b)
print(f"{(a + b) * (a + b) ** 2 / (a + b)}\n")  # markdown-exec: hide
```

# Quantum operators

Standard quantum operators are defined as Python `Callable` that accept a qubit support as argument. Please note that the support can either be a single `int` for single qubit operations or a tuple of qubit indices for operations that span across multiple qubits or nothing to create global operations that span across the whole register (denoted by the `*` wildcard).

```python exec="on" source="material-block" html="1" session="getting_started"
X(2) * Y() * Z(1,2)
print(f"{X(2) * Y() * Z(1,2)}")  # markdown-exec: hide
```

(Multi-)Controlled operators need to be provided with non-overlapping tuples for control and target qubits. The notation convention is to display target indices first followed by control indices.

```python exec="on" source="material-block" html="1" session="getting_started"
NOT(control=(1,), target=(2,)) * NOT(target=(1,3), control=(2,4))
print(f"{NOT(control=(1,), target=(2,)) * NOT(target=(1,3), control=(2,4))}")  # markdown-exec: hide
```

Quantum operators can be parametrized and expressions expanded.

```python exec="on" source="material-block" html="1" session="getting_started"
X() * (cos(a) * X() + 1j * sin(a) * Y()) / 2
print(f"{X() * (cos(a) * X() + 1j * sin(a) * Y()) / 2}")  # markdown-exec: hide
```

Global and local operators can be combined.

```python exec="on" source="material-block" html="1" session="getting_started"
X(1) * (cos(a) * X() + 1j * sin(a) * Y()) * Z(1) / 2
print(f"{X(1) * (cos(a) * X() + 1j * sin(a) * Y()) * Z(1) / 2}")  # markdown-exec: hide
```

Custom operators can be created as functions or based on other operators. For instance, the `CNOT`:

```python exec="on" source="material-block" html="1" session="getting_started"
CNOT = lambda ctrl, tgt: NOT(target=(tgt,), control=(ctrl,))
Y(4) * X(3) * Y(5,4) * CNOT(1,2) * Z(3)
print(f"{Y(4) * X(3) * Y(5,4) * CNOT(1,2) * Z(3)}")  # markdown-exec: hide
```

Or the number operator. Expansion rules still hold.

```python exec="on" source="material-block" html="1" session="getting_started"
N = lambda k: (1 - Z(k)) / 2

sum(a * X(i) - b * Z(i) + N(i) * N(i + 1) for i in range(1))
print(f"{sum(a * X(i) - b * Z(i) + N(i) * N(i + 1) for i in range(1))}")  # markdown-exec: hide
```

Parametric operators need to get passed a parameter as first argument, then the qubit support. This ensures syntactic consistency across operators. Unitarity still holds.

```python exec="on" source="material-block" html="1" session="getting_started"
phi = variable("phi")

RX(phi / 2)(1) * RX(phi / 2)(1).dag
print(f"{RX(phi / 2)(1) * RX(phi / 2)(1).dag}")  # markdown-exec: hide
```

Arithmetic operations still hold for operator parameters defined over the same support.

```python exec="on" source="material-block" html="1" session="getting_started"
RX(phi / 2)(1) * RX(- phi / 2)(1)

print(f"{RX(phi / 2)(1) * RX(- phi / 2)(1)}")  # markdown-exec: hide
```

As opposed to:

```python exec="on" source="material-block" html="1" session="getting_started"
RX(phi / 2)(1) * RX(phi / 2)(2).dag

print(f"{RX(phi / 2)(1) * RX(phi / 2)(2).dag}")  # markdown-exec: hide
```

## The `expression` module

The `expression` module defines an `Expression` type as a symbolic representation for mathematical expressions together with arithmetic rules. It is syntactically constructed using [S-Expressions](https://en.wikipedia.org/wiki/S-expression) in prefix notation where the ordered parameters are:

- A tag as a Python `Enum`: a token identifier for variables, functions or operations.
- Arguments: a set of arguments to define or be passed to the expression.
- Attributes: keyword arguments for symbolic evaluation and compilation directives.

The `Expression` type defines constructors for four identifiers and operations variants:

- `VALUE`: A value type to hold numerical `complex`, `float` or `int` primitive types.
- `SYMBOL`: A symbol type for names definition.
- `FN`: A variadic function type defined as a symbolic name and arguments.
- `QUANTUM_OP`: A quantum operator type defined as an expression, a support of qubit resources and a collection of property attributes.
- `ADD`: A variadic addition type as the sum of arguments.
- `MUL`: A variadic multiplication type as the product of arguments.
- `KRON`: A variadic multiplication type as the product of arguments with commutative rules.
- `POW`: A power type as the exponentiation of a base and power arguments.


## The `environment` module

 The `environment` module defines an `Environment` type that plays a similar role as a context (or typing environment) for type checking systems. Here, it is a record of information for the qubit register and compilation directives.

## The `constructors` module

The `constructors` module holds a collection of convenience functions for expression type constructions and quantum operations (_e.g._ unitary and Hermitian operators, projectors) as well as trainable and non-trainable parameters as symbols.

## The `support` module

The `support` module defines a `Support` type to handle qubit support for single, multi and controlled quantum operations.
