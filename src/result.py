"""
# Error handling with the `Result` type.

[`Result[T, E]`] is the type used for returning and propagating
errors. It is an enum with the variants, [`Ok(T)`], representing
success and containing a value, and [`Err(E)`], representing error
and containing an error value.

Functions return [`Result`] whenever errors are expected and recoverable.

A simple function returning [`Result`] might be
defined and used like so:

>>> def double_number(number_str: str) -> Result[int, TypeError]:
...     # Parse the string to a number. This will return a `Result` with the
...     # value, or the error if it couldn't be parsed.
...     val = Result.from_(lambda: int(number_str))
...     # or
...     val = Result.from_(int, number_str)
...     return val

## Results must be used

A common problem with using return values to indicate errors is
that it is easy to ignore the return value, thus failing to handle
the error.

When writing code that calls many functions that return the
[`Result`] type, the error handling can be tedious.

## Method overview:

In addition to working with pattern matching, [`Result`] provides a
wide variety of different methods.

### Querying the variant

The [`is_ok`] and [`is_err`] methods return [`True`] if the [`Result`]
is [`Ok`] or [`Err`], respectively.

### Extracting contained values

These methods extract the contained value in a [`Result[T, E]`] when it
is the [`Ok`] variant. If the [`Result`] is [`Err`]:

* [`expect`] panics with a provided custom message
* [`unwrap`] panics with a generic message
* [`unwrap_or`] returns the provided default value
* [`unwrap_or_else`] returns the result of evaluating the provided
  function

These methods extract the contained value in a [`Result[T, E]`] when it
is the [`Err`] variant.
If the [`Result`] is [`Ok`]: raise UnwrapError

* [`expect_err`] raises an UnwrapError with a provided custom message
* [`unwrap_err`] raises an UnwrapError with a generic message

### Transforming contained values

These methods transform [`Result[T, U]`] to [`Option[T]`]:

* [`Result.err`] transforms [`Result[T, E]`] into [`Option[E]`],
  mapping [`Err(e)`] to [`Some(e)`] and [`Ok(v)`] to [`None`]
* [`Result.ok`] transforms [`Result[T, E]`] into [`Option[T]`],
  mapping [`Ok(v)`] to [`Some(v)`] and [`Err(e)`] to [`None`]
* [`transpose`] transposes a [`Result`] of an [`Option`] into an
  [`Option`] of a [`Result`]

#### This method transforms the contained value of the [`Ok`] variant:

* [`map`] transforms [`Result[T, E]`] into [`Result[U, E]`] by applying
  the provided function to the contained value of [`Ok`] and leaving
  [`Err`] values unchanged

This method transforms the contained value of the [`Err`] variant:

* [`map_err`] transforms [`Result[T, E]`] into [`Result[T, F]`] by
  applying the provided function to the contained value of [`Err`] and
  leaving [`Ok`] values unchanged

#### These methods transform a [`Result[T, E]`] into a value of a possibly different type `U`:

* [`map_or`] applies the provided function to the contained value of
  [`Ok`], or returns the provided default value if the [`Result`] is [`Err`]
* [`map_or_else`] applies the provided function to the contained value
  of [`Ok`], or applies the provided default fallback function to the contained value of [`Err`]

### Boolean operators

These methods treat the [`Result`] as a boolean value, where [`Ok`]
acts like [`True`] and [`Err`] acts like [`False`]. There are two
categories of these methods: ones that take a [`Result`] as input, and
ones that take a function as input (to be lazily evaluated).

The [`and_`] and [`or_`] methods take another [`Result`] as input, and
produce a [`Result`] as output. The [`and_`] method can produce a
[`Result[U, E]`] value having a different inner type `U` than
[`Result[T, E]`]. The [`or_`] method can produce a [`Result[T, V]`]
value having a different error type `V` than [`Result[T, V]`].

```md
| method  | self     | input     | output   |
|---------|----------|-----------|----------|
| [`and`] | `Err(e)` | (ignored) | `Err(e)` |
| [`and`] | `Ok(x)`  | `Err(d)`  | `Err(d)` |
| [`and`] | `Ok(x)`  | `Ok(y)`   | `Ok(y)`  |
| [`or`]  | `Err(e)` | `Err(d)`  | `Err(d)` |
| [`or`]  | `Err(e)` | `Ok(y)`   | `Ok(y)`  |
| [`or`]  | `Ok(x)`  | (ignored) | `Ok(x)`  |
```

The [`and_then`] and [`or_else`] methods take a function as input, and
only evaluate the function when they need to produce a new value. The
[`and_then`] method can produce a [`Result[U, E]`] value having a
different inner type `U` than [`Result[T, E]`]. The [`or_else`] method
can produce a [`Result[T, F]`] value having a different error type `F`
than [`Result[T, E]`].

```md
| method       | self     | function input | function result | output   |
|--------------|----------|----------------|-----------------|----------|
| [`and_then`] | `Err(e)` | (not provided) | (not evaluated) | `Err(e)` |
| [`and_then`] | `Ok(x)`  | `x`            | `Err(d)`        | `Err(d)` |
| [`and_then`] | `Ok(x)`  | `x`            | `Ok(y)`         | `Ok(y)`  |
| [`or_else`]  | `Err(e)` | `e`            | `Err(d)`        | `Err(d)` |
| [`or_else`]  | `Err(e)` | `e`            | `Ok(y)`         | `Ok(y)`  |
| [`or_else`]  | `Ok(x)`  | (not provided) | (not evaluated) | `Ok(x)`  |
```

### Comparison operators
>>> assert ok(1) < err(0)

>>> x = ok(0)
>>> y = ok(1)
>>> assert x < y

>>> x = ok(0)
>>> y = ok(1)
>>> assert x < y

### Collecting into `Result`

[`Result`] implements the [`from_`] method, which can be used to
collect a [`Result`] from an function call.

>>> res: Result[float, Exception] = Result.from_(lambda: 1 / 0)
>>> assert res.is_err()
>>> assert res.err() == ZeroDivisionError('division by zero')
"""

