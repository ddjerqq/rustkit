"""
# Optional values.

Type [`Option`] represents an optional value: every [`Option`]
is either [`Some`] and contains a value, or [`None`], and
does not. [`Option`] types are very common in R̶u̶s̶t̶ Python code, as
they have a number of uses:

* Initial values
* Return values for functions that are not defined
  over their entire input range (partial functions)
* Return value for otherwise reporting simple errors, where [`None`] is
  returned on error
* Optional class attributes
* Optional function arguments

[`Option`]s are commonly paired with pattern matching to query the presence
of a value and take action, always accounting for the [`None`] case.

### Examples:
    >>> def divide(numerator: float, denominator: float) -> Option[float]:
    ...     if denominator == 0.0:
    ...         return none()
    ...     else:
    ...         return some(numerator / denominator)

    >>> # The return value of the function is an option
    >>> result = divide(2.0, 3.0)

    >>> # cant really pattern match in (older versions of) Python to retrieve the value,
    >>> # but you can use [`Option.is_some`]

    >>> if result.is_some():
    >>>     print(f"Result: {result.unwrap()}")
    >>> else:
    >>>     print("Cannot divide by 0")

    >>> User = type("User", (), {"id": 0})
    >>> def get_user(id: int) -> Option[User]:
    ...     db = ...
    ...     maybe_user = db.get_user(id)
    ...     return Option.from_(maybe_user)


## Method overview:
In addition to working with pattern matching, [`Option`] provides a wide variety of different methods.

### Querying the variant:
The [`is_some`] and [`is_none`] methods return [`True`] if the [`Option`] is [`Some`] or [`None`], respectively.

### Extracting the contained value:
These methods extract the contained value in an [`Option[T]`] when it is the [`Some`] variant.
If the [`Option`] is [`None`]:

* [`expect`] raises UnwrapError with a provided custom message
* [`unwrap`] raises UnwrapError with a generic message
* [`unwrap_or`] returns the provided default value
* [`unwrap_or_else`] returns the result of evaluating the provided function

### Transforming contained values:
These methods transform [`Option`] to [`Result`]:

* [`ok_or`] transforms [`Some(v)`] to [`Ok(v)`], and [`None`] to [`Err(err)`] using the provided default `err` value
* [`ok_or_else`] transforms [`Some(v)`] to [`Ok(v)`], and [`None`] to a value of [`Err`] using the provided function
* [`transpose`] transposes an [`Option`] of a [`Result`] into a [`Result`] of an [`Option`]

#### These methods transform the [`Some`] variant:

* [`filter`] calls the provided predicate function on the contained value `t` if the [`Option`] is [`Some(t)`],
  and returns [`Some(t)`] if the function returns `true`;
  otherwise, returns [`None`]
* [`flatten`] removes one level of nesting from an [`Option[Option[T]]`]
* [`map`] transforms [`Option[T]`] to [`Option[U]`] by applying the provided function to the
  contained value of [`Some`] and
  leaving [`None`] values unchanged

#### These methods transform [`Option[T]`] to a value of a possibly different type `U`:

* [`map_or`] applies the provided function to the contained value of [`Some`], or returns the
  provided default value if the [`Option`] is [`None`]
* [`map_or_else`] applies the provided function to the contained value of [`Some`], or
  returns the result of evaluating the provided fallback function if the [`Option`] is [`None`]

#### These methods combine the [`Some`] variants of two [`Option`] values:

* [`zip`] returns [`Some((T, U))`] if `self` is [`Some(T)`] and the
  provided [`Option`] value is [`Some(U)`]; otherwise, returns [`None`]

* [`zip_with`] calls the provided function `f` and returns
  [`Some(func(T, U))`] if `self` is [`Some(T)`] and the provided
  [`Option`] value is [`Some(U)`]; otherwise, returns [`None`]

### Boolean operators:

These methods treat the [`Option`] as a boolean value, where [`Some`]
acts like [`true`] and [`None`] acts like [`false`]. There are two
categories of these methods: ones that take an [`Option`] as input, and
ones that take a function as input (to be lazily evaluated).

The [`and_`], [`or_`], and [`xor`] methods take another [`Option`] as
input, and produce an [`Option`] as output. Only the [`and_`] method can
produce an [`Option[U]`] value having a different inner type `U` than
[`Option[T]`].

```md
| method  | self      | input     | output    |
|---------|-----------|-----------|-----------|
| [`and`] | `None`    | (ignored) | `None`    |
| [`and`] | `Some(x)` | `None`    | `None`    |
| [`and`] | `Some(x)` | `Some(y)` | `Some(y)` |
| [`or`]  | `None`    | `None`    | `None`    |
| [`or`]  | `None`    | `Some(y)` | `Some(y)` |
| [`or`]  | `Some(x)` | (ignored) | `Some(x)` |
| [`xor`] | `None`    | `None`    | `None`    |
| [`xor`] | `None`    | `Some(y)` | `Some(y)` |
| [`xor`] | `Some(x)` | `None`    | `Some(x)` |
| [`xor`] | `Some(x)` | `Some(y)` | `None`    |
```

The [`and_then`] and [`or_else`] methods take a function as input, and
only evaluate the function when they need to produce a new value. Only
the [`and_then`] method can produce an [`Option[U]`] value having a
different inner type `U` than [`Option[T]`].

```md
| method       | self      | function input | function result | output    |
|--------------|-----------|----------------|-----------------|-----------|
| [`and_then`] | `None`    | (not provided) | (not evaluated) | `None`    |
| [`and_then`] | `Some(x)` | `x`            | `None`          | `None`    |
| [`and_then`] | `Some(x)` | `x`            | `Some(y)`       | `Some(y)` |
| [`or_else`]  | `None`    | (not provided) | `None`          | `None`    |
| [`or_else`]  | `None`    | (not provided) | `Some(y)`       | `Some(y)` |
| [`or_else`]  | `Some(x)` | (not provided) | (not evaluated) | `Some(x)` |
```

This is an example of using methods like [`and_then`] and [`or_`] in a
pipeline of method calls. Early stages of the pipeline pass failure
values ([`None`]) through unchanged, and continue processing on
success values ([`Some`]). Toward the end, [`or_`] substitutes an error
message if it receives [`None`].

### Comparison operators:

If `T` implements [`__eq__`] then [`Option[T]`] will derive its
[`__eq__`] implementation. With this order, [`None`] compares as
less than any [`Some`], and two [`Some`] compare the same way as their
contained values would in `T`.

>>> assert none()  <  some(0)
>>> assert some(1) <= some(1)
>>> assert some(2) >  some(1)
>>> assert some(2) >= some(1)
>>> assert some(1) == some(1)
>>> assert some(1) != some(2)


### Modifying an [`Option`] in-place:

These methods return the contained value of an [`Option[T]`]:

* [`insert`] inserts a value, dropping any old contents
* [`get_or_insert`] gets the current value, inserting a provided default value if it is [`None`]
* [`get_or_insert_with`] gets the current value, inserting a default computed by the provided function if it is [`None`]

### These methods transfer ownership of the contained value of an [`Option`]:

* [`take`] takes ownership of the contained value of an [`Option`], if
  any, replacing the [`Option`] with [`None`]
* [`replace`] takes ownership of the contained value of an [`Option`],
  if any, replacing the [`Option`] with a [`Some`] containing the
  provided value
"""

