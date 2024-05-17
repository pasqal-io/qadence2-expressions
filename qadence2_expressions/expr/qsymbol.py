from __future__ import annotations

from typing import Any

from .expr import NonCommutative


class QSymbol(NonCommutative):
    """QSymbol class define quantum operators and quantum gates.

    QSymbols are part of U and SU groups, meaning A^dag == A^-1, and they can be
    parametrised with acceptable parameters being numbers, symbols, and expresions.

    An instance of a QSymbol is a callable object which the arguments list is the indices of
    subspace the symbol acts on. If no index is provided, the QSymbol is assumed to act on all
    subspaces.
    """

    def __init__(
        self,
        name: str,
        *params: Any,
        ordered_support: bool = False,
        is_hermitian: bool = True,
    ) -> None:
        self.name = name
        self.support: tuple[int, ...] = tuple()
        self.has_ordered_support = ordered_support
        self.is_hermitian = is_hermitian
        self.is_dagger = False
        self.params = params

    def __call__(self, *support: Any) -> QSymbol:
        new_qsymbol = QSymbol(
            self.name,
            *self.params,
            ordered_support=self.has_ordered_support,
            is_hermitian=self.is_hermitian,
        )
        new_qsymbol.support = support
        new_qsymbol.is_dagger = self.is_dagger
        return new_qsymbol

    def __repr__(self) -> str:
        ordered = ", Ord" if self.has_ordered_support else ", NoOrd"
        support = f"{ordered}{self.support}" if self.support else ""
        return f"{self.__class__.__name__}({self.name}{support})"

    def _repr_pretty_(self, p, _cycle) -> None:  # type: ignore
        """Provide a friendly representation when using IPython/Jupyter notebook."""
        p.text(str(self))

    def __str__(self) -> str:
        dagger = "'" if self.is_dagger else ""
        support = "*" if not self.support else ",".join(map(str, self.support))
        params = "" if not self.params else "(" + ",".join(map(str, self.params)) + ")"
        return f"{self.name}{dagger}{params}[{support}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QSymbol):
            return NotImplemented

        return (
            self.name == other.name
            and self.has_ordered_support == other.has_ordered_support
            and self.support == other.support
            and self.is_hermitian == other.is_hermitian
            and self.is_dagger == other.is_dagger
            and self.params == other.params
        )

    def __hash__(self) -> int:
        return hash((self.name, self.support))

    def same_subspace(self, other: QSymbol) -> bool:
        """Return true is two QSymbols act over the same Hilbert space."""

        if not isinstance(other, QSymbol):
            return NotImplemented

        if self.has_ordered_support and other.has_ordered_support:
            return self.support == other.support

        if not (self.has_ordered_support or other.has_ordered_support):
            return set(self.support) == set(other.support)

        return False

    def collide_with(self, other: QSymbol) -> bool:
        """Return true if two QSymbols have overlap indices, e.g. `X_ij` and `Y_jk` collide since
        both act on subspace `j`.
        """

        if not isinstance(other, QSymbol):
            return NotImplemented

        return bool(set(self.support) & set(other.support)) or not (
            self.support and other.support
        )

    def is_dagger_of(self, other: QSymbol) -> bool:
        """Returns true if two QSymbols are the inverse of each other."""

        if not isinstance(other, QSymbol):
            return NotImplemented

        if self.is_hermitian and other.is_hermitian:
            return self.name == other.name and self.same_subspace(other)

        if not (self.is_hermitian or other.is_hermitian):
            return (
                self.name == other.name
                and self.same_subspace(other)
                and self.is_dagger ^ other.is_dagger
            )

        return False

    def __matmul__(self, other: QSymbol) -> list:
        """Multiplication of two QSymbols returns either a empty list if both elements
        cancel each other, or a list with the two original element such that, if the elements
        subspace overlaps, the order of element is preserved, otherwise they are ordered by
        indices.
        """

        if not isinstance(other, QSymbol):
            return NotImplemented

        if self.is_dagger_of(other):
            return []

        if self.name == other.name and self.same_subspace(other):
            sign1 = 1 - 2 * self.is_dagger
            sign2 = 1 - 2 * other.is_dagger
            params = [
                sign1 * p1 + sign2 * p2 for p1, p2 in zip(self.params, other.params)
            ]
            return [
                QSymbol(
                    self.name,
                    *params,
                    ordered_support=self.has_ordered_support,
                    is_hermitian=self.is_hermitian,
                )
            ]

        if self.same_subspace(other) or self.collide_with(other):
            return [self, other]

        return [other, self] if other.support < self.support else [self, other]

    def __rmatmul__(self, other: list) -> list:
        """Handles the cancelation properties for multiplication of noncommutative
        expression when a QSymbol is used in a expression.
        """

        if not isinstance(other, list):
            return NotImplemented

        if not other:
            return [self]

        # Uses a insertion sort-like to arrange the list of QSymbols accordingly to the
        # multiplication property.
        acc = []
        for i in range(len(other) - 1, -1, -1):
            ii = i + 1

            if other[i].collide_with(self):
                acc = [*other[:i], *(other[i] @ self), *other[ii:]]
                break

            if self.support > other[i].support:
                acc = [*other[:ii], self, *other[ii:]]
                break

            if i == 0:
                acc = [self, *other]

        return acc

    @property
    def dag(self) -> QSymbol:
        new_qsymbol = QSymbol(
            self.name,
            *self.params,
            ordered_support=self.has_ordered_support,
            is_hermitian=self.is_hermitian,
        )
        new_qsymbol.support = self.support
        new_qsymbol.is_dagger = not (self.is_hermitian or self.is_dagger)
        return new_qsymbol