from __future__ import annotations
import asyncio as aio
import functools
from typing import (
    Any,
    Callable,
    Generic,
    TypeVar,
    TYPE_CHECKING,
    Coroutine,
)
from .error import UnwrapError

if TYPE_CHECKING:
    from .option import Option, some, none

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
E = TypeVar("E")
R = TypeVar("R", bound="Result")
Arg = TypeVar("Arg")


__all__ = (
    "Result",
    "ok",
    "err",
)


class Result(Generic[T, E]):
    """Error handling with the [`Result[T,] E]` type.

    [`Result[T,] E]` is the type used for returning and propagating errors.
    It is an enum with the variants, [`Ok(T)`] representing success and containing a value,
    and [`Err(E)`] representing error and containing an error value.
    """
    __is_ok: bool
    __value: T | E
    __slots__ = ("__is_ok", "__value")

    ###########################################################################
    # Creating the Result objects
    ###########################################################################

    def __init__(self: Result[T, E], is_ok: bool, value: T, *, _force: bool = False) -> None:
        """DO NOT DIRECTLY INITIALIZE THE RESULT TYPE!!!
        """
        if not _force:
            raise RuntimeError(
                "you may not create the result type directly. \n"
                "instead use one of the provided factory methods"
            )

        self.__is_ok = is_ok
        self.__value = value

    @classmethod
    def from_(
            cls,
            func: Callable[[...], Coroutine[Any, Any, T]] | Callable[[...], T] | Coroutine[Any, Any, T],
            *args,
            loop: aio.AbstractEventLoop = None,
            **kwargs
    ) -> Result[T, E]:
        """Collect the result of a function in a [`Result[T, E]`]

        Examples:
            >>> res: Result[float, Exception] = Result.from_(lambda: 1 / 0)
            >>> assert res.is_err()

            >>> async def coro():
            ...     return 1 / 0
            >>> res: Result[float, Exception] = Result.from_(coro)

        Args:
            func: the function to call
            *args: the arguments to pass to the function
            loop: the event loop to use for the coroutine, default to the current running loop
            **kwargs: the keyword arguments to pass to the function

        Raises:
            TypeError: if the function is not a callable, coroutine or a coroutine function

        Returns:
            [`Result[T, E]`]
            if the function returns a value, returns `ok(T)`
            if the function raises an exception, returns `err(E)`
        """
        if aio.iscoroutinefunction(func):
            func = func(*args, **kwargs)

        if aio.iscoroutine(func):
            loop = loop or aio.get_event_loop()
            try:
                return ok(loop.run_until_complete(func))
            except Exception as e:
                return err(e)

        if callable(func):
            try:
                return ok(func(*args, **kwargs))
            except Exception as e:
                return err(e)

        raise TypeError(f"func must be a callable or a coroutine, not {func.__class__.__name__}")

    ###########################################################################
    # Querying the contained values
    ###########################################################################

    def is_ok(self) -> bool:
        """Returns true if the result is [`Ok(T)`.]

        Examples:
            >>> x = ok(2)
            >>> assert x.is_ok()
        """
        return self.__is_ok

    def is_ok_and(self: Result[T, E], func: Callable[[T], bool]) -> bool:
        """Returns true if the result is [`Ok(T)`] and the function returns true.

        Examples:
            >>> x = ok(2)
            >>> assert x.is_ok_and(lambda i: i == 2)
        """
        if self.is_err():
            return False

        return func(self.__value)

    def is_err(self: Result[T, E]) -> bool:
        """Returns true if the result is [`Err(E)`.]

        Examples:
            >>> x = err("Nothing here")
            >>> assert x.is_err()
        """
        return not self.__is_ok

    def is_err_and(self: Result[T, E], func: Callable[[E], bool]) -> bool:
        """Returns true if the result is [`Err(E)`] and the function returns true.

        Examples:
            >>> x = err("Nothing here")
            >>> assert x.is_err_and(lambda i: i == "Nothing here")
        """
        if self.is_ok():
            return False

        return func(self.__value)

    ###########################################################################
    # Transforming contained values
    ###########################################################################

    def map(self: Result[T, E], func: Callable[[T], U]) -> Result[U, E]:
        """Maps a `Result[T, E]` to `Result[U, E]` by applying a function to a contained [`Ok(T)`] value.

        This function can be used to compose the results of two functions.

        Examples:
            >>> x = ok(2)
            >>> assert x.map(lambda i: i + 1) == ok(3)
        """
        if self.is_ok():
            return ok(func(self.__value))

        return self

    def map_or(self: Result[T, E], default: U, func: Callable[[T], U]) -> U:
        """Returns the provided default (if [`Err`]), or
        applies a function to the contained value (if [`Ok`]),

        Arguments passed to `map_or` are eagerly evaluated; if you are passing
        the result of a function call, it is recommended to use [`map_or_else`],
        which is lazily evaluated.

        [`map_or_else`]: Result.map_or_else

        Examples:
            >>> assert ok(2).map_or(0, lambda i: i + 1) == 3

            >>> assert err(0).map_or(0, lambda i: i + 1) == 0
        """
        if self.is_ok():
            return func(self.__value)

        return default

    def map_or_else(self: Result[T, E], default: Callable[[E], U], func: Callable[[T], U]) -> U:
        """Returns the provided default (if [`Err`]), or
        applies a function to the contained value (if [`Ok`]),
        lazily evaluating the default function.

        Examples:
            >>> x = ok(2)
            >>> assert x.map_or_else(int, lambda i: i + 1) == 3
        """
        if self.is_ok():
            return func(self.__value)

        return default(self.__value)

    def map_err(self: Result[T, E], func: Callable[[E], V]) -> Result[T, V]:
        """Maps a `Result[T, E]` to `Result[T, V]` by applying a function to a contained [`Err(E)`] value.

        This function can be used to pass through a successful result while handling an error.

        Examples:
            >>> x = err("Nothing here")
            >>> assert x.map_err(lambda i: i + " again") == err("Nothing here again")
        """
        if self.is_ok():
            return self

        return err(func(self.__value))

    def inspect(self: Result[T, E], func: Callable[[T], None]) -> Result[T, E]:
        """Inspect the value of a [`Result[T, E]`].

        This function can be used to inspect the value of a [`Result[T, E]`] without changing it.

        Examples:
            >>> x = ok(2)
            >>> assert x.inspect(lambda i: print(i)) == ok(2)
        """
        if self.is_ok():
            func(self.__value)

        return self

    def inspect_err(self: Result[T, E], func: Callable[[E], None]) -> Result[T, E]:
        """Inspect the error of a [`Result[T, E]`].

        This function can be used to inspect the error of a [`Result[T, E]`] without changing it.

        Examples:
            >>> x = err("Nothing here")
            >>> assert x.inspect_err(print) == err("Nothing here")
        """
        if self.is_err():
            func(self.__value)

        return self

    ###########################################################################
    # Extract a value
    ###########################################################################

    def ok(self: Result[T, E]) -> Option[T]:
        """Returns [`Some(T)`] if the result is [`Ok(T)`], otherwise [`None`].

        Examples:
            >>> x = ok(2)
            >>> assert x.ok() == some(2)
        """
        from .option import some, none
        return some(self.__value) if self.is_ok() else none()

    def err(self: Result[T, E]) -> Option[E]:
        """Returns [`Some(E)`] if the result is [`Err(E)`], otherwise [`None`].

        Examples:
            >>> x = err("Nothing here")
            >>> assert x.err() == some("Nothing here")
        """
        from .option import some, none
        return none() if self.is_ok() else some(self.__value)

    def expect(self: Result[T, E], msg: str) -> T:
        """Unwraps a result, yielding the content of an [`Ok(T)`.]
        Else, it returns the provided default.

        Arguments passed to `expect` are eagerly evaluated; if you are passing
        the result of a function call, it is recommended to use [`expect_err`],
        which is lazily evaluated.

        [`expect_err`]: Result.expect_err

        Examples:
            >>> x = ok(2)
            >>> assert x.expect("Nothing here") == 2

            >>> x = err("Nothing here")
            >>> assert x.expect("Nothing here") == "Nothing here"

        Raises:
            UnwrapError: If the value is an [`Err(E)`.]
        """
        if self.is_ok():
            return self.__value

        if isinstance(self.__value, Exception):
            raise UnwrapError(msg) from self.__value

        raise UnwrapError(msg)

    def expect_err(self: Result[T, E], msg: str) -> E:
        """Returns the contained [`Err`] value, consuming the `self` value.

        [`expect_err`]: Result.expect_err

        Examples:
            >>> x: Result[int, str] = ok(2)
            >>> assert x.expect_err("fail")  # raises UnwrapError

            >>> x: Result[int, str] = err("Nothing here")
            >>> assert x.expect_err("fail") == "Nothing here"

        Raises:
            UnwrapError: If the value is an [`Ok(T)`].
        """
        if self.is_ok():
            if isinstance(self.__value, Exception):
                raise UnwrapError(msg) from self.__value

            raise UnwrapError(msg)

        return self.__value

    def unwrap(self: Result[T, E]) -> T:
        """Unwraps a result, yielding the content of an [`Ok(T)`.]

        Raises:
            UnwrapError: If the value is an [`Err(E)`.]

        Examples:
            >>> x = ok(2)
            >>> assert x.unwrap() == 2

            >>> x = err("Nothing here")
            >>> assert x.unwrap()  # raises UnwrapError("called `Result.unwrap()` on an `Err` value")

        Raises:
            UnwrapError: If the value is an [`Err(E)`.] or an instance of `Exception`.
        """
        if self.is_ok():
            return self.__value

        if isinstance(self.__value, Exception):
            raise UnwrapError("called `Result.unwrap` on an `Err` value") from self.__value

        raise UnwrapError("called `Result.unwrap` on an `Err` value")

    def unwrap_err(self: Result[T, E]) -> E:
        """Returns the contained [`Err`] value, consuming the `self` value.

        Examples:
            >>> x: Result[int, str] = ok(2)
            >>> assert x.unwrap_err()  # raises UnwrapError

            >>> x: Result[int, str] = err("Nothing here")
            >>> assert x.unwrap_err() == "Nothing here"

        Raises:
            UnwrapError: If the value is an [`Ok(T)`].
        """
        if self.is_ok():
            if isinstance(self.__value, Exception):
                raise UnwrapError("called `Result.unwrap_err` on an `Ok` value") from self.__value

            raise UnwrapError("called `Result.unwrap_err` on an `Ok` value")

        return self.__value

    def unwrap_or(self: Result[T, E], default: T) -> T:
        """Returns the contained [`Ok(T)`] value or a provided default.

        Arguments passed to `unwrap_or` are eagerly evaluated; if you are passing the result of a function call,
        it is recommended to use [`unwrap_or_else`], which is lazily evaluated.

        [`unwrap_or_else`]: Result.unwrap_or_else

        Examples:
            >>> x = ok(2)
            >>> assert x.unwrap_or(3) == 2

            >>> x = err("Nothing here")
            >>> assert x.unwrap_or(3) == 3
        """
        if self.is_ok():
            return self.__value

        return default

    def unwrap_or_else(self: Result[T, E], func: Callable[[E], T]) -> T:
        """Returns the contained [`Ok(T)`] value or computes it from a closure.

        Examples:
            >>> assert ok(2).unwrap_or_else(len) == 2
            >>> assert err("foo").unwrap_or_else(len) == 3
        """
        if self.is_ok():
            return self.__value

        return func(self.__value)

    ###########################################################################
    # Boolean operations on the values, eager and lazy
    ###########################################################################

    def and_(self: Result[T, E], rhs: Result[U, E]) -> Result[U, E]:
        """Returns `res` if the result is [`Ok(T)`] otherwise returns the [`Err(E)`] value of `self`.

        Arguments passed to `and_` are eagerly evaluated; if you are passing the result of a function call,
        it is recommended to use [`and_then`], which is lazily evaluated.

        [`and_then`]: Result.and_then

        Examples:
            >>> x = ok(2)
            >>> assert x.and_(ok(3)) == ok(3)
            >>> assert x.and_(err("Nothing here")) == err("Nothing here")

            >>> x = err("Nothing here")
            >>> assert x.and_(ok(3)) == err("Nothing here")
            >>> assert x.and_(err("Nothing here")) == err("Nothing here")
        """
        if self.is_ok():
            return rhs

        return err(self.__value)

    def __and__(self: Result[T, E], rhs: Result[T, E]):
        return self.and_(rhs)

    def and_then(self: Result[T, E], func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Calls func if the result is [`Ok(T)`] otherwise returns the [`Err(E)`] value of self.

        This function can be used for control flow based on [`Result`] values.

        Examples:
            >>> def sq(x: int) -> Result[int, str]:
            ...     return ok(x * x)

            >>> def err_(x: int) -> Result[int, str]:
            ...     return err("Nothing here")

            >>> assert ok(2).and_then(sq).and_then(sq) == ok(16)
            >>> assert ok(2).and_then(sq).and_then(err_) == err("Nothing here")
            >>> assert ok(2).and_then(err_).and_then(sq) == err("Nothing here")
            >>> assert err("Nothing here").and_then(sq).and_then(sq) == err("Nothing here")
        """
        if self.is_ok():
            return func(self.__value)

        return err(self.__value)

    def filter(self: Result[T, E], predicate: Callable[[T], bool]) -> Result[T, E]:
        """Returns `self` if the result is [`Ok(T)`] and
        `predicate` returns `True` when applied to the [`Ok(T)`']s value, otherwise returns the
        [`Err(E)`] value of `self`.

        Arguments passed to `filter` are eagerly evaluated; if you are passing the result of a function call,
        it is recommended to use [`filter_map`], which is lazily evaluated.

        [`filter_map`]: Result.filter_map

        Examples:
            >>> def is_even(x: int) -> bool:
            ...     return x % 2 == 0

            >>> assert ok(2).filter(is_even) == ok(2)
            >>> assert ok(3).filter(is_even) == err(3)
            >>> assert err(3).filter(is_even) == err(3)
        """
        if self.is_ok():
            if predicate(self.__value):
                return ok(self.__value)

            return err(self.__value)

        return err(self.__value)

    def or_(self: Result[T, E], rhs: Result[T, V]) -> Result[T, V]:
        """Returns `res` if the result is [`Err(E)`] otherwise returns the [`Ok(T)`] value of `self`.

        Arguments passed to `or_` are eagerly evaluated; if you are passing the result of a function call,
        it is recommended to use [`or_else`], which is lazily evaluated.

        [`or_else`]: Result.or_else

        Examples:
            >>> x = ok(2)
            >>> assert x.or_(ok(3)) == x
            >>> assert x.or_(err("Nothing here")) == x

            >>> x = err("Nothing here")
            >>> assert x.or_(ok(3)) == ok(3)
            >>> assert x.or_(err("Nothing here")) == err("Nothing here")
        """
        if self.is_ok():
            return self

        return rhs

    def __or__(self: Result[T, E], rhs: Result[T, E]) -> Result[T, V]:
        return self.or_(rhs)

    def or_else(self: Result[T, E], func: Callable[[E], Result[T, V]]) -> Result[T, V]:
        """Calls func if the result is [`Err(E)`] otherwise returns the [`Ok(T)`] value of self.

        This function can be used for control flow based on [`Result`] values.

        Examples:
            >>> def sq(x: int) -> Result[int, int]:
            ...     return ok(x * x)

            >>> def err_(x: int) -> Result[int, int]:
            ...     return err(-1)

            >>> assert ok(2).or_else(err_).or_else(err_) == ok(2)
            >>> assert ok(2).or_else(sq).or_else(err) == ok(2)
            >>> assert ok(2).or_else(err_).or_else(sq) == ok(2)
            >>> assert err(-1).or_else(sq).or_else(err_) == ok(4)
        """
        if self.is_ok():
            return ok(self.__value)

        return func(self.__value)

    ###########################################################################
    # Comparison operators
    ###########################################################################

    def __eq__(self: Result[T, E], rhs: Result[T, E]) -> bool:
        if isinstance(rhs, Result):
            # rhs is a Result
            if (self.is_err() and rhs.is_err()) or (self.is_ok() and rhs.is_ok()):
                # both are err or both are ok
                return self.__value == rhs.__value
            elif (self.is_ok() and rhs.is_err()) or (self.is_err() and rhs.is_ok()):
                # either is error
                return False

        raise TypeError(f"Cannot compare Result with {rhs.__class__.__name__}")

    def __ne__(self: Result[T, E], rhs: Result[T, E]) -> bool:
        return not self.__eq__(rhs)

    # def __lt__(self: Result[T, E], rhs: Result[T, E]) -> bool:
    #     if isinstance(rhs, Result):
    #         # rhs is a Result
    #         if (self.is_err() and rhs.is_err()) or (self.is_ok() and rhs.is_ok()):
    #             # both are err or both are ok
    #             return self.__value < rhs.__value
    #         elif (self.is_ok() and rhs.is_err()) or (self.is_err() and rhs.is_ok()):
    #             # either is error
    #             return False
    #
    #     raise TypeError(f"Cannot compare Result with {rhs.__class__.__name__}")
    #
    # def __le__(self: Result[T, E], rhs: Result[T, E]) -> bool:
    #     if isinstance(rhs, Result):
    #         # rhs is a Result
    #         if (self.is_err() and rhs.is_err()) or (self.is_ok() and rhs.is_ok()):
    #             # both are err or both are ok
    #             return self.__value <= rhs.__value
    #         elif (self.is_ok() and rhs.is_err()) or (self.is_err() and rhs.is_ok()):
    #             # either is error
    #             return False
    #
    #     raise TypeError(f"Cannot compare Result with {rhs.__class__.__name__}")
    #
    # def __gt__(self: Result[T, E], rhs: Result[T, E]) -> bool:
    #     if isinstance(rhs, Result):
    #         # rhs is a Result
    #         if (self.is_err() and rhs.is_err()) or (self.is_ok() and rhs.is_ok()):
    #             # both are err or both are ok
    #             return self.__value > rhs.__value
    #         elif (self.is_ok() and rhs.is_err()) or (self.is_err() and rhs.is_ok()):
    #             # either is error
    #             return False
    #
    #     raise TypeError(f"Cannot compare Result with {rhs.__class__.__name__}")
    #
    # def __ge__(self: Result[T, E], rhs: Result[T, E]) -> bool:
    #     if isinstance(rhs, Result):
    #         # rhs is a Result
    #         if (self.is_err() and rhs.is_err()) or (self.is_ok() and rhs.is_ok()):
    #             # both are err or both are ok
    #             return self.__value >= rhs.__value
    #         elif (self.is_ok() and rhs.is_err()) or (self.is_err() and rhs.is_ok()):
    #             # either is error
    #             return False
    #
    #     raise TypeError(f"Cannot compare Result with {rhs.__class__.__name__}")

    ###########################################################################
    # Miscellaneous
    ###########################################################################

    def contains(self: Result[T, E], x: T) -> bool:
        """Returns `True` if the result is [`Ok(T)`] and
        the value is equal to `x`, otherwise returns `False`.

        Examples:
            >>> assert ok(2).contains(2)
            >>> assert not ok(2).contains(3)
            >>> assert not err("Nothing here").contains(2)
        """
        return self.is_ok() and self.__value == x

    def contains_err(self: Result[T, E], x: E) -> bool:
        """Returns `True` if the result is [`Err(E)`] and
        the value is equal to `x`, otherwise returns `False`.

        Examples:
            >>> assert err("Nothing here").contains_err("Nothing here")
            >>> assert not err("Nothing here").contains_err("Nothing")
            >>> assert not ok(2).contains_err("Nothing here")
        """
        return self.is_err() and self.__value == x

    def transpose(self: Result[Option[T], E]) -> Option[Result[T, E]]:
        """Transposes a `Result[Option(T), E]` into an `Option[Result[T, E]]`.

        Examples:
            >>> assert ok(some(2)).transpose() == some(ok(2))
            >>> assert ok(none()).transpose() == none()
        """
        from .option import Option, some, none
        self.__value: Option[T]

        # Ok(Some(x)) => Some(Ok(x))
        if self.is_ok_and(lambda val: isinstance(val, Option) and val.is_some()):
            # Safety: it's safe to unwrap because we checked that the value is some above
            return some(ok(self.__value.unwrap()))

        # Ok(None) => None
        if self.is_ok_and(lambda val: isinstance(val, Option) and val.is_none()):
            return none()

        if self.is_err_and(lambda val: isinstance(val, Option)):
            if self.__value.is_some():
                # Err(Some(x)) => Some(Err(x))
                return some(err(self.__value.unwrap()))

            # Err(None) => None
            return none()

        raise TypeError("Result must contain an Option when using transpose")


    def flatten(self: Result[Result[T, E], E]) -> Result[T, E]:
        """Flattens a nested `Result` into a single `Result`.

        Examples:
            >>> assert ok(ok(2)).flatten() == ok(2)
            >>> assert ok(err("Nothing here")).flatten() == err("Nothing here")
            >>> assert err("Nothing here").flatten() == err("Nothing here")
        """
        if self.is_ok():
            return self.__value

        return self

    ###########################################################################
    # Pythonic implementation
    ###########################################################################

    @classmethod
    @functools.cache
    def __class_getitem__(cls: Option[T], ok_: T, err_: E) -> Option[T]:
        if (isinstance(ok_, type) and isinstance(err_, type)) or (isinstance(ok_, ...) ^ isinstance(err_, ...)):
            return cls

        raise TypeError("Result can only be used as a generic type")

    def __contains__(self: Result[T, E], item: T | E) -> bool:
        return self.contains(item) or self.contains_err(item)

    def __repr__(self: Result[T, E]) -> str:
        return f"<Ok({self.__value})>" if self.is_ok() else f"<Err({self.__value})>"

    def __bool__(self: Result[T, E]) -> bool:
        return self.is_ok()


def ok(value: T) -> Result[T, E]:
    """Creates a new [`Ok(T)`] value.

    Examples:
        >>> assert ok(2) == ok(2)
        >>> assert ok(2) != ok(3)
        >>> assert ok(2) != err("Nothing here")
    """
    return Result(True, value, _force=True)


def err(value: E) -> Result[T, E]:
    """Creates a new [`Err(E)`] value.

    Examples:
        >>> assert err("Nothing here") == err("Nothing here")
        >>> assert err("Nothing here") != err("Nothing")
        >>> assert err("Nothing here") != ok(2)
    """
    return Result(False, value, _force=True)
