from __future__ import annotations

from typing import Literal


class Environment:
    protected: set[str] = {"E"}
    qubit_positions: list[tuple[int, int]] | None = None
    grid_type: Literal["linear", "square", "triangular"] | None = None
    grid_scale: float = 1.0


def set_qubits_positions(pos: list[tuple[int, int]]) -> None:
    Environment.qubit_positions = pos


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
