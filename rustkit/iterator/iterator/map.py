from __future__ import annotations

from typing import (
    Callable,
    TypeVar,
    TYPE_CHECKING,
)

from result import Result
from option import Option
from .iterator import Iterator

if TYPE_CHECKING:
    from iterator.vec import Vec


T = TypeVar("T")
B = TypeVar("B")
Acc = TypeVar("Acc")
E = TypeVar("E")

F = Callable[[T], B]
R = Result[T, E]


def _map_try_fold(
        f: Callable[[T], B],
        g: Callable[[Acc, B], R]
) -> Callable[[Acc, T], R]:
    return lambda acc, elt: g(acc, f(elt))


def _map_fold(
        f: Callable[[T], B],
        g: Callable[[Acc, B], Acc]
) -> Callable[[Acc, T], Acc]:
    return lambda acc, elt: g(acc, f(elt))


class Map(Iterator[T]):
    """An iterator that maps the values of `iter` with `func`.

    This `struct` is created by the [`map`] method on [`Iterator`]. See its
    documentation for more.

    [`map`]: Iterator.map

    >>> c = 0
    >>> def closure(letter: str) -> (str, int):
    ...     c += 1
    ...     return letter, c

    >>> for pair in Vec[str](['a', 'b', 'c']).iter().map(closure):
    >>>     print(f"{pair}")

    This will print `('a', 1), ('b', 2), ('c', 3)`.
    """

    __iter: Iterator[T]
    __func: F

    __slots__ = ("__iter", "__func") + Iterator.__slots__

    def __init__(self: Map[T], it: Iterator[T], func: F) -> None:
        self.__iter = it
        self.__func = func

    def next(self: Map[T]) -> Option[B]:
        return self.__iter.next().map(self.__func)

    def try_fold(self: Map[T], accum: Acc, func: Callable[[Acc, T], R]) -> R:
        return self.__iter.try_fold(accum, _map_try_fold(self.__func, func))

    def fold(self: Map[T], accum: Acc, func: Callable[[Acc, T], Acc]) -> Acc:
        return self.__iter.fold(accum, _map_fold(self.__func, func))
