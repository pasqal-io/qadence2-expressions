from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Numeric(Protocol):
    """
    Protocol class to represent Python base classes for numeric values,
    such as complex, float, int, but also include packages types, such
    as numpy and torch. It is especially useful for handling operations
    with Expressions and any kind of "Numeric" type.
    """

    def __add__(self, *args: Any, **kwargs: Any) -> Any: ...

    @property
    def real(self, *args: Any, **kwargs: Any) -> Any: ...

    def __eq__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __mul__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __ne__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __neg__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __pow__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __sub__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __truediv__(self, *args: Any, **kwargs: Any) -> Any: ...