from __future__ import annotations

import functools
from types import NoneType
from typing import (
    Callable,
    Generic,
    TYPE_CHECKING,
    Tuple,
    TypeVar,
    Optional,
    Protocol,
)

from .error import UnwrapError

if TYPE_CHECKING:
    from .result import Result, ok, err


class SupportsRichComparison(Protocol):
    def __eq__(self, other: object) -> bool:
        ...

    def __ne__(self, other: object) -> bool:
        ...

    def __lt__(self, other: object) -> bool:
        ...

    def __le__(self, other: object) -> bool:
        ...

    def __gt__(self, other: object) -> bool:
        ...

    def __ge__(self, other: object) -> bool:
        ...


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
E = TypeVar("E")
R = TypeVar("R", bound="Result")
C = TypeVar("C", bound=SupportsRichComparison)


__all__ = (
    "Option",
    "some",
    "none",
)


class Option(Generic[T]):
    """Optional values. aka, explicit nullable types.

    use [`Option.none`] to create a [`None`] value, and [`Option.some`] to
    create a [`Some`] value. alternatively use the module level function [`some`]
    and the constant variable [`none()`] to create a [`Option`].

    Type [`Option`] represents an optional value: every [`Option`]
    is either [`Some`] and contains a value, or [`None`], and
    does not. [`Option`] types are very common in ~Rust~ Python code, as
    they have a number of uses:

    * Initial values
    * Return values for functions that are not defined over their entire input range (partial functions)
    * Return value for otherwise reporting simple errors, where :class:`None` is returned on error
    * Optional struct fields
    * Struct fields that can be loaned or "taken"
    * Optional function arguments
    * Nullable variables
    * Swapping things out of difficult situations
    """
    __value: T | None
    __slots__ = ("__value",)

    ###########################################################################
    # Creating the option type
    ###########################################################################

    def __init__(self, value: Optional[T] = None, *, _force: bool = False) -> None:
        """Try not to directly initialize the option type. There are better ways.

        such as: the module level functions [`none`] and [`some`],
        or the class methods [`Option.none`] and [`Option.some`]
        """
        if not _force:
            raise RuntimeError(
                "you may not create the option type directly. \n"
                "instead use one of the provided factory methods"
            )

        self.__value = value
        """T: value of the Option object"""

    @classmethod
    def from_(cls, value: T | NoneType) -> Option[T]:
        """create an [`Option`] from a value that may be [`None`]

        >>> from random import random
        >>> f = lambda: None if random() < 0.1 else 1

        >>> assert Option[int].from_(f()) == Option.none()
        >>> assert Option[int].from_(f()) == Option.some(1)
        """
        return cls(value, _force=True)

    @classmethod
    def some(cls, value: T) -> Option[T]:
        """create an [`Option`] from a value that you know for sure that is not [`None`]
        if you're not sure about the value being some, use [`Option.from_`]

        Examples:
            >>> assert Option.some(1) == Option.from_(1)
        """
        return cls(value, _force=True)

    @classmethod
    def none(cls) -> Option[T]:
        """create an [`Option`] which is None.

        Examples:
            >>> assert Option.none().is_none()
        """
        return cls(None, _force=True)

    ###########################################################################
    # Querying the contained values
    ###########################################################################

    def is_some(self) -> bool:
        """Returns `True` if the option has [`Some`] value.

        Examples:
            >>> x: Option[int] = some(2)
            >>> assert x.is_some() == True

            >>> x: Option[int] = none()
            >>> assert x.is_some() == False
        """
        return self.__value is not None

    def is_some_and(self: Option[T], func: Callable[[T], bool]) -> bool:
        """Check if the option is has `Some` value and that value satisfies the given predicate.

        Examples:
            >>> x: Option[int] = some(2)
            >>> assert x.is_some_and(lambda val: val > 1) == True

            >>> x: Option[int] = some(0)
            >>> assert x.is_some_and(lambda val: val > 1) == False

            >>> x: Option[int] = none()
            >>> assert x.is_some_and(lambda val: val > 1) == False
        """
        return func(self.__value) if self.is_some() else False

    def is_none(self) -> bool:
        """Returns `True` if the option has [`None`] value.

        Examples:
            >>> x: Option[int] = some(2)
            >>> assert x.is_none() == False

            >>> x: Option[int] = none()
            >>> assert x.is_none() == True
        """
        return not self.is_some()

    ###########################################################################
    # Getting to contained values
    ###########################################################################

    def expect(self: Option[T], msg: str) -> T:
        """Returns the contained value, consuming the `self` value.

        Raises:
            UnwrapError: if the value is [`None`] with a custom panic message provided by `msg`.

        Examples:
            >>> x = some("value")
            >>> assert x.expect("fruits are healthy") == "value"

            >>> # should raise UnwrapError
            >>> x: Option[str] = none()
            >>> x.expect("msg")  # raises UnwrapError with message: `msg`

            >>> # Recommended Message Style
            >>> # I recommend that `expect` messages describe the reason you expect the `Option` to be `Some`.
            >>> # Also try avoiding full stops in exception stack traces.

            >>> # should raise UnwrapError
            >>> id_ = Option.from_({"id": 10}.get("id"))
            >>> item = id_.expect("dict should contain key `id`")
        """
        if self.is_none():
            raise UnwrapError(msg)

        return self.__value

    def unwrap(self: Option[T]) -> T:
        """Returns the contained [`Some`] value, consuming the `self` value.

        Because this function may raise an UnwrapError, its use is generally discouraged.
        Instead, prefer to use pattern matching and handle the [`None`]
        case explicitly, or call [`unwrap_or`], [`unwrap_or_else`].

        Raises:
            Exception if the self value equals [`None`].

        Examples:
            >>> x = some("air")
            >>> assert x.unwrap() == "air"

            >>> # should raise UnwrapError
            >>> x: Option[str] = none()
            >>> assert x.unwrap() == "air"  # raises UnwrapError
        """
        if self.is_none():
            raise UnwrapError("called `Option.unwrap()` on a `None` value")

        return self.__value

    def unwrap_or(self: Option[T], default: T) -> T:
        """Returns the contained [`Some`] value or a provided default.

        Arguments passed to `unwrap_or` are eagerly evaluated; if you are passing
        the result of a function call, it is recommended to use [`unwrap_or_else`], which is lazily evaluated.

        Examples:
            >>> assert some("car").unwrap_or("bike") == "car"
            >>> assert none().unwrap_or("bike") == "bike"
        """
        if self.is_none():
            return default

        return self.__value

    def unwrap_or_else(self: Option[T], func: Callable[[], T]) -> T:
        """Returns the contained [`Some`] value or computes it from a function.

        Examples:
            >>> assert some(4).unwrap_or_else(int) == 4
            >>> assert none().unwrap_or_else(int) == 0
        """
        if self.is_none():
            return func()

        return self.__value

    ###########################################################################
    # Transforming contained values
    ###########################################################################

    def map(self: Option[T], func: Callable[[T], U]) -> Option[U]:
        """Maps an `Option[T]` to `Option[U]` by applying a function to a contained value.

         Examples:
             >>> maybe_string = some("Hello, World!")
             >>> maybe_len = maybe_string.map(len)
             >>> assert maybe_len == Option(13)
        """
        if self.is_none():
            return self

        return Option.some(func(self.__value))

    def inspect(self: Option[T], func: Callable[[T], None]) -> Option[T]:
        """Calls the provided closure with a reference to the contained value (if [`Some`]).

        Examples:
            >>> id_ = Option.from_({"id": 10}.get("id"))

            >>> x: Option[int] = id_.inspect(lambda val: print(f"got: {val}"))
            ... got: 4

            >>> x: Option[int] = id_.inspect(lambda val: print(f"got: {val}"))
            ... # does not print anything
        """
        if self.is_some():
            func(self.__value)
        return self

    def map_or(self: Option[T], default: U, func: Callable[[T], U]) -> U:
        """Returns the provided default result (if none), or applies a function to the contained value (if any).

        Arguments passed to `map_or` are eagerly evaluated; if you are passing
        the result of a function call, it is recommended to use [`map_or_else`],
        which is lazily evaluated.

        Examples:
            >>> x = some("foo")
            >>> assert x.map_or(-1, lambda v: len(v)) == 3
            # that or directly use the function, for a more pythonic way
            >>> assert x.map_or(-1, len) == 3
            >>>
            >>> x: Option[str] = none()
            >>> assert x.map_or(-1, len) == -1
        """
        if self.is_none():
            return default

        return func(self.__value)

    def map_or_else(self: Option[T], default: Callable[[], U], func: Callable[[T], U]) -> U:
        """Computes a default function result (if none), or
        applies a different function to the contained value (if any).

        Examples:
            >>> k = 21

            >>> x = some("foo")
            >>> assert x.map_or_else(int, len) == 3

            >>> x: Option[str] = none()
            >>> assert x.map_or_else(int, len) == 0  # default for calling int()
        """
        if self.is_none():
            return default()

        return func(self.__value)

    def ok_or(self: Option[T], error: E) -> Result[T, E]:
        """Transforms the `Option[T]` into a [`Result[T, E]`],
        mapping [`Some(v)`] to [`Ok(v)`] and [`None`] to [`Err(error)`].

        Arguments passed to `ok_or` are eagerly evaluated; if you are passing the
        result of a function call, it is recommended to use [`ok_or_else`], which is
        lazily evaluated.

        Examples:
            >>> x: Option[str] = some("foo")
            >>> assert x.ok_or(0) == ok("foo")

            >>> x: Option[str] = none()
            >>> assert x.ok_or(0) == err(0)
        """
        from .result import ok, err as _err

        if self.is_none():
            return _err(error)

        return ok(self.__value)

    def ok_or_else(self: Option[T], func: Callable[[], E]) -> Result[T, E]:
        """Transforms the `Option[T]` into a [`Result[T, E]`], mapping [`Some(T)`] to [`Ok(T)`]
        and [`None`] to [`Err(func())`].

        use the `func` to create the Err variant.

        Examples:
            >>> x = some("foo")
            >>> assert x.ok_or_else(int) == ok("foo")

            >>> x: Option[str] = none()
            >>> assert x.ok_or_else(int) == err(0)
        """
        from .result import ok, err

        if self.is_none():
            return err(func())

        return ok(self.__value)

    ###########################################################################
    # Boolean operations on the values, eager and lazy
    ###########################################################################

    def and_(self: Option[T], rhs: Option[U]) -> Option[T] | Option[U]:
        """Returns [`None`] if the option is [`None`], otherwise returns `rhs`.

        Arguments passed to `and_` are eagerly evaluated; if you are passing the
        result of a function call, it is recommended to use [`and_then`], which is
        lazily evaluated.

        Examples:
            >>> x = some(2)
            >>> y = none()
            >>> assert x.and_(y) == none()

            >>> x = none()
            >>> y = some("foo")
            >>> assert x.and_(y) == none()

            >>> x = some(2)
            >>> y = some("foo")
            >>> assert x.and_(y) == some("foo")

            >>> x = none()
            >>> y = none()
            >>> assert x.and_(y) == Option()
        """
        if self.is_none():
            return self

        return rhs

    def __and__(self: Option[T], rhs: Option[U]) -> Option[T] | Option[U]:
        return self.and_(rhs)

    def and_then(self: Option[T], func: Callable[[T], Option[U]]) -> Option[U]:
        """Returns [`None`] if the option is [`None`], otherwise calls `func`
        with the wrapped value and returns the result.
        Some languages call this operation flatmap.

        Examples:
            >>> # Often used to chain fallible operations that may return [`None`].

            >>> i = Option.from_(10).and_then(lambda ten: Option.from_(ten / 2))
            >>> assert i == Option(5.0)
        """
        if self.is_none():
            return self

        return func(self.__value)

    def filter(self: Option[T], func: Callable[[T], bool]) -> Option[T]:
        """Returns [`None`] if the option is [`None`], otherwise calls `func`
        with the wrapped value and returns:

        * [`Some(T)`] if `func` returns `true` (where `T` is the wrapped value), and

        * [`None`] if `func` returns `false`.

        This function works similar to [`Iterator.filter()`]. You can imagine
        the `Option[T]` being an iterator over one or zero elements. `filter()`
        lets you decide which elements to keep.

        Examples:
            >>> def is_even(n: int) -> bool:
            ...     '''this is a joke, don't cancel me'''
            ...     if n == 0:
            ...         return True
            ...     elif n == 1:
            ...         return False
            ...     elif n == 2:
            ...         return True
            ...     elif n == 3:
            ...         return False
            ...     elif n == 4:
            ...         return True
            ...     elif n == 5:
            ...         return False
            ...     elif n == 6:
            ...         return True
            ...     ...

            >>> assert none().filter(is_even) == none()
            >>> assert some(3).filter(is_even) == none()
            >>> assert some(4).filter(is_even) == some(4)
        """
        if self.is_some() and func(self.__value):
            return self

        return none()

    def or_(self: Option[T], rhs: Option[U]) -> Option[T] | Option[U]:
        """Returns the option if it contains a value, otherwise returns `rhs`.

        Arguments passed to `or` are eagerly evaluated; if you are passing the
        result of a function call, it is recommended to use [`or_else`], which is lazily evaluated.

        Examples:
            >>> x = some(2)
            >>> y = none()
            >>> assert x.or_(y) == some(2)

            >>> x = none()
            >>> y = some(100)
            >>> assert x.or_(y) == some(100)

            >>> x = some(2)
            >>> y = some(100)
            >>> assert x.or_(y) == some(2)

            >>> x = none()
            >>> y = none()
            >>> assert x.or_(y) == none()
        """
        if self.is_none():
            return rhs

        return self

    def __or__(self: Option[T], rhs: Option[U]) -> Option[T] | Option[U]:
        return self.or_(rhs)

    def or_else(self: Option[T], func: Callable[[], Option[T]]) -> Option[T]:
        """Returns the option if it contains a value, otherwise calls `func` and
        returns the result.

        Examples:
            >>> nobody = Option.none
            >>> vikings = lambda: some("vikings")

            >>> assert some("barbarians").or_else(vikings) == some("barbarians")
            >>> assert none().or_else(vikings) == some("vikings")
            >>> assert none().or_else(nobody) == none()
        """
        if self.is_none():
            return func()

        return self

    def xor(self: Option[T], rhs: Option[T]) -> Option[T]:
        """Returns [`Some`] if exactly one of `self`, `rhs` is [`Some`], otherwise returns [`None`].

        # T and U are some values, N are Nones

        N | N == N

        N | U == U

        T | N == T

        T | U == N

        Examples:
            >>> x = some(2)
            >>> y = none()
            >>> assert x.xor(y) == some(2)

            >>> x = none()
            >>> y = some(2)
            >>> assert x.xor(y) == some(2)

            >>> x = some(2)
            >>> y = some(2)
            >>> assert x.xor(y) == none()

            >>> x = none()
            >>> y = none()
            >>> assert x.xor(y) == none()
        """

        if self.is_none():
            if rhs.is_none():
                return none()

            return rhs

        if rhs.is_none():
            return self

        return none()

    def __xor__(self: Option[T], rhs: Option[T]) -> Option[T]:
        return self.xor(rhs)

    ###########################################################################
    # Comparison operators
    ###########################################################################

    def __eq__(self: Option[T], rhs: Option[T] | NoneType) -> bool:
        if isinstance(rhs, Option):
            # rhs is an option
            if self.is_none() and rhs.is_none():
                # both are none
                return True
            elif (self.is_some() and rhs.is_none()) or (self.is_none() and rhs.is_some()):
                # either is none
                return False
            else:
                # both are some
                # compare values
                return self.__value == rhs.__value

        if rhs is None:
            return self.is_none()

        raise TypeError(f"Cannot compare Option with {rhs.__class__.__name__}")

    def __ne__(self: Option[T], rhs: Option[T] | NoneType) -> bool:
        return not self.__eq__(rhs)

    # def __lt__(self: Option[C], rhs: Option[C] | NoneType) -> bool:
    #     if isinstance(rhs, Option):
    #         # rhs is an option
    #         if self.is_none() and rhs.is_none():
    #             # N < N
    #             return False
    #         elif self.is_none() and rhs.is_some():
    #             # N < S
    #             return True
    #         elif self.is_some() and rhs.is_none():
    #             # S !< N
    #             return False
    #         else:
    #             # both are some
    #             # compare values
    #             return self.__value < rhs.__value
    #
    #     if rhs is None:
    #         return False
    #
    #     raise TypeError(f"Cannot compare Option with {rhs.__class__.__name__}")
    #
    # def __le__(self: Option[C], rhs: Option[C] | NoneType) -> bool:
    #     if isinstance(rhs, Option):
    #         # rhs is an option
    #         if self.is_none() and rhs.is_none():
    #             # N <= N
    #             return True
    #         elif self.is_none() and rhs.is_some():
    #             # N <= S
    #             return True
    #         elif self.is_some() and rhs.is_none():
    #             # S !<= N
    #             return False
    #         else:
    #             # both are some
    #             # compare values
    #             return self.__value <= rhs.__value
    #
    #     if rhs is None:
    #         return self.is_none()
    #
    #     raise TypeError(f"Cannot compare Option with {rhs.__class__.__name__}")
    #
    # def __gt__(self: Option[C], rhs: Option[C] | NoneType) -> bool:
    #     if isinstance(rhs, Option):
    #         # rhs is an option
    #         if self.is_none() and rhs.is_none():
    #             # N > N
    #             return False
    #         elif self.is_none() and rhs.is_some():
    #             # N > S
    #             return False
    #         elif self.is_some() and rhs.is_none():
    #             # S > N
    #             return True
    #         else:
    #             # both are some
    #             # compare values
    #             return self.__value > rhs.__value
    #
    #     if rhs is None:
    #         # S > N
    #         return self.is_some()
    #
    #     raise TypeError(f"Cannot compare Option with {rhs.__class__.__name__}")
    #
    # def __ge__(self: Option[C], rhs: Option[C] | NoneType) -> bool:
    #     if isinstance(rhs, Option):
    #         # rhs is an option
    #         if self.is_none() and rhs.is_none():
    #             # N >= N
    #             return True
    #         elif self.is_none() and rhs.is_some():
    #             # N >= S
    #             return False
    #         elif self.is_some() and rhs.is_none():
    #             # S >= N
    #             return True
    #         else:
    #             # both are some
    #             # compare values
    #             return self.__value >= rhs.__value
    #
    #     if rhs is None:
    #         return True
    #
    #     raise TypeError(f"Cannot compare Option with {rhs.__class__.__name__}")

    ###########################################################################
    # Entry-like operations to insert a value and return a reference
    ###########################################################################

    def insert(self: Option[T], value: T) -> T:
        """Inserts `value` into the option, then returns it.
        If the option already contains a value, the old value is overwritten.

        See also [`Option.get_or_insert`], which doesn't update the value if
        the option already contains [`Some`].

        Example
            >>> a = none()
            >>> val = a.insert(1)
            >>> assert val == 1
            >>> assert a.unwrap() == 1

            >>> val = a.insert(2)
            >>> assert val == 2
        """
        self.__value = value

        # Safety: we just set the value up top, so self.__value can never be None.
        return self.__value

    def get_or_insert(self: Option[T], value: T) -> T:
        """Inserts `value` into the option if it is [`None`], then returns the contained value.
        See also [`Option.insert`], which updates the value even if the option already contains [`Some`].

        Examples:
            >>> assert none().get_or_insert(5) == 5

            >>> assert some(10).get_or_insert(5) == 10
        """
        if self.is_none():
            self.__value = value

        return self.__value

    def get_or_insert_with(self: Option[T], func: Callable[[], T]) -> T:
        """Inserts a value computed from `func` into the option if it is [`None`],
        then returns the contained value.

        Examples:
            >>> y = none().get_or_insert_with(int)
            >>> assert y == 0
        """
        if self.is_none():
            self.__value = func()

        return self.__value

    ###########################################################################
    # Miscellaneous
    ###########################################################################

    def take(self: Option[T]) -> Option[T]:
        """Takes the value out of the option, leaving a [`None`] in its place.

        Examples:
            >>> x = some(2)
            >>> y = x.take()
            >>> assert x == none()
            >>> assert y == some(2)

            >>> x = none()
            >>> y = x.take()
            >>> assert x == none()
            >>> assert y == none()
        """
        if self.is_none():
            return self

        self.__value, value = None, self.__value
        return some(value)

    def replace(self: Option[T], value: T) -> Option[T]:
        """Replaces the actual value in the option by the value given in parameter,
        returning the old value if present,
        leaving a [`Some`] in its place without deinitializing either one.

        Examples:
            >>> x = some(2)
            >>> old = x.replace(5)
            >>> assert x == some(5)
            >>> assert old == some(2)

            >>> x = none()
            >>> old = x.replace(3)
            >>> assert x == some(3)
            >>> assert old == none()
        """
        self.__value, old_value = value, self.__value
        return Option.some(old_value) if old_value is not None else Option.none()

    def contains(self: Option[T], value: T) -> bool:
        """Returns `True` if the option contains a value equal to the given value.

        Examples:
            >>> x = some(2)
            >>> assert x.contains(2)
            >>> assert not x.contains(3)
            >>> assert 2 in x
            >>> assert 3 not in x

            >>> x = none()
            >>> assert not x.contains(0)
            >>> assert 0 not in x
        """
        return self.__value == value

    def zip(self: Option[T], option: Option[U]) -> Option[Tuple[T, U]]:
        """Zips `self` with another `Option`.

        If `self` is `Some(T)` and `other` is `Some(U)`, this method returns `Some((T, U))`. Otherwise,
        `none()` is returned.

        Examples:
            >>> x = some(1)
            >>> y = some("hi")
            >>> z = none()
            >>> assert x.zip(y) == some((1, "hi"))
            >>> assert x.zip(z) == none()
        """
        if self.is_some() and option.is_some():
            return Option.some((self.__value, option.__value))

        return Option.none()

    def zip_with(self: Option[T], rhs: Option[U], func: Callable[[T, U], V]) -> Option[V]:
        """Zips `self` and another `Option` with function `func`.
        If `self` is `Some(T)` and `rhs` is `Some(T)`, this method returns `Some(func(T, U))`.
        Otherwise, `none()` is returned.

        Examples:
            >>> class Point:
            ...     def __init__(self, x: float, y: float):
            ...         self.x = x
            ...         self.y = y

            >>> x = some(17.5)
            >>> y = some(42.7)

            >>> assert x.zip_with(y, Point) == some(Point(17.5, 42.7))
            >>> assert x.zip_with(none(), Point) == none()
        """
        if self.is_some() and rhs.is_some():
            return Option.some(func(self.__value, rhs.__value))

        return Option.none()

    def transpose(self: Option[Result[T, E]]) -> Result[Option[T], E]:
        """Transposes an [`Option`] of a [`Result`] into a [`Result`] of an [`Option`].

        * [`None`] will be mapped to Result.ok(Option())

        * Option(Result.ok(_)) -> Result.ok(Option(_))

        * Option(Result.err(_)) -> Result.err(_)

        Examples:
            >>> x: Result[Option[int], Exception] = ok(some(5))
            >>> y: Option[Result[int, Exception]] = some(ok(5))
            >>> assert x == y.transpose()
        """
        from .result import Result, ok, err

        if not isinstance(self.__value, (Result, NoneType)):
            raise TypeError("Option must contain a Result when using transpose")

        if self.is_some_and(Result.is_ok):
            # Safety: we are sure that self.__value is not err because we checked it above.
            return ok(some(self.__value.unwrap()))

        if self.is_some_and(Result.is_err):
            # Safety: we are sure that self.__value is not ok because we checked it above.
            return err(self.__value.unwrap_err())

        if self.is_none():
            return ok(none())

    def flatten(self: Option[Option[T]]) -> Option[T]:
        """Converts from `Option[Option[T]]` to `Option[T]`.

        Examples:
        >>> x = some(some(6))
        >>> assert x.flatten() == some(6)

        >>> x = some(none())
        >>> assert x.flatten() == none()

        >>> x = none()
        >>> assert x.flatten() == none()

        >>> # Flattening only removes one level of nesting at a time:

        >>> x: Option[Option[Option[int]]] = some(some(some(6)))
        >>> assert x.flatten() == some(some(6))
        >>> assert x.flatten().flatten() == some(6)
        """
        if self.is_none():
            return self

        return self.__value

    ###########################################################################
    # Pythonic implementation
    ###########################################################################

    @classmethod
    @functools.cache
    def __class_getitem__(cls: Option[T], item: T) -> Option[T]:
        if isinstance(item, type):
            return cls
        raise TypeError("Option can only be used as a generic type")

    def __contains__(self: Option[T], value: T) -> bool:
        return self.contains(value)

    def __repr__(self: Option[T]) -> str:
        return f"<Option({self.__value})>" if self.is_some() else "<Option(None)>"

    def __bool__(self: Option[T]) -> bool:
        return self.is_some()


def some(value: T) -> Option[T]:
    """shortcut to create a some variant

    Examples:
        >>> x = some(2)
        >>> assert x == some(2)

        >>> x = some(2)
        >>> assert x.unwrap() == 2

        >>> x = some(2)
        >>> assert x.is_some()
    """
    return Option.some(value)


def none() -> Option[T]:
    """shortcut to create a some variant

    Examples:
        >>> x = none()
        >>> assert x.is_none()

        >>> x = none()
        >>> assert x.is_none()
    """
    return Option.none()
