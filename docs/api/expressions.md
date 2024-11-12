# The `expression` module

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


::: qadence2_expressions.core.expression
