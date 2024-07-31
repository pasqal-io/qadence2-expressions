from __future__ import annotations

from typing import Any, Literal


class Environment:
    protected: set[str] = {"E"}
    qubit_positions: list[tuple[int, int]] | list[int] | None = None
    grid_type: Literal["linear", "square", "triangular"] | None = None
    grid_scale: float = 1.0
    num_qubits: int = 0
    grid_options: dict[str, Any] | None = None
    directives: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None


def set_number_qubits(n: int) -> None:
    if Environment.qubit_positions and n != len(Environment.qubit_positions):
        raise ValueError("Number of qubits already defined by the register.")
    Environment.num_qubits = n


def get_number_qubits() -> int:
    return Environment.num_qubits


def set_qubits_positions(pos: list[tuple[int, int]] | list[int]) -> None:
    Environment.qubit_positions = pos
    set_number_qubits(len(pos))


def get_qubits_positions() -> list[tuple[int, int]] | list[int] | None:
    return Environment.qubit_positions


def set_grid_type(grid: Literal["linear", "square", "triangular"]) -> None:
    Environment.grid_type = grid


def get_grid_type() -> Literal["linear", "square", "triangular"] | None:
    return Environment.grid_type


def set_grid_scale(s: float) -> None:
    Environment.grid_scale = s


def get_grid_scale() -> float:
    return Environment.grid_scale


def add_grid_options(options: dict[str, Any]) -> None:
    current = Environment.grid_options or {}
    Environment.grid_options = {**current, **options}


def get_grid_options() -> dict[str, Any] | None:
    return Environment.grid_options


def add_qpu_directives(directives: dict[str, Any]) -> None:
    current = Environment.directives or {}
    Environment.directives = {**current, **directives}


def get_qpu_directives() -> dict[str, Any] | None:
    return Environment.directives


def add_settings(settings: dict[str, Any]) -> None:
    current = Environment.settings or {}
    Environment.settings = {**current, **settings}


def get_settings() -> dict[str, Any] | None:
    return Environment.settings


def reset_ir_options() -> None:
    Environment.qubit_positions = None
    Environment.grid_type = None
    Environment.grid_scale = 1.0
    Environment.num_qubits = 0
    Environment.grid_options = None
    Environment.directives = None
    Environment.settings = None
