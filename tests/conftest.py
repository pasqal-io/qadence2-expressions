from __future__ import annotations

from typing import List, Callable
import pytest

from qadence2_expressions import (
    CZ,
    H,
    NOT,
    SWAP,
    X,
    Y,
    Z,
)


@pytest.fixture
def unitary_hermitian_operators() -> List[Callable]:
    return [CZ, H, X, Y, Z, NOT, SWAP]
