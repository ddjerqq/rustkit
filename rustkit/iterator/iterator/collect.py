from __future__ import annotations

import functools
from typing import (
    Generic,
    Iterable,
    Protocol,
    TypeVar,
    TYPE_CHECKING,
)

from result import Result, ok
from option import Option

if TYPE_CHECKING:
    from .iterator import Iterator


T = TypeVar("T")


class Collect:
    __iter: Iterator[T]
    __collect_into: Iterable[T]
    __slots__ = ("__iter", "__type__")

    def __init__(self):
        ...

    @classmethod
    @functools.cache
    def __class_getitem__(cls, key: Iterable[T]) -> Collect[T]:
        from ..vec import Vec
        if isinstance(key, (Result, Option, Vec, list, dict, set, tuple)):
            return type(  # type: ignore
                f"Collect[{key.__name__}]",
                (cls,),
                {"__type__": key}
            )
