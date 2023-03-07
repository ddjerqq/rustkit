from __future__ import annotations

from typing import (
    Callable,
    Tuple,
    TypeVar,
)

from result import Result
from option import Option, some, NONE
from .iterator import Iterator


T = TypeVar("T")
Acc = TypeVar("Acc")
E = TypeVar("E")
R = Result[T, E]


class Enumerate(Iterator[T]):
    """An iterator that yields the current count and the element during iteration.

    This `struct` is created by the [`enumerate`] method on [`Iterator`]. See its
    documentation for more.

    [`enumerate`]: Iterator.enumerate
    """

    __type__: Tuple[int, T]

    __iter: Iterator[T]
    __count: int

    __slots__ = ("__iter", "__count") + Iterator.__slots__

    def __init__(self: Enumerate[T], it: Iterator[T]) -> None:
        self.__iter = it
        self.__count = 0

    def next(self: Enumerate[T]) -> Option[Tuple[int, T]]:
        if (a := self.__iter.next()).is_none():
            return NONE
        # Safety: we can unwrap safely, because if `a` were none, we would return.
        a = a.unwrap()
        i = self.__count
        self.__count += 1
        return some((i, a))

    def nth(self: Enumerate[T], n: int) -> Option[Tuple[int, T]]:
        if (a := self.__iter.next()).is_none():
            return NONE
        # Safety: we can unwrap safely, because if `a` were none, we would return.
        a = a.unwrap()
        i = self.__count + n
        self.__count += 1
        return some((i, a))

    def count(self: Enumerate[T]) -> int:
        return self.__iter.count()

    def try_fold(self: Enumerate[T], accum: Acc, fold: Callable[[Acc, T], R]) -> R:
        def _enumerate(count: int, _fold: Callable[[Acc, Tuple[int, T]], R]) -> Callable[[Acc, T], R]:
            def __fold(acc: Acc, item: T) -> R:
                nonlocal count
                acc = _fold(acc, (count, item))
                count += 1
                return acc
            return __fold

        return self.__iter.try_fold(accum, _enumerate(self.__count, fold))

    def fold(self: Enumerate[T], accum: Acc, fold: Callable[[Acc, T], Acc]) -> Acc:
        def _enumerate(count: int, _fold: Callable[[Acc, Tuple[int, T]], Acc]) -> Callable[[Acc, T], Acc]:
            def __fold(acc: Acc, item: T) -> Acc:
                nonlocal count
                acc = _fold(acc, (count, item))
                count += 1
                return acc
            return __fold

        return self.__iter.fold(accum, _enumerate(self.__count, fold))

    def advance_by(self: Enumerate[T], n: int) -> Result[..., int]:
        res = self.__iter.advance_by(n)
        if res.is_ok():
            self.__count += n
            return res
        else:
            def inspector(advanced: int) -> None:
                self.__count += advanced

            res.inspect_err(inspector)
            return res
