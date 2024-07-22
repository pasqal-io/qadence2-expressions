from __future__ import annotations

from typing import Any, Protocol, get_args

SPACE_SEPARATOR = "\u00a0"


Numerical = int | float | complex


class Numeric(Protocol):
    """Covering objects with basic algebraic operations implements."""

    def __mul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __rmul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __pow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __rpow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __truediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __rtruediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __add__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __radd__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __neg__(self) -> Numeric | Numerical:
        ...

    def __sub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...

    def __rsub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        ...


class Adjoint(Protocol):
    """Apply to objects with Hermitian conjugate property. That covers complex numebers
    and quantum operators.
    """

    @property
    def dag(self) -> Adjoint | Numerical:
        ...


class Operator:
    """Qadence expressions can be: a sum, a multiplication or a power. Negative terms
    are store with a negative constant while division is represented with negative power.
    These datastructs choices were made to simplify some symbolic multiplications.

    By default, addition and multiplication are considered commutative. This behaviour can
    be changed wrapping the terms in a noncommutative expression in order to protect the
    elements order.

    Functions can be represented as expressions as well using the "call" operator. In that
    case, the first argument of the expression is a string naming a callable object, and
    the remaining elements are passed as its arguments.
    """

    PLUS = "+"
    TIMES = "*"
    NONCOMMUTE = "@"
    POWER = "^"
    CALL = "call"


