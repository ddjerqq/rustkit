from __future__ import annotations

from typing import (
    Callable,
    TypeVar,
    TYPE_CHECKING,
)

from result import Result, ok
from option import Option
from .iterator import Iterator

if TYPE_CHECKING:
    pass


T = TypeVar("T")
B = TypeVar("B")
Acc = TypeVar("Acc")
E = TypeVar("E")

F = Callable[[T], B]
R = Result[T, E]


class SkipWhile(Iterator[T]):
    """An iterator that rejects elements while `predicate` returns `true`.

    This `struct` is created by the [`skip_while`] method on [`Iterator`]. See its
    documentation for more.

    [`skip_while`]: Iterator.skip_while
    """
    __iter: Iterator[T]
    __flag: bool
    __predicate: Callable[[T], bool]

    def __init__(self, it: Iterator[T], predicate: Callable[[T], bool]) -> None:
        self.__iter = it
        self.__flag = False
        self.__predicate = predicate

    def next(self: SkipWhile[T]) -> Option[T]:
        def check(flag: bool, pred: Callable[[T], bool]) -> Callable[[T], bool]:
            def inner(x: T) -> bool:
                if flag or not pred(x):
                    self.__flag = True
                    return True
                else:
                    return False
            return inner

        return self.__iter.find(check(self.__flag, self.__predicate))

    def try_fold(self: SkipWhile[T], accum: Acc, func: Callable[[Acc, T], Result[T, E]]) -> Result[T, E]:
        if not self.__flag:
            if (nxt := self.next()).is_some():
                v = nxt.unwrap()
                if (res := func(accum, v)).is_ok():
                    accum = res
                else:
                    return res
            else:
                return ok(accum)

        return self.__iter.try_fold(accum, func)

    def fold(self: SkipWhile[T], accum: Acc, func: Callable[[Acc, T], Acc]) -> Acc:
        if not self.__flag:
            if (nxt := self.next()).is_some():
                v = nxt.unwrap()
                accum = func(accum, v)
            else:
                return accum

        return self.__iter.fold(accum, func)
