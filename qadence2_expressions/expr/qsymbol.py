from __future__ import annotations

from typing import Any

from .expr import NonCommutative
from .qubit_support import Support


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
        is_hermitian: bool = True,
    ) -> None:
        self.name = name
        self.support = Support()
        self.is_hermitian = is_hermitian
        self.is_dagger = False

    def __call__(self, *targets: Any, **target_control: Any) -> QSymbol:
        new_qsymbol = QSymbol(
            self.name,
            is_hermitian=self.is_hermitian,
        )
        new_qsymbol.support = Support(*targets, **target_control)
        new_qsymbol.is_dagger = self.is_dagger
        return new_qsymbol

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.support})"

    def _repr_pretty_(self, p, _cycle) -> None:  # type: ignore
        """Provide a friendly representation when using IPython/Jupyter notebook."""
        p.text(str(self))

    def __str__(self) -> str:
        dagger = "'" if self.is_dagger else ""
        return f"{self.name}{dagger}{self.support}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QSymbol):
            return NotImplemented

        return (
            self.name == other.name
            and self.support == other.support
            and self.is_hermitian == other.is_hermitian
            and self.is_dagger == other.is_dagger
        )

    def __hash__(self) -> int:
        return hash((self.name, self.support))

    def is_dagger_of(self, other: QSymbol) -> bool:
        """Returns true if two QSymbols are the inverse of each other."""

        if not isinstance(other, QSymbol):
            return NotImplemented

        if self.is_hermitian and other.is_hermitian:
            return self.name == other.name

        if not (self.is_hermitian or other.is_hermitian):
            return self.name == other.name and self.is_dagger ^ other.is_dagger

        return False

    def __matmul__(self, other: QSymbol) -> list:
        """Multiplication of two QSymbols returns either a empty list if both elements
        cancel each other, or a list with the two original element such that, if the elements
        subspace overlaps, the order of element is preserved, otherwise they are ordered by
        indices.
        """

        if not isinstance(other, QSymbol):
            return NotImplemented

        if self.support == other.support and self.is_dagger_of(other):
            return []

        if self.support.overlap_with(other.support):
            return [self, other]

        return [other, self] if other.support < self.support else [self, other]

    def __rmatmul__(self, other: list[QSymbol]) -> list:
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

            if other[i].support.overlap_with(self.support):
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
            is_hermitian=self.is_hermitian,
        )
        new_qsymbol.support = self.support
        new_qsymbol.is_dagger = not (self.is_hermitian or self.is_dagger)
        return new_qsymbol