class Expr:
    """Qadence expression system class holds mathematical and circuit expressions
    in a s-expression. The first element holds a `Operator` while the other are
    its arguments. For instance, the expression `2 * x + 3 * y + 8` is stored as
        Expr(+, Expr(*, 2, x), Expr(*, 3, y), 8)

    By default, qadence expression are expanded to keep the addition as the most
    external expression (root). So expression like `a * (b + c + 2)` will be expanded
    to `a*b + a*c + 2*a`. This behaviour, however, doesn't happen in case of power of
    a sum like `a * (b + c)^2`. This choice was made to help simplify power terms like
        (a + b) * (a + b) ^ 0.5 / (a + b)^2 == (a + b) ^ -0.5
    """

    def __init__(self, head: str, *args: Any) -> None:
        self.head: str = head
        self.args = args

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.head, self.args}"

    def _repr_pretty_(self, p, _cycle) -> None:  # type: ignore
        """Provide a friendly representation when using IPython/Jupyter notebook."""
        p.text(str(self))

    def __str__(self) -> str:
        if self.head == Operator.PLUS:
            return f" {self.head} ".join(map(str, self.args))

        if self.head == Operator.NONCOMMUTE:
            return SPACE_SEPARATOR.join(map(str, self.args))

        if self.head == Operator.TIMES:
            if isinstance(self.args[0], int | float) and abs(self.args[0]) == 1:
                sign = "-" if self.args[0] == -1 else ""
                return sign + SPACE_SEPARATOR.join(
                    map(
                        lambda x: (
                            f"({x})" if isinstance(x, Expr) and x.head == Operator.PLUS else str(x)
                        ),
                        self.args[1:],
                    )
                )
            return SPACE_SEPARATOR.join(map(str, self.args))

        if self.head == Operator.POWER:
            factor, power = list(map(str, self.args))
            if isinstance(self.args[0], Expr) and self.args[0].head not in (
                Operator.CALL,
                Operator.NONCOMMUTE,
            ):
                factor = f"({factor})"
            if isinstance(self.args[1], Expr):
                power = f"({power})"
            return f"{factor}^{power}"

        if self.head == Operator.CALL:
            args = ", ".join(map(str, self.args[1:]))
            return f"{self.args[0]}({args})"

        raise NotImplementedError(f"Visualization with operator {self.head} not implemented")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expr):
            # It use the standard Python implementation returning a `NotImplemented`
            # as a way to delgate the interpreter the task to handle incompatible
            # types.
            return NotImplemented

        if self.head != other.head:
            return False

        if self.head == Operator.PLUS or self.head == Operator.TIMES:
            return set(self.args) == set(other.args)

        return self.args == other.args

    def __hash__(self) -> int:
        # For commutative operations, the arguments are hashed using `frozenset`
        # to discard their order.
        if self.head == Operator.PLUS or self.head == Operator.TIMES:
            return hash((self.head, frozenset(self.args)))

        # With noncommutative operations, the order of the argument are relevant
        # for the hashing.
        return hash((self.head, self.args))

    def __matmul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        """Uses the matmul operator to concatenate noncommutative expressions."""

        # Only two noncommutative expressions can be concatenated
        if (
            self.head == Operator.NONCOMMUTE
            and isinstance(other, Expr)
            and other.head == Operator.NONCOMMUTE
        ):
            args = args_reduce_noncomm(self.args, other.args)
            return 1 if not args else Expr(Operator.NONCOMMUTE, *args)

        return NotImplemented

    def __rmamtmul__(self, _other: Numeric | Numerical) -> Numeric | Numerical:
        return NotImplemented

    def __mul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        """ "Multiplication involving expressions are made acording to the following
        rules in the order as described.

          1. Multiply by zero: e * 0 = 0   (shortcut case)
          2. Multiply by one: e * 1 = e    (shortcut case)

          3. Power:
              - e^m * e^n = e^(m+n)
              - e^m * e   = e^(m+1)
              - e   * e^m = e^(m+1)

          4. Noncommutative multiplication:
              E(@, [a,…]) * E(@, [b,…]) = E(@, [a,…]) @ E(@, [b,…])

          5. Distributive:
              - (a + b) * ? = (a*? + b*?)
              - ? * (a + b) = (?*a + ?*b)

          6. Multiplication:
              - E(*, [a,…]) * E(*, [b,…]) = E(*, [a,b,…])
              - E(*, [a,…]) * ? = E(*, [a,?,…])
              - ? * E(*, [a,…]) = E(*, [?,a,…])

          7. General case: e1 * e2 = E(*, [e1,e2,…])
        """

        # WARNING: The conditions below can be regrouped in different ways. Depending
        # on how the code is rearranged, the multiplication rules may be be clear.
        # Please, keep that in mind when refactor the code.

        # shortcuts
        if other == 0:
            return 0

        if other == 1:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            # Multiplication of power.
            # <<< E(^, [a,m]) * E(^, [a,n]) = a ^ (m+n)
            if (
                self.head == Operator.POWER
                and isinstance(other, Expr)
                and other.head == Operator.POWER
                and self.args[0] == other.args[0]
            ):
                return self.args[0] ** (self.args[1] + other.args[1])  # type: ignore

            # <<< E(^, [a,m]) * a = E(^, [a,m+1])
            if self.head == Operator.POWER and other == self.args[0]:
                return self.args[0] ** (self.args[1] + 1)  # type: ignore

            # <<< a * E(^, [a,m]) = E(^, [a,m+1])
            if isinstance(other, Expr) and other.head == Operator.POWER and self == other.args[0]:
                power = other.args[1] + 1
                return 1 if not power else Expr(Operator.POWER, self, power)

            # Multiplication of noncommutative elements.
            if (
                self.head == Operator.NONCOMMUTE
                and isinstance(other, Expr)
                and other.head == Operator.NONCOMMUTE
            ):
                return self @ other

            # Left distributive, (a + b) * c = a*c + b*c.
            if self.head == Operator.PLUS:
                return sum(el * other for el in self.args)  # type: ignore

            # <<< Right distributive, a * (b + c) = a*b + a*c.
            if isinstance(other, Expr) and other.head == Operator.PLUS:
                return sum(self * el for el in other.args)  # type: ignore

            # <<< E(*, [a,…]) * E(*, [b,…]) = E(*, [a,b,…])
            if (
                self.head == Operator.TIMES
                and isinstance(other, Expr)
                and other.head == Operator.TIMES
            ):
                args = args_reduce_mul(*self.args, *other.args)
                if len(args) == 1:
                    return args[0]  # type: ignore
                if len(args) == 2 and args[0] == 1:
                    return args[1]  # type: ignore
                return Expr(Operator.TIMES, *args)

            # <<< E(*, [a,…]) * ? = E(*, [a,?,…])
            if self.head == Operator.TIMES:
                args = args_reduce_mul(*self.args, other)
                if len(args) == 1:
                    return args[0]  # type: ignore
                if len(args) == 2 and args[0] == 1:
                    return args[1]  # type: ignore
                return Expr(Operator.TIMES, *args)

            # <<< ? * E(*, [a,…]) = E(*, [?,a,…])
            if isinstance(other, Expr) and other.head == Operator.TIMES:
                args = args_reduce_mul(self, *other.args)
                if len(args) == 1:
                    return args[0]  # type: ignore
                if len(args) == 2 and args[0] == 1:
                    return args[1]  # type: ignore
                return Expr(Operator.TIMES, *args)

            # General case.
            args = args_reduce_mul(self, other)
            if len(args) == 1:
                return args[0]  # type: ignore
            if len(args) == 2 and args[0] == 1:
                return args[1]  # type: ignore
            return Expr(Operator.TIMES, *args)

        return NotImplemented

    def __rmul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        if isinstance(other, (*get_args(Numerical), Symbol)):
            return self * other

        return NotImplemented

    def __pow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        """Power involving expressions are made acording to the following rules in
        the order as described.

          1. e^0 = 1  (shortcut case)
          2. e^1 = e  (shortcut case)

          3. Poewr of power: E(^, [a,b]) ^ ? = E(^, [a,b*?])
          4. Power of multiplication: E(*, [a,b,…]) ^ ? = E(*, [a^?,b^?,…])

          5. General case: e ^ ? = E(^, [e, ?])
        """

        # shortcuts
        if other == 0:
            return 1

        if other == 1:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            # <<< E(^, [a,b]) ^ ? = E(^, [a,b*?])
            if self.head == Operator.POWER:
                power = self.args[1] * other
                return self.args[0] if power == 1 else Expr(Operator.POWER, self.args[0], power)

            # <<< E(*, [a,b,…]) ^ ? = E(*, [a^?,b^?,…])
            if self.head == Operator.TIMES:
                args = tuple(elem**other for elem in self.args)
                return Expr(self.head, *args)

            # <<< e ^ ? = E(^, [e, ?])
            return Expr(Operator.POWER, self, other)

        return NotImplemented

    def __rpow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        if isinstance(other, get_args(Numerical)):
            return Expr(Operator.POWER, other, self)

        return NotImplemented

    def __truediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return self * other**-1

    def __rtruediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return other * self**-1

    def __add__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        """Addition involving expressions are made acording to the following rules
        in the order as described.

          1. Neutral element: e + 0 = e  (shortcut case)

          2. Sum with addition expression:
              - E(+, [a,…]) + E(+, [b,…]) = E(+, [a,b,…])
              - E(+, [a,…]) + b = E(+, [a,b,…])
              - a + E(+, [b,…]) = E(+, [a,b,…])

          3. General case: e + ? = E(+, r[e,?])
        """

        if other == 0:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            if (
                self.head == Operator.PLUS
                and isinstance(other, Expr)
                and other.head == Operator.PLUS
            ):
                args = args_reduce_sum(*self.args, *other.args)
                return Expr(Operator.PLUS, *args) if len(args) > 1 else args[0]

            if self.head == Operator.PLUS:
                args = args_reduce_sum(*self.args, other)
                return Expr(Operator.PLUS, *args) if len(args) > 1 else args[0]

            if isinstance(other, Expr) and other.head == Operator.PLUS:
                args = args_reduce_sum(self, *other.args)
                return Expr(Operator.PLUS, *args) if len(args) > 1 else args[0]

            args = args_reduce_sum(self, other)
            return Expr(Operator.PLUS, *args) if len(args) > 1 else args[0]

        return NotImplemented

    def __radd__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        # addition is commutative
        return self.__add__(other)

    def __neg__(self) -> Numeric | Numerical:
        return -1 * self

    def __sub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return self + (-other)

    def __rsub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return (-self) + other

    @property
    def dag(self) -> Numerical | Numeric | Adjoint:
        return conjugate(self)


