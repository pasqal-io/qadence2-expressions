from __future__ import annotations

from typing import Any, Protocol, get_args

SPACE_SEPARATOR = "\u00a0"


Numerical = int | float | complex


# TODO: please do type annotation for all the args


class Numeric(Protocol):
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
    @property
    def dag(self) -> Adjoint | Numerical:
        ...


class Operator:
    ADD = "+"
    TIMES = "*"
    NONCOMMUTE = "@"
    POWER = "^"
    CALL = "call"


class Expr:
    def __init__(self, head: str, *args: Any) -> None:
        self.head: str = head
        self.args = args

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.head, self.args}"

    def _repr_pretty_(self, p, _cycle) -> None:  # type: ignore
        # to avoid using `print` in IPython / Jupyter Notebook
        p.text(str(self))

    def __str__(self) -> str:
        if self.head == Operator.ADD:
            return f" {self.head} ".join(map(str, self.args))

        if self.head == Operator.NONCOMMUTE:
            return SPACE_SEPARATOR.join(map(str, self.args))

        if self.head == Operator.TIMES:
            if isinstance(self.args[0], int | float) and abs(self.args[0]) == 1:
                sign = "-" if self.args[0] == -1 else ""
                return sign + SPACE_SEPARATOR.join(
                    map(
                        lambda x: (
                            f"({x})"
                            if isinstance(x, Expr) and x.head == Operator.ADD
                            else str(x)
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

        raise NotImplementedError(
            f"Visualization with operator {self.head} not implemented"
        )

    # TODO: please do type annotation for all the args
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expr):
            return NotImplemented
        if self.head != other.head:
            return False

        if self.head == Operator.ADD or self.head == Operator.TIMES:
            return set(self.args) == set(other.args)

        return self.args == other.args

    def __hash__(self) -> int:
        # commutative operations
        if self.head == Operator.ADD or self.head == Operator.TIMES:
            return hash((self.head, frozenset(self.args)))

        # non-commutative operations
        return hash((self.head, self.args))

    def __matmul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
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

    def __mul__(  # pylint: disable=too-many-return-statements
        self, other: Numeric | Numerical
    ) -> Numeric | Numerical:
        # CASES:

        #   1. Multiply by zero: e * 0 = 0
        #   2. Multiply by one: e * 1 = e

        #   3. Power:
        #       - e^m * e^n = e^(m+n)
        #       - e^m * e   = e^(m+1)
        #       - e   * e^m = e^(m+1)

        #   4. Noncommutative multiplication:
        #       E(@, [a,…]) * E(@, [b,…]) = E(@, [a,…]) @ E(@, [b,…])

        #   5. Distributive:
        #       - (a + b) * ? = (a*? + b*?)
        #       - ? * (a + b) = (?*a + ?*b)

        #   6. Multiplication:
        #       - E(*, [a,…]) * E(*, [b,…]) = E(*, [a,b,…])
        #       - E(*, [a,…]) * ? = E(*, [a,?,…])
        #       - ? * E(*, [a,…]) = E(*, [?,a,…])

        #   7. General case: e1 * e2 = E(*, [e1,e2,…])

        # <<< e * 0 = 0
        if isinstance(other, get_args(Numerical)) and other == 0:
            return 0

        # <<< e * 1 = e
        if isinstance(other, get_args(Numerical)) and other == 1:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
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
            if (
                isinstance(other, Expr)
                and other.head == Operator.POWER
                and self == other.args[0]
            ):
                power = other.args[1] + 1
                return 1 if not power else Expr(Operator.POWER, self, power)

            # <<< E(@, [a,…]) * E(@, [b,…]) = E(@, [a,…,b,…])
            if (
                self.head == Operator.NONCOMMUTE
                and isinstance(other, Expr)
                and other.head == Operator.NONCOMMUTE
            ):
                return self @ other

            # <<< E(+, [a,b,…]) * ? = E(+, [a*?,b*?,…])
            if self.head == Operator.ADD:
                return sum(el * other for el in self.args)  # type: ignore

            # <<< ? * E(+, [a,b,…]) = E(+, [?*a,?*a,…])
            if isinstance(other, Expr) and other.head == Operator.ADD:
                return sum(self * el for el in other.args)  # type: ignore

            # <<< E(*, [a,…]) * E(*, [b,…]) = E(*, [a,b,…])
            if (
                self.head == Operator.TIMES
                and isinstance(other, Expr)
                and other.head == Operator.TIMES
            ):
                args = args_reduce_mul(*self.args, *other.args)
                return args[0] if len(args) == 1 else Expr(Operator.TIMES, *args)

            # <<< E(*, [a,…]) * ? = E(*, [a,?,…])
            if self.head == Operator.TIMES:
                args = args_reduce_mul(*self.args, other)
                return args[0] if len(args) == 1 else Expr(Operator.TIMES, *args)

            # <<< ? * E(*, [a,…]) = E(*, [?,a,…])
            if isinstance(other, Expr) and other.head == Operator.TIMES:
                args = args_reduce_mul(self, *other.args)
                return args[0] if len(args) == 1 else Expr(Operator.TIMES, *args)

            # <<< e1 * e2 = E(*, [e1,e2,…])
            args = args_reduce_mul(self, other)
            return args[0] if len(args) == 1 else Expr(Operator.TIMES, *args)

        return NotImplemented

    def __rmul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        if isinstance(other, (*get_args(Numerical), Symbol)):
            return self * other

        return NotImplemented

    def __pow__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        # CASES:

        #   - e^0 = 1
        #   - e^1 = e

        #   - E(^, [a,b]) ^ ? = E(^, [a,b*?])
        #   - E(*, [a,b,…]) ^ ? = E(*, [a^?,b^?,…])

        #   <<<
        #    This option was left out to prioritise division simplitication.
        #       - n:Nat, n>1 -> E(+, [a,b,…]) ^ n = E(+, [a,b,…]) * E(+, [a,b,…]) * … ; n times
        #       - n:Nat, n>1 -> E(+, [a,b,…]) ^ -n = E(^, [E(+, [a,b,…]) ^ n, -1])
        #   >>>

        #   - e ^ ? = E(^, [e, ?])

        if isinstance(other, get_args(Numerical)) and other == 0:
            return 1

        if isinstance(other, get_args(Numerical)) and other == 1:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            # <<< E(^, [a,b]) ^ ? = E(^, [a,b*?])
            if self.head == Operator.POWER:
                power = self.args[1] * other
                return (
                    self.args[0]
                    if power == 1
                    else Expr(Operator.POWER, self.args[0], power)
                )

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
        # CASES:

        #   - e + 0 = e

        #   - E(+, [a,…]) + E(+, [b,…]) = E(+, [a,b,…])
        #   - E(+, [a,…]) + b = E(+, [a,b,…])
        #   - a + E(+, [b,…]) = E(+, [a,b,…])

        #   - e + ? = E(+, r[e,?])

        if isinstance(other, get_args(Numerical)) and other == 0:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            if (
                self.head == Operator.ADD
                and isinstance(other, Expr)
                and other.head == Operator.ADD
            ):
                args = args_reduce_sum(*self.args, *other.args)
                return Expr(Operator.ADD, *args)

            if self.head == Operator.ADD:
                args = args_reduce_sum(*self.args, other)
                return Expr(Operator.ADD, *args)

            if isinstance(other, Expr) and other.head == Operator.ADD:
                args = args_reduce_sum(self, *other.args)
                return Expr(Operator.ADD, *args)

            args = args_reduce_sum(self, other)
            return Expr(Operator.ADD, *args)

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
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def _repr_pretty_(self, p, _cycle):  # type: ignore
        # to avoid using `print` in IPython / Jupyter Notebook
        p.text(str(self))

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other: Numeric | Numerical) -> bool:
        if isinstance(other, Symbol):
            return self.name < other.name
        return NotImplemented

    def __gt__(self, other: Numeric | Numerical) -> bool:
        if isinstance(other, Symbol):
            return self.name > other.name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    def __mul__(self, other: Numeric | Numerical) -> Numeric | Numerical:
        # cases:

        #   - s * 0 = 0
        #   - s * 1 = s
        #   - s * ? = E(*, [1,s]) * ?  ; type casting: Symbol -> Expr

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
        # cases:
        #   - s ^ 0 = 1
        #   - s ^ 1 = s
        #   - s ^ ? = E(^, [s, ?])

        if isinstance(other, get_args(Numerical)) and other == 0:
            return 1

        if isinstance(other, get_args(Numerical)) and other == 1:
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
        # CASES:

        #   - s + 0 = s
        #   - s + ? = E(+, [s]) + ?  ; type casting Symbol -> Expr

        if isinstance(other, get_args(Numerical)) and other == 0:
            return self

        if isinstance(other, (*get_args(Numerical), Symbol, Expr)):
            return Expr(Operator.ADD, self) + other

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
    acc = list(lhs)
    for term in rhs:
        acc = acc @ term
    return tuple(acc)


def conjugate(value: Numerical | Numeric | Adjoint) -> Numerical | Numeric | Adjoint:
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
