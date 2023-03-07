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
    from iterator.vec import Vec


T = TypeVar("T")
B = TypeVar("B")
Acc = TypeVar("Acc")
E = TypeVar("E")

F = Callable[[T], B]
R = Result[T, E]


class Peekable(Iterator[T]):
    """An iterator with a `peek()` that returns an optional reference to the next
    element.

    This `class` is created by the [`peekable`] method on [`Iterator`]. See its
    documentation for more.

    [`peekable`]: Iterator.peekable
    """
    __iter: Iterator[T]
    __peeked: Option[Option[T]]

    __slots__ = ("__iter", "__peeked") + Iterator.__slots__

    def __init__(self: Peekable[T], it: Iterator[T]) -> None:
        self.__iter = it
        self.__peeked = NONE

    def next(self: Peekable[T]) -> Option[T]:
        if (v := self.__peeked.take()).is_some():
            return v
        return self.__iter.next()

    def count(self: Peekable[T]) -> int:
        peeked: Option[Option[T]] = self.__peeked.take()

        if peeked.is_some():
            # Safety: we just checked if peeked is some
            inner: Option[T] = peeked.unwrap()

            if inner.is_none():
                return 0

            return 1 + self.__iter.count()

        return self.__iter.count()

    def nth(self: Peekable[T], n: int) -> Option[T]:
        peeked: Option[Option[T]] = self.__peeked.take()

        if peeked.is_some():
            # Safety: we just checked if peeked is some
            inner: Option[T] = peeked.unwrap()

            if inner.is_none():
                return NONE

            elif inner.is_some() and n == 0:
                return inner

            else:
                return self.__iter.nth(n - 1)

        return self.__iter.nth(n)

    def last(self: Peekable[T]) -> Option[T]:
        peeked: Option[Option[T]] = self.__peeked.take()

        peek_opt = None

        if peeked.is_some():
            # Safety: we just checked if peeked is some
            inner: Option[T] = peeked.unwrap()

            if inner.is_none():
                return NONE

            elif inner.is_some():
                peek_opt = inner

        else:
            peek_opt = NONE

        return self.__iter.last().or_(peek_opt)

    def try_fold(self: Peekable[T], accum: Acc, func: Callable[[Acc, T], Result[T, E]]) -> Result[T, E]:
        peeked: Option[Option[T]] = self.__peeked.take()

        acc = None

        if peeked.is_some():
            # Safety: we just checked if peeked is some
            inner: Option[T] = peeked.unwrap()

            if inner.is_none():
                return ok(accum)

            elif inner.is_some():
                # Safety: we just checked if peeked is some
                v = inner.unwrap()
                if (res := func(accum, v)).is_err():
                    return res
                else:
                    acc = res

        else:
            acc = accum

        return self.__iter.try_fold(acc, func)

    def fold(self: Peekable[T], accum: Acc, func: Callable[[Acc, T], Acc]) -> Acc:
        peeked: Option[Option[T]] = self.__peeked.take()

        acc = None

        if peeked.is_some():
            # Safety: we just checked if peeked is some
            inner: Option[T] = peeked.unwrap()

            if inner.is_none():
                return accum

            elif inner.is_some():
                # Safety: we just checked if peeked is some
                v = inner.unwrap()
                acc = func(accum, v)

        else:
            acc = accum

        return self.__iter.fold(acc, func)

    def peek(self: Peekable[T]) -> Option[T]:
        """Returns a reference to the next() value without advancing the iterator.

        Like [`next`], if there is a value, it is wrapped in a `Some(T)`.
        But if the iteration is over, `NONE` is returned.

        [`next`]: Iterator.next

        Examples:
            >>> xs = Vec[int]([1, 2, 3])

            >>> it = xs.iter().peekable()

            >>> # peek() lets us see into the future
            >>> assert it.peek() == some(1)
            >>> assert it.next() == some(1)

            >>> assert it.next() == some(2)

            >>> # The iterator does not advance even if we `peek` multiple times
            >>> assert it.peek() == some(3)
            >>> assert it.peek() == some(3)

            >>> assert it.next() == some(3)

            >>> # After the iterator is finished, so is `peek()`
            >>> assert it.peek() == NONE
            >>> assert it.next() == NONE
        """
        return self.__peeked.get_or_insert_with(lambda: self.__iter.next())

    def next_if(self: Peekable[T], func: Callable[[T], bool]) -> Option[T]:
        """
        Consume and return the next value of this iterator if a condition is true.

        If `func` returns `true` for the next value of this iterator, consume and return it.
        Otherwise, return `None`.

        Examples:
            >>> # Consume a number if it's equal to 0.
            >>> it = Vec[int](range(10)).iter().peekable()
            >>> # The first item of the iterator is 0; consume it.
            >>> assert it.next_if(lambda x: x == 0) == some(0)
            >>> # The next item returned is now 1, so `consume` will return `false`.
            >>> assert it.next_if(lambda x: x == 0) == NONE
            >>> # `next_if` saves the value of the next item if it was not equal to `expected`.
            >>> assert it.next() == some(1)

            >>> # Consume any number less than 10.
            >>> it = Vec[int](range(20)).iter().peekable()
            >>> # Consume all numbers less than 10
            >>> while it.next_if(lambda x: x < 10).is_some() {}
            >>> # or more esoteric way
            >>> # while it.next_if((10).__gt__).is_some() {}
            >>> # The next value returned will be 10
            >>> assert it.next() == some(10)
        """
        if (nxt := self.next()).is_some_and(func):
            return nxt
        else:
            self.__peeked = some(nxt)
            return NONE

    def next_if_eq(self: Peekable[T], expected: T) -> Option[T]:
        return self.next_if(lambda nxt: nxt == expected)
