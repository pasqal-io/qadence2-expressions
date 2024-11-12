from __future__ import annotations

from importlib import import_module

from .collect import collect_operators
from .core import *
from .functions import (
    cos,
    exp,
    log,
    sin,
    sqrt,
)
from .ircompiler import compile_to_model
from .operators import (
    CZ,
    H,
    NOT,
    RX,
    RY,
    RZ,
    SWAP,
    Z0,
    Z1,
    FreeEvolution,
    NativeDrive,
    X,
    Xm,
    Xp,
    Y,
    Z,
)
from .replace import prod, replace

__all__ = [
    "cos",
    "collect_operators",
    "compile_to_model",
    "CZ",
    "exp",
    "FreeEvolution",
    "H",
    "log",
    "NativeDrive",
    "NOT",
    "prod",
    "replace",
    "RX",
    "RY",
    "RZ",
    "SWAP",
    "sin",
    "sqrt",
    "X",
    "Xm",
    "Xp",
    "Y",
    "Z",
    "Z0",
    "Z1",
]


"""Fetch the functions defined in the __all__ of each sub-module.

Import to the qadence2_expressions name space.
Make sure each added submodule has the respective definition:

    - `__all__ = ["function0", "function1", ...]`

Furthermore, add the submodule to the list below to automatically build
the __all__ of the qadence2_expressions namespace. Make sure to keep alphabetical ordering.
"""

submodules = [
    ".core",
]

for submodule in submodules:
    __all_submodule__ = getattr(import_module(submodule, package="qadence2_expressions"), "__all__")
    __all__ += __all_submodule__
