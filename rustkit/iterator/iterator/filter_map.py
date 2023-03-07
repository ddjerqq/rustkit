from __future__ import annotations

from typing import (
    Callable,
    TypeVar,
)

from result import Result
from option import Option
from .iterator import Iterator

T = TypeVar("T")
U = TypeVar("U")
B = TypeVar("B")
Acc = TypeVar("Acc")
E = TypeVar("E")
R = Result[T, E]


def _filter_map_try_fold(
        f: Callable[[T], Option[B]],
        fold: Callable[[Acc, B], R]
) -> Callable[[Acc, T], R]:
    def _fold(acc: Acc, item: T) -> R:
        if (x := f(item)).is_some():
            return fold(acc, x)
        return acc
    return _fold


def _filter_map_fold(
        f: Callable[[T], Option[B]],
        fold: Callable[[Acc, B], Acc]
) -> Callable[[Acc, T], Acc]:
    def _fold(acc: Acc, item: T) -> R:
        if (x := f(item)).is_some():
            return fold(acc, x)
        return acc

    return _fold


class FilterMap(Iterator[T]):
    """An iterator that filters the elements of `iter` with `predicate`.

    This `class` is created by the [`filter`] method on [`Iterator`]. See its documentation for more.

    [`filter`]: Iterator.filter
    """

    __iter: Iterator[T]
    __func: Callable[[T], Option[B]]

    __slots__ = ("__iter", "__func") + Iterator.__slots__

    def __init__(self: FilterMap[T], it: Iterator[T], f: Callable[[T], Option[B]]) -> None:
        self.__iter = it
        self.__func = f

    def next(self: FilterMap[T]) -> Option[B]:
        return self.__iter.find_map(self.__func)

    def try_fold(self: FilterMap[T], accum: Acc, fold: Callable[[Acc, T], Result[Acc, E]]) -> Result[Acc, E]:
        return self.__iter.try_fold(accum, _filter_map_try_fold(self.__func, fold))

    def fold(self: FilterMap[T], accum: Acc, fold: Callable[[Acc, T], Acc]) -> Acc:
        return self.__iter.fold(accum, _filter_map_fold(self.__func, fold))
