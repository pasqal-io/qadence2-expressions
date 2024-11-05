# Expression system

Qadence 2 Expression system is designed to create expressive, self-contained and abstract symbolic expressions to represent quantum programs in the digital-analog paradigm. These expressions can be transpiled later with concretized and specific data types, such as `numpy`, `pytorch` and `jax` for execution on targeted backends.

The Expression system defines syntactic rules to generate symbolic quantum expressions, that can contain parametric expressions for **parameters** (static, `FeatureParameter`) and **variables** (dynamic, `VariationalParameter`) to be used for training purposes. Expression composition can be seamlessly applied to quantum operators for digital, analog and digital-analog computations. It also supports arithmetic operations for both classical and quantum expressions as well as reduction, simplification and replacement methods.

## The `expression` module

The `expression` modules defines an `Expression` type as symbolic representation for mathematical expressions together with arithmetic rules. It is syntactically constructed using [S-Expressions](https://en.wikipedia.org/wiki/S-expression) in prefix notation where the ordered parameters are:

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
