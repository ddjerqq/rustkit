from __future__ import annotations

from typing import (
    Callable,
    TypeVar,
)

from option import Option
from result import Result
from ..iterator.from_fn import from_fn
from .iterator import Iterator

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


class StepBy(Iterator[T]):
    """An iterator for stepping other iterators by a custom amount.

    This `class` is created by the [`step_by`] method on [`Iterator`].
    See its documentation for more.

    [`step_by`]: Iterator.step_by
    [`Iterator`]: iterator.Iterator
    """

    __iter: Iterator[T]
    __step: int
    __first_take: bool

    __slots__ = ("__iter", "__step", "__first_take") + Iterator.__slots__

    def __init__(self: StepBy[T], it: Iterator[T], step: int) -> None:
        if step == 0:
            raise ValueError("cannot step by 0")
        self.__iter = it
        self.__step = step - 1
        self.__first_take = True

    def next(self: StepBy[T]) -> Option[T]:
        if self.__first_take:
            self.__first_take = False
            return self.__iter.next()

        return self.__iter.nth(self.__step)

    def nth(self: StepBy[T], n: int) -> Option[T]:
        if self.__first_take:
            self.__first_take = False
            first = self.__iter.next()
            if n == 0:
                return first
            n -= 1

        # n and self.__step are indices, we need to add 1 to get the amount of elements
        # When calling `.nth`, we need to subtract 1 again to convert back to an index
        # step + 1 can't overflow because `.step_by` sets `self.__step` to `step - 1`
        step = self.__step + 1
        self.__iter.nth(step)
        return self.__iter.nth(n * step - 1)

    def try_fold(self: StepBy[T], accum: U, func: Callable[[U, T], Result[U, E]]) -> Result[U, E]:
        def nth(it: Iterator[T], step: int) -> Callable[[], T]:
            return lambda: it.nth(step)

        if self.__first_take:
            self.__first_take = False
            if (x := self.__iter.next()).is_some():
                accum = func(accum, x)
            else:
                return accum

        return from_fn(nth(self.__iter, self.__step)).try_fold(accum, func)

    def fold(self: StepBy[T], accum: U, func: Callable[[U, T], U]) -> U:
        def nth(it: Iterator[T], step: int) -> Callable[[], T]:
            return lambda: it.nth(step)

        if self.__first_take:
            self.__first_take = False

            if (x := self.__iter.next()).is_some():
                accum = func(accum, x)
            else:
                return accum

        return from_fn(nth(self.__iter, self.__step)).fold(accum, func)
