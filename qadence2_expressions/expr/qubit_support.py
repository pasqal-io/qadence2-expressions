from __future__ import annotations


class Support:
    def __init__(
        self,
        *indices: int,
        target: tuple[int, ...] | None = None,
        control: tuple[int, ...] | None = None,
    ) -> None:
        if indices and (target or control):
            raise SyntaxError(
                "Please, provide either qubit indices or target-control tuples"
            )

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
        return self._subspace

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Support):
            return NotImplemented

        return self._ordered_subspace == other._ordered_subspace

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Support):
            return NotImplemented

        return self._ordered_subspace < other._ordered_subspace

    def overlap_with(self, other: Support) -> bool:
        # A support applied to all qubits overlaps with any support.
        if not (self.target and other.target):
            return True

        return bool(self._subspace & other._subspace)
    
    def join(self, other: Support) -> Support:
        # If one of the supports covers all the qubits so the join of both will
        # cover all qubits.
        if not (self.target and other.target):
            return Support()
        
        target = set(self.target) | set(other.target)
        control = set(self.control) | set(other.control)
        overlap = target & control

        if overlap:
            return Support(target=target | control)
        
        return Support(target=target, control=control)
