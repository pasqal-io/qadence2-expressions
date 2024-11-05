from __future__ import annotations

from typing import Any

import pytest
import numpy as np
import torch

from qadence2_expressions.core.utils import Numeric
from qadence2_expressions import X, Y, RX, parameter


@pytest.mark.parametrize(
    "value",
    [
        2,
        3.0,
        5.0j,
        np.pi,
        np.array([1]),
        np.array([0.0, 1.0]),
        np.cos(2 / 3 * np.pi),
        torch.pi,
        torch.tensor([1, 2, 3]),
        torch.cos(torch.tensor(5 * torch.pi)),
    ],
)
def test_numeric(value: Any) -> None:
    assert isinstance(value, Numeric)


@pytest.mark.parametrize(
    "value", ["i", X(0), X(0) * Y(1), parameter("a") + parameter("b"), RX(parameter("x"))(2)]
)
def test_not_numeric(value: Any) -> None:
    assert not isinstance(value, Numeric)
