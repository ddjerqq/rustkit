from __future__ import annotations

from typing import (
    TypeVar,
    Tuple,
    TYPE_CHECKING,
)

from option import Option, some, NONE
from .iterator import Iterator


if TYPE_CHECKING:
    from iterator.vec import Vec


T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


class Zip(Iterator[Tuple[T, U]]):
    """An iterator that iterates two other iterators simultaneously.

    This `struct` is created by [`zip`] or [`Iterator.zip`].
    See their documentation for more.
    """

    __a: Iterator[T]
    __b: Iterator[U]
    __index: int
    __len: int
    __a_len: int

    __type: Tuple[T, U]

    __slots__ = ("__a", "__b", "__index", "__len", "__a_len") + Iterator.__slots__

    def __init__(self: Zip[Tuple[T, U]], a: Iterator[T], b: Iterator[U]) -> None:
        self.__a = a
        self.__b = b
        self.__index = 0
        self.__len = 0
        self.__a_len = 0

    def __super_nth(self, n: int) -> Option[Tuple[T, U]]:
        while (x := Iterator.next(self)).is_some():
            if n == 0:
                return some(x.unwrap())
            n -= 1

        return NONE

    def next(self: Zip[T]) -> Option[Tuple[T, U]]:
        if (x := self.__a.next()).is_none():
            return NONE

        if (y := self.__b.next()).is_none():
            return NONE

        return some((x, y))

    def nth(self: Zip[T], n: int) -> Option[Tuple[T, U]]:
        return self.__super_nth(n)


def zip(a: Iterator[T], b: Iterator[U]) -> Zip[Tuple[T, U]]:
    """Converts the arguments to iterators and zips them.

    See the documentation of [`Iterator.zip`] for more.

    Examples:
        >>> xs = Vec[int]([1, 2, 3])
        >>> ys = Vec[int]([4, 5, 6])
        >>>
        >>> it = zip(xs, ys)
        >>>
        >>> assert it.next().unwrap() == (1, 4)
        >>> assert it.next().unwrap() == (2, 5)
        >>> assert it.next().unwrap() == (3, 6)
        >>> assert it.next().is_none()
        >>>
        >>> # Nested zips are also possible:
        >>> zs = [7, 8, 9]
        >>>
        >>> it = zip(zip(xs, ys), zs)
        >>>
        >>> assert it.next().unwrap() == ((1, 4), 7)
        >>> assert it.next().unwrap() == ((2, 5), 8)
        >>> assert it.next().unwrap() == ((3, 6), 9)
        >>> assert it.next().is_none()
    """
    return Zip(a, b)
