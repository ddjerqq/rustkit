"""An interface for dealing with iterators.

This is the main iterator abstract base class.
For more about the concept of iterators generally,
please see the [module-level documentation].
In particular, you may want to know how to [implement `Iterator`][impl].
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Callable,
    Generic,
    Iterable,
    TYPE_CHECKING,
    Tuple,
    TypeVar,
)

from option import Option, some, NONE
from result import Result, ok, err

if TYPE_CHECKING:
    from iterator.vec import Vec
    from .collect import Collect
    from .step_by import StepBy
    from .chain import Chain
    from .zip import Zip
    from .map import Map
    from .filter import Filter
    from .filter_map import FilterMap
    from .enumerate import Enumerate
    from .peekable import Peekable
    from .skip_while import SkipWhile
    from .take_while import TakeWhile
    from .map_while import MapWhile

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


class Iterator(ABC, Generic[T], Iterable[T]):
    """An interface for dealing with iterators.

    This is the main iterator abstract base class.
    For more about the concept of iterators generally,
    please see the [module-level documentation].
    In particular, you may want to know how to [implement `Iterator`][impl].
    """
    __type__: T | None
    """T: it is recommended to provide what kind of type the iterator will yield"""

    __slots__ = ("__type__",)

    @abstractmethod
    def next(self: Iterator[T]) -> Option[T]:
        """Advances the iterator and returns the next value.

        Returns [`NONE`] when iteration is finished. Individual iterator
        implementations may choose to resume iteration, and so calling `next()`
        again may or may not eventually start returning [`some(Item)`] again at some point.

        Examples:
            >>> a = Vec[int]([1, 2, 3])
            >>> it = a.iter()

            >>> # A call to next() returns the next value
            >>> assert some(1) == it.next()
            >>> assert some(2) == it.next()
            >>> assert some(3) == it.next()

            >>> # and then NONE once it's over
            >>> assert NONE == it.next()

            >>> # More calls may or may not return `NONE`. Here, they always will.
            >>> assert NONE == it.next()
            >>> assert NONE == it.next()
        """
        raise NotImplementedError

    def __iter__(self: Iterator[T]) -> Iterator[T]:
        return self

    def __next__(self: Iterator[T]) -> T:
        if (nxt := self.next()).is_some():
            # Safety: we are sure that self.next is some
            return nxt.unwrap()

        # Stop a python for loop
        raise StopIteration

    def count(self: Iterator[T]) -> int:
        """Consumes the iterator, counting the number of iterations and returning it.

        This method will call [`next`] repeatedly until [`None`] is encountered,
        returning the number of times it saw [`Some`]. Note that [`next`] has to be
        called at least once even if the iterator does not have any elements.

        Examples:
            >>> a = Vec[int]([1, 2, 3])
            >>> assert a.iter().count() == 3

            >>> a = Vec[int]([1, 2, 3, 4, 5])
            >>> assert a.iter().count() == 5
        """
        return self.fold(0, lambda cnt, _: cnt + 1)

    def last(self: Iterator[T]) -> Option[T]:
        """Consumes the iterator, returning the last element.

        This method will evaluate the iterator until it returns [`NONE`]. While
        doing so, it keeps track of the current element. After [`NONE`] is
        returned, `last()` will then return the last element it saw.

        Examples
            >>> a = Vec[int]([1, 2, 3])
            >>> assert a.iter().last() == some(3)

            >>> a = Vec[int]([1, 2, 3, 4, 5])
            >>> assert a.iter().last() == some(5)
        """
        return self.fold(NONE, lambda _, nxt: some(nxt))

    def advance_by(self: Iterator[T], n: int) -> Result[..., int]:
        """Advances the iterator by `n` elements.

        This method will eagerly skip `n` elements by calling [`next`] up to `n`
        times until [`NONE`] is encountered.

        `advance_by(n)` will return [`Ok(...)`] if the iterator successfully advances by
        `n` elements, or [`Err(k)`] if [`NONE`] is encountered, where `k` is the number
        of elements the iterator is advanced by before running out of elements
        (i.e. the length of the iterator). Note that `k` is always less than `n`.

        Calling `advance_by(0)` can do meaningful work, for example [`Flatten`]
        can advance its outer iterator until it finds an inner iterator that is not empty, which
        then often allows it to return a more accurate `size_hint()` than in its initial state.

        [`Flatten`]: iterator.Flatten
        [`next`]: Iterator.next

        Examples:
            >>> a = Vec[int]([1, 2, 3, 4])
            >>> it = a.iter()

            >>> assert it.advance_by(2) == ok(...)
            >>> assert it.next() == some(3)
            >>> assert it.advance_by(0) == ok(...)
            >>> assert it.advance_by(100) == err(1)  # only one element - `4` was skipped
        """
        for i in range(n):
            if self.next().is_none():
                return err(i)

        return ok(...)

    def nth(self: Iterator[T], n: int) -> Option[T]:
        """Returns the `n`th element of the iterator.

        Like most indexing operations, the count starts from zero, so `nth(0)`
        returns the first value, `nth(1)` the second, and so on.

        Note that all preceding elements, as well as the returned element, will be
        consumed from the iterator. That means that the preceding elements will be
        discarded, and also that calling `nth(0)` multiple times on the same iterator
        will return different elements.

        `nth()` will return [`NONE`] if `n` is greater than or equal to the length of the iterator.

        Examples:
        >>> a = Vec[int]([1, 2, 3])
        >>> assert a.iter().nth(1) == some(2)

        >>> # Calling `nth()` multiple times doesn't rewind the iterator:
        >>> a = Vec[int]([1, 2, 3])

        >>> it = a.iter()

        >>> assert it.nth(1) == some(2)
        >>> assert it.nth(1) == NONE

        >>> # Returning `None` if there are less than `n + 1` elements:
        >>> a = Vec[int]([1, 2, 3])
        >>> assert a.iter().nth(10) == NONE
        """
        if self.advance_by(n).ok().is_none():
            return NONE

        return self.next()

    def step_by(self: Iterator[T], step: int) -> StepBy[T]:
        """Creates an iterator starting at the same point, but stepping by
        the given amount at each iteration.

        Note 1: The first element of the iterator will always be returned,
        regardless of the step given.

        Note 2: The time at which ignored elements are pulled is not fixed.
        `StepBy` behaves like the sequence `self.next()`, `self.nth(step-1)`,
        `self.nth(step-1)`, ..., but is also free to behave like the sequence
        `advance_n_and_return_first(&mut self, step)`,
        `advance_n_and_return_first(&mut self, step)`, ...
        Which way is used may change for some iterators for performance reasons.
        The second way will advance the iterator earlier and may consume more items.

        `advance_n_and_return_first` is the equivalent of:
        >>> def advance_n_and_return_first(it: Iterator[T], n: int) -> Option[T]:
        ...     nxt = it.next()
        ...     if n > 1:
        ...         it.nth(n - 2)
        ...     return nxt

        Raises:
            ValueError: if the given step is `0`.

        Examples:
        >>> a = Vec[int]([0, 1, 2, 3, 4, 5])
        >>> it = a.iter().step_by(2)

        >>> assert it.next() == some(0)
        >>> assert it.next() == some(2)
        >>> assert it.next() == some(4)
        >>> assert it.next() == NONE
        """
        from .step_by import StepBy
        return StepBy(self, step)

    def chain(self: Iterator[T], other: Iterator[T]) -> Chain[T]:
        """Takes two iterators and creates a new iterator over both in sequence.

        `chain()` will return a new iterator which will first iterate over
        values from the first iterator and then over values from the second
        iterator.

        In other words, it links two iterators together, in a chain. 🔗

        [`once`] is commonly used to adapt a single value into a chain of
        other kinds of iteration.

        Examples:
            >>> a1 = Vec[int]([1, 2, 3])
            >>> a2 = Vec[int]([4, 5, 6])

            >>> it = a1.iter().chain(a2.iter())

            >>> assert it.next() == some(1)
            >>> assert it.next() == some(2)
            >>> assert it.next() == some(3)
            >>> assert it.next() == some(4)
            >>> assert it.next() == some(5)
            >>> assert it.next() == some(6)
            >>> assert it.next() == NONE

        Since the argument to `chain()` must be an Iterable[T]
        we can use python's built-in data structures as well.

        [`once`]: iterator.once
        """
        from .chain import Chain
        return Chain(self, other)

    def zip(self: Iterator[T], other: Iterator[T]) -> Zip[Tuple[T, U]]:
        """'Zips up' two iterators into a single iterator of pairs.

        `zip()` returns a new iterator that will iterate over two other
        iterators, returning a tuple where the first element comes from the
        first iterator, and the second element comes from the second iterator.

        In other words, it zips two iterators together, into a single one.

        If either iterator returns [`None`], [`next`] from the zipped iterator will return [`None`].
        If the zipped iterator has no more elements to return then each further attempt to advance
        it will first try to advance the first iterator at most one time and if it still yielded an item
        try to advance the second iterator at most one time.

        Examples:
            >>> xs = Vec[int]([1, 2, 3])
            >>> ys = Vec[int]([4, 5, 6])
            >>>
            >>> it = xs.iter().zip(ys)
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

        `zip()` is often used to zip an infinite iterator to a finite one.
        This works because the finite iterator will eventually return [`None`],
        ending the zipper. Zipping with `(0..)` can look a lot like [`enumerate`]:
            >>> enum = list(enumerate("foo"))

            >>> zipper = Vec[int](range(1, 1000)).iter().zip("foo").collect[Vec]()

            >>> assert (0, 'f') == enum[0]
            >>> assert (0, 'f') == zipper[0]

            >>> assert (1, 'o') == enum[1]
            >>> assert (1, 'o') == zipper[1]

            >>> assert (2, 'o') == enum[2]
            >>> assert (2, 'o') == zipper[2]
        """
        from .zip import Zip
        return Zip(self, other)

    def map(self: Iterator[T], func: Callable[[T], U]) -> Map[Iterator[T], Callable[[T], U]]:
        """Takes a closure and creates an iterator which calls that closure on each element.

        `map()` transforms one iterator into another, by means of its argument:
        something that is [`Callable`]. It produces a new iterator which
        calls this closure on each element of the original iterator.

        If you are good at thinking in types, you can think of `map()` like this:
        If you have an iterator that gives you elements of some type `A`, and
        you want an iterator of some other type `B`, you can use `map()`,
        passing a closure that takes an `A` and returns a `B`.

        `map()` is conceptually similar to a [`for`] loop. However, as `map()` is
        lazy, it is best used when you're already working with other iterators.
        If you're doing some sort of looping for a side effect, it's considered
        more idiomatic to use [`for`] than `map()`.

        Examples:
            >>> a = Vec[int]([1, 2, 3])

            >>> it = a.iter().map(lambda i: i * 2)

            >>> assert it.next() == some(2)
            >>> assert it.next() == some(4)
            >>> assert it.next() == some(6)
            >>> assert it.next() == NONE
        """
        from .map import Map
        return Map(self, func)

    def for_each(self: Iterator[T], func: Callable[[T], None]) -> None:
        self.fold(None, lambda _, nxt: func(nxt))

    def filter(self: Iterator[T], pred: Callable[[T], bool]) -> Filter[T]:
        """Creates an iterator which uses a closure to determine if an element should be yielded.

        Given an element the closure must return `True` or `False`. The returned
        iterator will yield only the elements for which the closure returns True.

        Examples:
            >>> a = Vec[int]([-1, 1, 2])

            >>> it = a.iter().filter(lambda x: x >= 0)

            >>> assert it.next() == some(1)
            >>> assert it.next() == some(2)
            >>> assert it.next() == NONE
        """
        from .filter import Filter
        return Filter(self, pred)

    def filter_map(self: Iterator[T], func: Callable[[T], Option[U]]) -> FilterMap[T]:
        """Creates an iterator that both filters and maps.

        The returned iterator yields only the `value`s for which the supplied
        closure returns `Some(value)`.

        `filter_map` can be used to make chains of [`filter`] and [`map`] more
        concise. The example below shows how a `map().filter().map()` can be
        shortened to a single call to `filter_map`.

        [`filter`]: Iterator.filter
        [`map`]: Iterator.map

        Examples:
            >>> a = Vec[str](["1", "two", "NaN", "four", "5"])
            >>> it = a.iter().filter_map(lambda s: Result.from_(int, s).ok())
            >>> assert it.next() == some(1)
            >>> assert it.next() == some(5)
            >>> assert it.next() == NONE

        Here's the same example, but with [`filter`] and [`map`]:
            >>> a = Vec[str](["1", "two", "NaN", "four", "5"])
            >>> it = a.iter().map(lambda s: Result.from_(int, s).filter(Result.is_ok).map(Result.unwrap)
            >>> assert it.next() == some(1))
            >>> assert it.next() == some(5))
            >>> assert it.next() == NONE)
        """
        from .filter_map import FilterMap
        return FilterMap(self, func)

    def enumerate(self: Iterator[T]) -> Enumerate[T]:
        """Creates an iterator which gives the current iteration count as well as
        the next value.

        The iterator returned yields pairs `(i, val)`, where `i` is the
        current index of iteration and `val` is the value returned by the
        iterator.

        `enumerate()` keeps its count as a [`usize`]. If you want to count by a
        different sized integer, the [`zip`] function provides similar
        functionality.

        Examples:
            >>> a = Vec[str](['a', 'b', 'c'])
            >>> it = a.iter().enumerate()
            >>> assert it.next() == some((0, 'a'))
            >>> assert it.next() == some((1, 'b'))
            >>> assert it.next() == some((2, 'c'))
            >>> assert it.next() == NONE)
        """
        from .enumerate import Enumerate
        return Enumerate(self)

    def peekable(self: Iterator[T]) -> Peekable[T]:
        """Creates an iterator which can use the [`peek`] method
        to look at the next element of the iterator without consuming it. See
        their documentation for more information.

        Note that the underlying iterator is still advanced when [`peek`] is
        called for the first time: In order to retrieve the next element,
        [`next`] is called on the underlying iterator, hence any side effects
        (i.e. anything other than fetching the next value) of the [`next`]
        method will occur.

        Note:
            unlike the Rust version, this one does not have peek_mut because
            it does not make sense in Python.


        Examples:
            >>> xs = Vec[int]([1, 2, 3])
            >>> it = xs.iter().peekable()

            >>> # peek() lets us see into the future
            >>> assert it.peek() == some(1)
            >>> assert it.next() == some(1)

            >>> assert it.next() == some(2)

            >>> # we can peek() multiple times, the iterator won't advance
            >>> assert it.peek() == some(3)
            >>> assert it.peek() == some(3)

            >>> assert it.next() == some(3)

            >>> # after the iterator is finished, so is peek()
            >>> assert it.peek() == NONE
            >>> assert it.next() == NONE
        """
        from .peekable import Peekable
        return Peekable(self)

    def skip_while(self: Iterator[T], predicate: Callable[[T], bool]) -> SkipWhile[T]:
        """Creates an iterator that [`skip`]s elements based on a predicate.

        [`skip`]: Iterator.skip

        `skip_while()` takes a callable as an argument. It will call this
        callable on each element of the iterator, and ignore elements
        until it returns `false`.

        After `false` is returned, `skip_while()`'s job is over, and the
        rest of the elements are yielded.

        Examples:
            >>> a = Vec[int]([-1, 0, 1])

            >>> it = a.iter().skip_while(lambda x: x < 0)

            >>> assert it.next() == some(0)
            >>> assert it.next() == some(1)
            >>> assert it.next() == NONE

        # Stopping after an initial `false`:
            >>> a = Vec[int]([-1, 0, 1, -2])

            >>> it = a.iter().skip_while(lambda x: x < 0)

            >>> assert it.next() == some(0)
            >>> assert it.next() == some(1)

            >>> # while this would have been false, since we already got a false,
            >>> # skip_while() isn't used anymore
            >>> assert it.next() == some(-2)
            >>> assert it.next() == NONE
        """
        from .skip_while import SkipWhile
        return SkipWhile(self, predicate)

    def take_while(self: Iterator[T], predicate: Callable[[T], bool]) -> TakeWhile[T]:
        """Creates an iterator that yields elements based on a predicate.

        `take_while()` takes a closure as an argument. It will call this
        closure on each element of the iterator, and yield elements
        while it returns `true`.

        After `false` is returned, `take_while()`'s job is over, and the
        rest of the elements are ignored.

        Examples:
            >>> a = Vec[int]([-1, 0, 1])
            >>> it = a.iter().take_while(lambda x: x < 0)
            >>> assert it.next() == some(-1)
            >>> assert it.next() == NONE
        """
        from .take_while import TakeWhile
        return TakeWhile(self, predicate)

    def map_while(self: Iterator[T], predicate: Callable[[T], Option[U]]) -> MapWhile[T]:
        """
        Creates an iterator that both yields elements based on a predicate and maps.

        `map_while()` takes a closure as an argument. It will call this
        closure on each element of the iterator, and yield elements
        while it returns [`Some(_)`][`Some`].

        Examples:
            >>> a = Vec([-1, 4, "0", "abc"])
            >>> it = a.iter().map_while(lambda i: Result.from_(int, i).ok())
            >>> assert it.next() == some(-1)
            >>> assert it.next() == some(4)
            >>> assert it.next() == some(0)
            >>> assert it.next() == NONE

        Here's the same example, but with [`take_while`] and [`map`]:

        [`take_while`]: Iterator.take_while
        [`map`]: Iterator.map

        >>> a = Vec([-1, 4, "NaN", 1])
        >>> it = a.iter()\
        ...       .map(lambda x: Result.from_(int, x).ok())\
        ...       .take_while(Option.is_some)\
        ...       .map(Option.unwrap)

        >>> assert it.next() == some(-1)
        >>> assert it.next() == some(4)
        >>> assert it.next() == NONE

        >>> # Stopping after an initial [`None`]:

        >>> a = Vec([0, 1, 2, "abc", 4, 5])
        >>> it = a.iter().map_while(lambda x: Result.from_(int, x).ok())
        >>> vec = it.collect()

        >>> # We have more elements which could fit in int (4, 5), but `map_while` returned `None` for `abc`
        >>> # (as the `predicate` returned `None`) and `collect` stops at the first `None` encountered.
        >>> assert vec == [1, 2, 3]

        Note that unlike [`take_while`] this iterator is **not** fused.
        It is also not specified what this iterator returns after the first [`None`] is returned.
        If you need fused iterator, use [`fuse`].

        [`fuse`]: Iterator::fuse
        """
        from .map_while import MapWhile
        return MapWhile(self, predicate)

    def skip(self: Iterator[T], n: int) -> Skip[T]:
        ...

    def take(self: Iterator[T], n: int) -> Take[T]:
        ...

    def flat_map(self: Iterator[T], func: Callable[[T], Iterator[U]]) -> FlatMap[T]:
        ...

    def flatten(self: Iterator[Iterator[T]]) -> Flatten[Iterator[Iterator[T]]]:
        ...

    def fuse(self: Iterator[T]) -> Fuse[T]:
        ...

    def collect(self: Iterator[T]) -> Collect:
        """Transforms an iterator into a collection.

        `collect()` can take anything iterable, and turn it into a relevant
        collection. This is one of the more powerful methods in the standard
        library, used in a variety of contexts.

        The most basic pattern in which `collect()` is used is to turn one
        collection into another. You take a collection, call [`iter`] on it,
        do a bunch of transformations, and then `collect()` at the end.

        `collect()` can also create instances of types that are not typical
        collections. For example, a [`String`] can be built from [`char`]s,
        and an iterator of [`Result[T, E]`][`Result`] items can be collected
        into `Result[Collection[T], E]`. See the examples below for more.

        Because `collect()` is so general, it can cause problems with type
        inference.

        Examples:
            >>> a = Vec[int]([1, 2, 3])
            >>> doubled = a.iter().map((2).__mul__).collect[list[int]]()
            >>> assert doubled == [2, 4, 6]


            >>> # Using `collect()` to make a [`String`]:

            >>> chars = Vec[str](['g', 'd', 'k', 'k', 'n'])
            >>> hello = chars.iter().map(ord).map(lambda x: chr(x + 1)).collect[str]()
            >>> assert hello == "hello"


            >>> # If you have a list of [`Result[T, E]`][`Result`]s, you can use `collect()` to
            >>> # see if any of them failed:

            >>> results = Vec[Result[int, str]]([ok(1), err("nope"), ok(3), err("bad")])
            >>> result = results.iter().collect[Result[Vec[int], str]]()
            >>> # gives us the first error
            >>> assert result == err("nope")


            >>> results = Vec[Result[int, str]]([ok(1), ok(3)])
            >>> result = results.iter().collect[Result[Vec[int], str]]()

            >>> # gives us the list of answers
            >>> assert result == ok(Vec[int]([1, 3])
        [`iter`]: Iterator.next
        """
        ...

    def partition(self: Iterator[T], predicate: Callable[[T], bool]) -> Tuple[Iterator[U], Iterator[U]]:
        from ..vec import Vec

        def extend(f: Callable[[T], bool], lft: Extend[T], r: Extend[T]) -> Callable[[T], None]:
            return lambda _, x: (lft.extend(x) if f(x) else r.extend(x))

        left = Vec[self.__type]()
        right = Vec[self.__type]()
        self.fold(None, extend(predicate, left, right))  # type: ignore
        return left, right

    def try_fold(self: Iterator[T], accum: U, func: Callable[[U, T], Result[T, E]]) -> Result[T, E]:
        while (x := self.next()).is_some():
            accum = func(accum, x)
            if accum.is_err():
                return accum

        if accum.is_err():
            return accum

    def fold(self: Iterator[T], accum: U, func: Callable[[U, T], U]) -> U:
        while (nxt := self.next()).is_some():
            accum = func(accum, nxt.unwrap())
        return accum

    def reduce(self: Iterator[T], func: Callable[[T, T], T]) -> Option[T]:
        if (first := self.next()).is_none():
            return first
        return Option.some(self.fold(first.unwrap(), func))

    def all(self: Iterator[T], predicate: Callable[[T], bool]) -> bool:
        return self.fold(True, lambda accum, nxt: accum and predicate(nxt))

    def any(self: Iterator[T], predicate: Callable[[T], bool]) -> bool:
        return self.fold(False, lambda accum, nxt: accum or predicate(nxt))

    def find(self: Iterator[T], predicate: Callable[[T], bool]) -> Option[T]:
        return self.fold(Option.none(), lambda _, nxt: Option.some(nxt) if predicate(nxt) else Option.none())

    def find_map(self: Iterator[T], func: Callable[[T], Option[U]]) -> Option[U]:
        return self.fold(Option.none(), lambda _, nxt: func(nxt) if func(nxt).is_some() else Option.none())

    def position(self: Iterator[T], predicate: Callable[[T], bool]) -> Option[int]:
        return self.fold(Option.none(), lambda accum, nxt: Option.some(accum + 1) if predicate(nxt) else Option.none())

    def max_by(self: Iterator[T], key: Callable[[T, T], bool]) -> Option[T]:
        def fold(compare: Callable[[T, T], bool]) -> Callable[[T, T], T]:
            return lambda x, y: x if compare(x, y) else y

        return self.reduce(fold(key))

    def max(self: Iterator[T]) -> Option[T]:
        return self.max_by(int.__gt__)

    def min_by(self: Iterator[T], key: Callable[[T, T], bool]) -> Option[T]:
        def fold(compare: Callable[[T, T], bool]) -> Callable[[T, T], T]:
            return lambda x, y: y if compare(x, y) else x

        return self.reduce(fold(key))

    def min(self: Iterator[T]) -> Option[T]:
        return self.min_by(int.__lt__)

    def cycle(self: Iterator[T]) -> Cycle[T]:
        ...

    def sum(self: Iterator[T]) -> T:
        return sum(self.collect())

    def product(self: Iterator[T]) -> Product[T]:
        ...

    def eq_by(self: Iterator[T], other: Iterator[U], eq: Callable[[T, U], bool]) -> bool:
        while True:
            x = self.next()

            if x.is_none():
                return other.next().is_none()

            if x.is_some():
                x = x.unwrap()

            y = other.next()

            if y.is_none():
                return False

            if y.is_some():
                y = y.unwrap()

            if not eq(x, y):
                return False

    def eq(self: Iterator[T], other: Iterator[T]) -> bool:
        return self.eq_by(other, lambda x, y: x == y)

    def ne(self: Iterator[T], other: Iterator[T]) -> bool:
        return not self.eq(other)
