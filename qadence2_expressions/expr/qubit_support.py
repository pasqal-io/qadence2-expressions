from __future__ import annotations


class Support:
    """A class to handle the qubit support providing easy initialization for
    single, multi, and controlled qubit operations.

    The class can be initializes in three ways:

    - `Support(i)` for single qubit support.
    - `Support(i₀,...,iₙ)` for supports covering indices `{i₀,...,iₙ}` use either by
      multi-indices operation or to span single indices operations over multiple
      indices.
    - `Support(target=(i₀,...), control=(j₀,...))` for controled operations where
      `target` and `control` are disjoint sets.

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
            self.target: tuple[int, ...] = tuple(sorted(indices))
            self.control: tuple[int, ...] = ()
        else:
            if target and control and set(target) & set(control):
                raise SyntaxError("Target and control indices cannot overlap.")

            self.target = tuple(sorted(target)) if target else ()
            self.control = tuple(sorted(control)) if control else ()

        self._subspace: set[int] = set(self.target) | set(self.control)
        self._ordered_subspace: tuple[int, ...] = (*self.target, *self.control)

    def __repr__(self) -> str:
        targets = "*" if not self.target else " ".join(map(str, self.target))
        controls = " ".join(map(str, self.control))
        return f"[{targets}]" if not controls else f"[{targets} ; {controls}]"

    def __hash__(self) -> int:
        return hash(self._ordered_subspace)

    @classmethod
    def target_all(cls) -> Support:
        return cls()

    @property
    def subspace(self) -> set[int]:
        """Return a set containing all the indices covered by the support."""

        return self._subspace

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Support):
            return NotImplemented

        return self._ordered_subspace == other._ordered_subspace

    def __lt__(self, other: object) -> bool:
        """Implement partial order to qubit supports."""

        if not isinstance(other, Support):
            return NotImplemented

        return self._ordered_subspace < other._ordered_subspace

    def overlap_with(self, other: Support) -> bool:
        """Returns true if both support cover common indices."""

        # A support applied to all indices overlaps with any support.
        if not (self.target and other.target):
            return True

        return bool(self._subspace & other._subspace)

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
