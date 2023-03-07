"""Composable external iteration.

If you've found yourself with a collection of some kind, and needed to
perform an operation on the elements of said collection, you'll quickly run
into 'iterators'. Iterators are heavily used in idiomatic Python code, so
it's worth becoming familiar with them.

Before explaining more, let's talk about how this module is structured:

# Organization

This module is largely organized by type:

* [Traits] are the core portion: these traits define what kind of iterators
  exist and what you can do with them. The methods of these traits are worth
  putting some extra study time into.

* [Functions] provide some helpful ways to create some basic iterators.

* [Structs] are often the return types of the various methods on this
  module's traits. You'll usually want to look at the method that creates
  the `struct`, rather than the `struct` itself. For more detail about why,
  see '[Implementing Iterator](#implementing-iterator)'.

[Traits]: #traits
[Functions]: #functions
[Structs]: #structs

That's it! Let's dig into iterators.

# Iterator:

The heart and soul of this module is the [`Iterator`] trait. The core of
[`Iterator`] looks like this:

    >>> class Iterator_:
    ...     __type__: int
    ...     def next(self) -> Option[int]:
    ...         ...


An iterator has a method, [`next`], which when called, returns an object of type __type__.
Calling [`next`] will return [`Some(Item)`] as long as there are elements,
and once they've all been exhausted, will return `None` to indicate that iteration is finished.
Individual iterators may choose to resume iteration, and so calling [`next`] again may or may
not eventually start returning [`Some(Item)`] again at some point (for example, see [`TryIter`]).

[`Iterator`]'s full definition includes a number of other methods as well,
but they are default methods, built on top of [`next`], and so you get
them for free.

Iterators are also composable, and it's common to chain them together to do
more complex forms of processing. See the [Adapters](#adapters) section
below for more details.

[`Some(Item)`]: Some
[`next`]: Iterator.next

# The three forms of iteration:

There are three common methods which can create iterators from a collection:

* `iter()`, which iterates over `&T` without consuming the collection.
* `into_iter()`, which iterates over `T` by consuming the collection.

Various things in the standard library may implement one or more of the
three, where appropriate.

# Implementing Iterator:

Creating an iterator of your own involves two steps: creating a `class` to
hold the iterator's state, and then implementing [`Iterator`] for that `class`.
This is why there are so many `class`es in this module: there is one for
each iterator and iterator adapter.

Let's make an iterator named `Counter` which counts from `1` to `5`:

    >>> # First, the class:

    # An iterator which counts from one to five
    >>> from src.option import some, NONE, Option

    >>> class Counter(Iterator[int]):
    ...     def __init__(self, start: int = 0) -> None:
    ...         self.start = start
    ...
    ...     def next(self) -> Option[int]:
    ...         self.count += 1
    ...         return some(self.start - 1)

    >>> # And now we can use it!
    >>> counter = Counter()
    >>> assert counter.next() == some(1)
    >>> assert counter.next() == some(2)
    >>> assert counter.next() == some(3)
    >>> assert counter.next() == some(4)
    >>> assert counter.next() == some(5)

Calling [`next`] this way gets repetitive. Rust has a construct which can
call [`next`] on your iterator, until it reaches `None`. Let's go over that
next.

Also note that `Iterator` provides a default implementation of methods such as `nth` and `fold`
which call `next` internally. However, it is also possible to write a custom implementation of
methods like `nth` and `fold` if an iterator can compute them more efficiently without calling `next`.

# `for` loops and `IntoIterator`

Python's `for` loop syntax is actually sugar for iterators. Here's a basic example of `for`:

    >>> from src.vec import Vec
    >>> values = Vec[int]([1, 2, 3, 4, 5])
    >>>
    >>> for x in values:
    >>>     print(f"{x}")

# Adapters:

Functions which take an [`Iterator`] and return another [`Iterator`] are
often called 'iterator adapters', as they're a form of the 'adapter
pattern'.

Common iterator adapters include [`map`], [`take`], and [`filter`].
For more, see their documentation.

If an iterator adapter panics, the iterator will be in an unspecified (but
memory safe) state. This state is also not guaranteed to stay the same
across versions of Rust, so you should avoid relying on the exact values
returned by an iterator which panicked.

[`map`]: Iterator.map
[`take`]: Iterator.take
[`filter`]: Iterator.filter

# Laziness:

Iterators (and iterator [adapters](#adapters)) are *lazy*. This means that
just creating an iterator doesn't _do_ a lot. Nothing really happens
until you call [`next`]. This is sometimes a source of confusion when
creating an iterator solely for its side effects. For example, the [`map`]
method calls a closure on each element it iterates over:

    >>> v = Vec[int]([1, 2, 3, 4, 5])
    >>> v.iter().map(print)

This will not print any values, as we only created an iterator, rather than
using it. The compiler will warn us about this kind of behavior:

The idiomatic way to write a [`map`] for its side effects is to use a
`for` loop or call the [`for_each`] method:

    >>> v = Vec[int]([1, 2, 3, 4, 5])

    >>> v.iter().for_each(print)
    >>> # or
    >>> for x in v:
    >>>     print(x)

[`map`]: Iterator.map
[`for_each`]: Iterator.for_each

Another common way to evaluate an iterator is to use the [`collect`]
method to produce a new collection.
# TODO add to_vec, to_list
[`collect`]: Iterator.collect

# Infinity

Bear in mind that methods on infinite iterators, even those for which a
result can be determined mathematically in finite time, might not terminate.
Specifically, methods such as [`min`], which in the general case require
traversing every element in the iterator, are likely not to return
successfully for any infinite iterators.
"""

from .iterator import Iterator
from .from_fn import FromFn, from_fn
from .chain import Chain
