from __future__ import annotations

from qadence2_expressions import (
    add_grid_options,
    add_qpu_directives,
    add_settings,
    get_grid_options,
    get_grid_scale,
    get_grid_type,
    get_number_qubits,
    get_qpu_directives,
    get_qubits_positions,
    get_settings,
    set_grid_scale,
    set_grid_type,
    set_number_qubits,
    set_qubits_positions,
)


def test_set_and_get_number_qubits() -> None:
    set_number_qubits(3)
    assert get_number_qubits() == 3


def test_set_and_get_qubit_positions() -> None:
    set_qubits_positions([(0, 0), (0, 1), (1, 0), (1, 1)])
    assert get_qubits_positions() == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_set_and_get_grid_scale() -> None:
    set_grid_scale(1.5)
    assert get_grid_scale() == 1.5


def test_set_and_get_grid_type() -> None:
    set_grid_type("square")
    assert get_grid_type() == "square"


def test_add_and_get_grid_options() -> None:
    add_grid_options({"Some": "Options"})
    assert get_grid_options() == {"Some": "Options"}


def test_add_and_get_qpu_directives() -> None:
    add_qpu_directives({"Some": "Directives"})
    assert get_qpu_directives() == {"Some": "Directives"}


def test_add_and_get_settings() -> None:
    add_settings({"Some": "Settings"})
    assert get_settings() == {"Some": "Settings"}
