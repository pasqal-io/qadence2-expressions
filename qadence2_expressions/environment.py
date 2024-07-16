from __future__ import annotations

from typing import Literal


class Environment:
    protected: set[str] = {"E"}
    qubit_positions: list[tuple[int, int]] | None = None
    grid_type: Literal["linear", "square", "triangular"] | None = None
    grid_scale: float = 1.0
    num_qubits: int = 0


def set_number_qubits(n: int) -> None:
    if Environment.qubit_positions and n != len(Environment.qubit_positions):
        raise ValueError("Number of qubits already defined by the register.")
    Environment.num_qubits = n


def get_number_qubits() -> int:
    return Environment.num_qubits


def set_qubits_positions(pos: list[tuple[int, int]]) -> None:
    Environment.qubit_positions = pos
    set_number_qubits(len(pos))


def get_qubits_positions() -> list[tuple[int, int]] | None:
    return Environment.qubit_positions


def set_grid_type(grid: Literal["linear", "square", "triangular"]) -> None:
    Environment.grid_type = grid


def get_grid_type() -> Literal["linear", "square", "triangular"] | None:
    return Environment.grid_type


def set_grid_scale(s: float) -> None:
    Environment.grid_scale = s


def get_grid_scale() -> float:
    return Environment.grid_scale
