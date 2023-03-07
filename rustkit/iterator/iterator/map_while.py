from __future__ import annotations

from typing import (
    Callable,
    TypeVar,
    TYPE_CHECKING,
)

from result import Result, ok
from option import Option, NONE
from .iterator import Iterator

if TYPE_CHECKING:
    pass


T = TypeVar("T")
U = TypeVar("U")
Acc = TypeVar("Acc")
E = TypeVar("E")

R = Result[T, E]


class MapWhile(Iterator[T]):
    """An iterator that only accepts elements while `predicate` returns `Some(_)`.

    This `class` is created by the [`map_while`] method on [`Iterator`]. See its
    documentation for more.

    [`map_while`]: Iterator.map_while
    """
    __iter: Iterator[T]
    __predicate: Callable[[T], Option[U]]
    __type__ = U

    def __init__(self, it: Iterator[T], predicate: Callable[[T], Option[U]]) -> None:
        self.__iter = it
        self.__predicate = predicate

    def next(self: MapWhile[T]) -> Option[U]:
        if (x := self.__iter.next()).is_none():
            return NONE
        else:
            x = x.unwrap()
            return self.__predicate(x)

    def try_fold(self: MapWhile[T], accum: Acc, func: Callable[[Acc, T], Result[T, E]]) -> R:
        def f(acc: Acc, x: T) -> R:
            if (x := self.__predicate(x)).is_some():
                item = x.unwrap()
                return ok(func(acc, item))
            else:
                return ok(accum)

        return self.__iter.try_fold(accum, f)

    def fold(self: MapWhile[T], accum: Acc, func: Callable[[Acc, T], Acc]) -> Acc:
        def _ok(f: Callable[[U, T], U]) -> Callable[[U, T], Result[U, ...]]:
            def inner(acc, x) -> Result[U, ...]:
                return ok(f(acc, x))
            return inner

        # Safety: we are making the _ok func infallible above;
        return self.try_fold(accum, _ok(func)).unwrap()
