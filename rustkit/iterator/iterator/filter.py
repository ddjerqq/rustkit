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
    pass


T = TypeVar("T")
U = TypeVar("U")
Acc = TypeVar("Acc")
E = TypeVar("E")
R = Result[T, E]


def _filter_try_fold(
        pred: Callable[[T], bool],
        fold: Callable[[Acc, T], R]
) -> Callable[[Acc, T], R]:
    return lambda acc, item: fold(acc, item) if pred(item) else acc


def _filter_fold(
        pred: Callable[[T], bool],
        fold: Callable[[Acc, T], Acc]
) -> Callable[[Acc, T], Acc]:
    return lambda acc, item: fold(acc, item) if pred(item) else acc


class Filter(Iterator[T]):
    """An iterator that filters the elements of `iter` with `predicate`.

    This `class` is created by the [`filter`] method on [`Iterator`]. See its documentation for more.

    [`filter`]: Iterator.filter
    """

    __iter: Iterator[T]
    __pred: Callable[[T], bool]

    __slots__ = ("__iter", "__pred") + Iterator.__slots__

    def __init__(self: Filter[T], it: Iterator[T], pred: Callable[[T], bool]) -> None:
        self.__iter = it
        self.__pred = pred

    def next(self: Filter[T]) -> Option[T]:
        return self.__iter.find(self.__pred)

    def count(self: Filter[T]) -> int:
        def to_usize(pred: Callable[[T], bool]) -> Callable[[T], int]:
            return lambda x: int(pred(x))

        return self.__iter.map(to_usize(self.__pred)).sum()

    def try_fold(self: Filter[T], accum: Acc, pred: Callable[[Acc, T], R]) -> R:
        return self.__iter.try_fold(accum, _filter_try_fold(self.__pred, pred))

    def fold(self: Filter[T], accum: Acc, func: Callable[[Acc, T], U]) -> U:
        return self.__iter.fold(accum, _filter_fold(self.__pred, func))
