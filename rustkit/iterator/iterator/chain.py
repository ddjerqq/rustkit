from __future__ import annotations

from typing import (
    Callable,
    TypeVar,
    TYPE_CHECKING,
)

from option import Option, some, NONE
from result import Result, ok, err
from .iterator import Iterator


if TYPE_CHECKING:
    from iterator.vec import Vec


T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


class Chain(Iterator[T]):
    """An iterator that links two iterators together, in a chain.

    This `object` is created by [`Iterator.chain`]. See its documentation for more.

    Examples:
        >>> a1 = Vec[int]([1, 2, 3])
        >>> a2 = Vec[int]([4, 5, 6])
        >>> it: Chain[int] = a1.iter().chain(a2.iter())
    """

    __a: Option[Iterator[T]]
    __b: Option[Iterator[T]]

    __slots__ = ("__a", "__b") + Iterator.__slots__

    def __init__(self: Chain[T], a: Iterator[T], b: Iterator[T]) -> None:
        self.__a = some(a)
        self.__b = some(b)

    def next(self: Chain[T]) -> Option[T]:
        if self.__b.is_none():
            return self.__b

        return and_then_or_clear(self.__a, Iterator.next).or_else(lambda: self.__b.unwrap().next())

    def count(self: Chain[T]) -> int:
        a_count = self.__a.map_or(0, Iterator.count)
        b_count = self.__b.map_or(0, Iterator.count)
        return a_count + b_count

    def try_fold(self: Chain[T], accum: U, func: Callable[[U, T], Result[T, E]]) -> Result[T, E]:
        if self.__a.is_some():
            a = self.__a.unwrap()
            accum = a.try_fold(accum, func)
            if accum.is_err():
                return accum
            self.__a = NONE

        if self.__b.is_some():
            a = self.__b.unwrap()
            accum = a.try_fold(accum, func)
            if accum.is_err():
                return accum
            # we don't fuse the second iterator

        return accum

    def fold(self: Chain[T], accum: U, func: Callable[[U, T], U]) -> U:
        if self.__a.is_some():
            a = self.__a.unwrap()
            accum = a.fold(accum, func)

        if self.__b.is_some():
            a = self.__b.unwrap()
            accum = a.try_fold(accum, func)

        return accum

    def advance_by(self: Chain[T], n: int) -> Result[..., int]:
        rem = n

        if self.__a.is_some():
            a: Iterator[T] = self.__a.unwrap()
            res = a.advance_by(rem)

            if res.is_ok():
                return ok(...)

            # Safety: we made sure that the res is of err variant
            k = res.unwrap_err()
            rem -= k

            self.__a = NONE

        if self.__b.is_some():
            b: Iterator[T] = self.__b.unwrap()
            res = b.advance_by(rem)

            if res.is_ok():
                return ok(...)

            # Safety: we made sure that the res is of err variant
            k = res.unwrap_err()
            rem -= k

        if rem == 0:
            return ok(...)

        return err(n - rem)

    def nth(self: Chain[T], n: int) -> Option[T]:
        if self.__a.is_some():
            a: Iterator[T] = self.__a.unwrap()
            res = a.advance_by(n)
            if res.is_ok():
                if (res := a.next()).is_none():
                    n = 0
                else:
                    return res
            else:
                # Safety: we made sure that the res is of err variant
                k = res.unwrap_err()
                n -= k

            self.__a = NONE

        if self.__b.is_none():
            return NONE

        return self.__b.unwrap().nth(n)

    def find(self: Chain[T], predicate: Callable[[T], bool]) -> Option[T]:
        def or_else() -> Option[T]:
            if self.__b.is_none():
                return NONE
            b = self.__b.unwrap()
            return b.find(predicate)

        return and_then_or_clear(self.__a, lambda a: a.find(predicate)).or_else(or_else)

    def last(self: Chain[T]) -> Option[T]:
        a_last = self.__a.and_then(Iterator.last)
        b_last = self.__b.and_then(Iterator.last)
        return a_last.or_(b_last)


def and_then_or_clear(option: Option[T], func: Callable[[T], Option[U]]) -> Option[U]:
    if option.is_none():
        return option

    # Safety: we just checked if the option was None or not.
    x = func(option.unwrap())

    if x.is_none():
        option.insert(None)

    return x
