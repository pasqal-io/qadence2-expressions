from __future__ import annotations

from functools import cached_property


class Support:
    """A class to handle the qubit support providing easy initialization for single, multi, and
    controlled qubit operations.

    The class can be initialized in three ways:

    1. `Support(i)` for single qubit support.
    2. `Support(i₀,...,iₙ)` for supports covering indices `{i₀,...,iₙ}` use either by multi-indices
        operation or to span single indices operations over multiple indices.
    3. `Support(target=(i₀,...), control=(j₀,...))` for controled operations where `target` and
        `control` are disjoint sets.

    Args:
        indices: Qubit indices where an operation is applied; all listed qubits are the target
            qubits.
        target: Tuple of qubit indices where a given operation is applied; not valid if `indices`
            is defined.
        control: Tuple of qubit indices used to control an operation; not valid without `target`.

    Methods:
        `subspace`: returns the set of indices covered by the support.
        `overlap_with`: returns true if a support overlaps with another (not
            distinguishing between target and controls).
        `join`: merge two supports.
    """

    def __init__(
        self,
        *indices: int,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> None:
        if indices and (target or control):
            raise SyntaxError("Please, provide either qubit indices or target-control tuples")

        if control and not target:
            raise SyntaxError("A controlled operation needs both, control and target.")

        if indices:
            target = tuple(sorted(indices))
            control = ()
        else:
            if target and control and set(target) & set(control):
                raise SyntaxError("Target and control indices cannot overlap.")

            target = tuple(sorted(target)) if target else ()
            control = tuple(sorted(control)) if control else ()

        self._subspace: tuple[int, ...] = (*target, *control)
        self._control_start = len(target)

    @classmethod
    def target_all(cls) -> Support:
        """Return a support that covers all qubits, regardless of range or total number of
        qubits.
        """
        return cls()

    @cached_property
    def subspace(self) -> set[int]:
        """Returns a set containing all the indices covered by the support."""
        return set(self._subspace)

    @property
    def target(self) -> tuple[int, ...]:
        """Returns the indices to which a given operation is applied."""
        return self._subspace[: self._control_start]

    @property
    def control(self) -> tuple[int, ...]:
        """Returns the indices used to control a given operation."""
        return self._subspace[self._control_start :]

    @cached_property
    def max_index(self) -> int:
        """Returns the largest index within the specified subspace, whether it is a target or
        control. If the support is applied to all qubits, it returns `-1`.
        """
        return max(self._subspace) if self._subspace else -1

    def overlap_with(self, other: Support) -> bool:
        """Returns true if both supports cover common indices."""

        # A support applied to all indices overlaps with any support.
        if not (self.target and other.target):
            return True

        # Check the overlap bewtween the subspace and convert non-empty result to `True`, or `False`
        # otherwise.
        return bool(self.subspace & other.subspace)

    def join(self, other: Support) -> Support:
        """Merge two support's indices according the following rules.

        1. If one of the supports cover all the indices, the result also covers
           all the indices.

        2. If the target of one support overlaps with the control of the other
           support, the resul is a support which the target covers all the
           indices without target.

        3. Otherwise, the targets and the controls are merged.
        """

        # If one of the supports covers all the indices, the join will also do.
        if not (self.target and other.target):
            return Support()

        target = set(self.target) | set(other.target)
        control = set(self.control) | set(other.control)
        overlap = target & control

        if overlap:
            return Support(target=tuple(target | control))

        return Support(target=tuple(target), control=tuple(control))

    def __repr__(self) -> str:
        separator = ","
        targets = "*" if not self.target else separator.join(map(str, self.target))
        controls = separator.join(map(str, self.control))
        return f"[{targets}]" if not controls else f"[{targets}|{controls}]"

    def __hash__(self) -> int:
        return hash(self._subspace)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Support):
            return NotImplemented

        return self._subspace == other._subspace

    def __lt__(self, other: object) -> bool:
        """Implement partial order to qubit supports."""

        if not isinstance(other, Support):
            return NotImplemented

        return self._subspace < other._subspace
