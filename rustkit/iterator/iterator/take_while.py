from __future__ import annotations

from typing import (
    Callable,
    TypeVar,
    TYPE_CHECKING,
)

from result import Result, ok
from option import Option, some, NONE
from .iterator import Iterator

if TYPE_CHECKING:
    pass


T = TypeVar("T")
B = TypeVar("B")
Acc = TypeVar("Acc")
E = TypeVar("E")

F = Callable[[T], B]
R = Result[T, E]


class TakeWhile(Iterator[T]):
    """An iterator that only accepts elements while `predicate` returns `true`.

    This `class` is created by the [`take_while`] method on [`Iterator`]. See its
    documentation for more.

    [`take_while`]: Iterator.take_while
    """
    __iter: Iterator[T]
    __flag: bool
    __predicate: Callable[[T], bool]

    def __init__(self, it: Iterator[T], predicate: Callable[[T], bool]) -> None:
        self.__iter = it
        self.__flag = False
        self.__predicate = predicate

    def next(self: TakeWhile[T]) -> Option[T]:
        if self.__flag:
            return NONE
        else:
            if (x := self.__iter.next()).is_none():
                return NONE

            if self.__predicate(x):
                return some(x)
            else:
                self.__flag = True
                return NONE

    def try_fold(self: TakeWhile[T], accum: Acc, func: Callable[[Acc, T], Result[T, E]]) -> Result[T, E]:
        def check(pred: Callable[[T], bool], fold: Callable[[Acc, T], Result[T, E]]) -> Callable[[Acc, T], Result[T, E]]:
            def inner(acc: Acc, x: T) -> Result[T, E]:
                if pred(x):
                    return fold(acc, x)
                else:
                    self.__flag = True

            return inner

        if self.__flag:
            return ok(accum)
        else:
            return self.__iter.try_fold(accum, check(self.__predicate, func))

    def fold(self: TakeWhile[T], accum: Acc, func: Callable[[Acc, T], Acc]) -> Acc:
        def _ok(f: Callable[[B, T], B]) -> Callable[[B, T], Result[B, ...]]:
            def inner(acc, x) -> Result[B, ...]:
                return ok(f(acc, x))
            return inner

        # Safety: we are making the _ok func infallible above;
        return self.try_fold(accum, _ok(func)).unwrap()
