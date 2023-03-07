from typing import Callable
from typing import Generic
from typing import TypeVar

from..iterator import Iterator
from option import Option, some, NONE

T = TypeVar("T")
F = Callable[[], Option[T]]


class FromFn(Iterator[T]):
    __slots__ = Iterator.__slots__ + ("__func",)

    def __init__(self, func: F) -> None:
        self.__func = func

    def next(self) -> Option[T]:
        return self.__func()

    def __repr__(self) -> str:
        return f"FromFn({self.__func})"



def from_fn(func: F) -> FromFn[F]:
    """Creates a new iterator where each iteration calls the provided closure
    `F: () -> Option[T]`.

    This allows creating a custom iterator with any behavior
    without using the more verbose syntax of creating a dedicated type
    and implementing the [`Iterator`] trait for it.

    # Examples

    # Let's re-implement the counter iterator from [module-level documentation]:

    >>> count = 0
    >>> def closure():
    ...     # Increment our count. This is why we started at zero.
    ...     count += 1
    ...     # Check to see if we've finished counting or not.
    ...     if count < 6:
    ...         return some(count)
    ...     else:
    ...         NONE

    >>> counter = from_fn(closure)

    >>> assert counter.collect() == [1, 2, 3, 4, 5]
    """
    return FromFn(func)