class Symbol:
    """Creates symbolic variables with algebraic properties which concrete type and value are
    defined later by the backend.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def _repr_pretty_(self, p, _cycle):  # type: ignore
        """Provide a friendly representation when using IPython/Jupyter notebook."""
        p.text(str(self))

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.name == other.name

    # Symbols can be ordered by their names.
    def __lt__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name < other.name
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name > other.name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    def __mul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        """Multiplication involving symbols are made acording to the following
        rules in the order as described.

          1. Multipy be zero: s * 0 = 0  (shortcut case)
          2. Identity multiplication: s * 1 = s  (shortcut case)

          3. General case:
              s * ? = E(*, [1,s]) * ?  ; type casting: Symbol -> Expr
        """

        if isinstance(other, get_args(Numerical)) and other == 0:
            return 0

        if isinstance(other, get_args(Numerical)) and other == 1:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            return Expr(Operator.TIMES, 1, self) * other

        return NotImplemented

    def __rmul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        # assuming commutative multiplication
        return self.__mul__(other)

    def __pow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        """Power involving symbols are made acording to the following rules in the
        order as described.

          1. s ^ 0 = 1
          2. s ^ 1 = s
          3. s ^ ? = E(^, [s, ?])
        """

        if other == 0:
            return 1

        if other == 1:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            return Expr(Operator.POWER, self, other)

        return NotImplemented

    def __rpow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        if isinstance(other, get_args(Numerical)):
            return Expr(Operator.POWER, other, self)

        return NotImplemented

    def __truediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return self * other**-1

    def __rtruediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return other * self**-1

    def __add__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        """Addition involving symbols require two simple rules.

        1. s + 0 = s  (shorcut case)

        2. General case:
            s + ? = E(+, [s]) + ?  ; type casting Symbol -> Expr
        """

        if isinstance(other, get_args(Numerical)) and other == 0:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            return Expr(Operator.PLUS, self) + other

        return NotImplemented

    def __radd__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        # addition is commutative
        return self.__add__(other)

    def __neg__(self) -> Numeric | Numerical:
        return Expr(Operator.TIMES, -1, self)

    def __sub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        if isinstance(other, Symbol) and other == self:
            return 0
        return self + (-other)

    def __rsub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        if isinstance(other, Symbol) and other == self:
            return 0
        return (-self) + other


class NonCommutative:
    """This base class allows to create objects that are automatic promoted to noncommutative
    expression terms when used in symbolic expression. Example of such objects are quantum
    operators.
    """

    def __mul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return Expr(Operator.NONCOMMUTE, self) * other

    def __rmul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return other * Expr(Operator.NONCOMMUTE, self)

    def __pow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return Expr(Operator.NONCOMMUTE, self) ** other

    def __rpow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return other ** Expr(Operator.NONCOMMUTE, self)

    def __truediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return Expr(Operator.NONCOMMUTE, self) / other

    def __rtruediv__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return other / Expr(Operator.NONCOMMUTE, self)

    def __add__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return Expr(Operator.NONCOMMUTE, self) + other

    def __radd__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return other + Expr(Operator.NONCOMMUTE, self)

    def __neg__(self) -> Numeric | Numerical:
        return -1 * Expr(Operator.NONCOMMUTE, self)

    def __sub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return Expr(Operator.NONCOMMUTE, self) - other

    def __rsub__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        return other - Expr(Operator.NONCOMMUTE, self)


def args_reduce_mul(*args: Any) -> tuple:
    """Auxiliar function to simplify arguments in multiplicative expression by combining expoents
    like in `a*b*a == a^2 * b` and removing elements with null expoent from the arguments list.
    """

    factors: dict[Expr, Numerical] = {}
    noncommuters: tuple[Any, ...] = ()

    acc = 1
    for arg in args:
        if isinstance(arg, get_args(Numerical)):
            acc *= arg

        elif isinstance(arg, Expr) and arg.head == Operator.NONCOMMUTE:
            noncommuters = (*noncommuters, *arg.args)

        elif isinstance(arg, Expr) and arg.head == Operator.POWER:
            factor, power = arg.args
            factors[factor] = factors.get(factor, 0) + power

        else:
            factors[arg] = factors.get(arg, 0) + 1

    new_factors = []
    for factor, power in factors.items():
        if power != 0:
            new_factors.append(factor**power)

    if noncommuters:
        nc_args = args_reduce_noncomm([], noncommuters)
        if nc_args:
            return (acc, *new_factors, Expr(Operator.NONCOMMUTE, *nc_args))

    return (acc, *new_factors)


def args_reduce_sum(*args: Any) -> tuple:
    """Auxiliar function to simplify arguments in addition expression by combining elements like in
    `a + b + a == 2*a + b` and removing elements with null coefficient from the arguments list.
    """

    terms: dict = {}

    acc = 0
    for arg in args:
        if isinstance(arg, get_args(Numerical)):
            acc += arg

        elif isinstance(arg, Expr) and arg.head == Operator.TIMES:
            key = frozenset(arg.args[1:]) if len(arg.args) > 2 else arg.args[1]
            terms[key] = terms.get(key, 0) + arg.args[0]

        else:
            terms[arg] = terms.get(arg, 0) + 1

    new_terms = []
    for term, coef in terms.items():
        if coef != 0:
            if isinstance(term, frozenset):
                # reordering the factos
                args = args_reduce_mul(coef, *term)
                new_terms.append(Expr(Operator.TIMES, *args))
            else:
                new_terms.append(coef * term)

    if not (acc or new_terms):
        return (0,)

    return (acc, *new_terms) if acc else (*new_terms,)


def args_reduce_noncomm(lhs: list | tuple, rhs: list | tuple) -> tuple:
    """Auxiliar function to possible reduce arguments on noncommutaive expression
    in case does elements have cancelation properties (implemented by the derivate class).
    """

    acc = list(lhs)
    for term in rhs:
        acc = acc @ term
    return tuple(acc)


def conjugate(value: Numerical | Numeric | Adjoint) -> Numerical | Numeric | Adjoint:
    """Apply the conjugate operation recursively in expressions.

    For noncommutative expression the arguments are reversed to match the algebraic
    properperties of quantum operators.
    """

    if isinstance(value, Expr) and value.head == Operator.NONCOMMUTE:
        args = [conjugate(el) for el in value.args[::-1]]
        return Expr(value.head, *args)

    if isinstance(value, Expr):
        args = [conjugate(el) for el in value.args]
        return Expr(value.head, *args)

    if hasattr(value, "conjugate"):
        return value.conjugate()

    if hasattr(value, "dag"):
        return value.dag

    return value
