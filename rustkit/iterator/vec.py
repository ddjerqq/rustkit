"""# A contiguous growable array type with heap-allocated contents, written [`Vec[T]`]
a better overall python list

## Examples:

#### You can explicitly create a [`Vec`] with [`Vec[type]()`]:

>>> v = Vec[int]()

#### You can [`push`] values onto the end of a vector (which will grow the vector as needed):

>>> v = Vec[int]([1, 2])
>>> v.append(3)
>>> assert v == [1, 2, 3]

#### Popping values works in much the same way:

>>> v = Vec[int]([1, 2])
>>> two = v.pop()

#### Vectors also support indexing:

>>> v = Vec[int]([1, 2])
>>> three = v[2]
>>> v[1] = v[1] + 5
"""

from __future__ import annotations

import functools
from typing import (
    Callable,
    Union,
    Iterable,
    TypeVar,
    SupportsIndex,
    List,
    Tuple,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from iterator.iterator import Iterator

from option import Option
from result import Result, ok, err


__all__ = ("Vec",)

T = TypeVar("T")

# groupby TypeVars
U = TypeVar("U")
V = TypeVar("V")
TKey = TypeVar("TKey")


class Vec(List[T]):
    """
    # A Python implementation of the legendary [`Vec<T>`] type from Rust.
    """

    __buffer: list[T]
    __type__: T | None
    __slots__ = ("__buffer", "__type__")

    def __check_value(self, value: T) -> None:
        if self.__type__ and not isinstance(value, self.__type__):
            raise TypeError(
                f"expected '{self.__type__.__name__}' got '{self.__type__.__name__}' instead. \n"
                f"if you don't want the vec to be strictly typed, just don't pass a type to the creation"
            )

    ###########################################################################
    # Python list methods
    ###########################################################################

    def append(self: Vec[T], value: T) -> None:
        """Append an object to the end of the vec.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.

        Examples:
            >>> vec = Vec[int]()
            >>> vec.append(1)
            >>> vec.append(2)
            >>> vec.append("3")  # type: ignore # Raises a TypeError + gives type hint warnings
        """
        self.__check_value(value)
        self.__buffer.append(value)

    def clear(self: Vec[T]) -> None:
        """Remove all items from this vec.

        Examples:
            >>> vec = Vec[int]([1, 2, 3])
            >>> vec.clear()
            >>> assert vec.len() == 0
        """
        self.__buffer.clear()

    def copy(self: Vec[T]) -> Vec[T]:
        """Return a shallow copy of the vec.

        Examples:
            >>> vec = Vec[int]([1, 2, 3])
            >>> vec_copy = vec.copy()
            >>> assert vec_copy == vec
        """
        return Vec[self.__type__](self.__buffer.copy())

    def count(self: Vec[T], value: T) -> int:
        """Return number of occurrences of value in this vec.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.

        Examples:
            >>> vec = Vec[int]([1, 2, 3, 1])
            >>> assert vec.count(1) == 2
            >>> assert vec.count("4") == 0  # type: ignore # Raises a TypeError + gives type hint warnings
        """
        self.__check_value(value)
        return self.__buffer.count(value)

    def extend(self: Vec[T], other: Iterable[T]) -> None:
        """Extend vec by appending elements from the other iterable.

        Note:
            if [`other`] is a destructible iterable, it will be consumed.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.

        Examples:
            >>> vec = Vec[int]([1, 2, 3])
            >>> vec.extend([4, 5, 6])
            >>> assert vec == Vec[int]([1, 2, 3, 4, 5, 6])
        """
        if isinstance(other, Vec):
            if self.__type__ == other.__type__:
                self.__buffer.extend(other.__buffer)

        self.__buffer.extend(other.__buffer)

    def index(self: Vec[T], value: T, after: SupportsIndex = None, before: SupportsIndex = None) -> int:
        """
        Return first index of value in range [after, before].

        Raises:
             ValueError: if the value is not present.
             TypeError: if the vec is strictly typed and the value is not of the same type as this vec.

        Examples:
            >>> vec = Vec[int]([1, 2, 3])
            >>> assert vec.index(1) == 0
            >>> assert vec.index("4") == 0  # type: ignore # Raises a TypeError + gives type hint warnings
            >>> assert vec.index(4) == 0  # Raises a ValueError

            >>> vec = Vec[int]([1, 2, 3, 4, 5, 6])
            >>> assert vec.index(4, after=2) == 3
            >>> assert vec.index(4, before=5) == 3
        """
        self.__check_value(value)
        return self.__buffer.index(value, after, before)

    def insert(self: Vec[T], idx: SupportsIndex, value: T) -> None:
        """Insert object before index.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.
            IndexError: if the index is out of range.

        Examples:
            >>> vec = Vec[int]([1, 2, 3])
            >>> vec.insert(1, 4)
            >>> assert vec == Vec[int]([1, 4, 2, 3])
        """
        self.__check_value(value)
        self.__buffer.insert(idx, value)

    def pop(self: Vec[T], idx: SupportsIndex = -1) -> T:
        """Remove and return item at index (default last).

        Raises:
             IndexError: if list is empty or index is out of range.
        """
        return self.__buffer.pop(idx)

    def remove(self: Vec[T], value: T) -> T:
        """Remove first occurrence of value.

        Raises:
            ValueError: if the value is not present.
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.
        """
        self.__check_value(value)
        return self.__buffer.remove(value)

    def reverse(self: Vec[T]) -> None:
        """Reverse *IN PLACE*.
        """
        return self.__buffer.reverse()

    def sort(self: Vec[T], *, key: Callable[[T], Union[int, float, str]] = None, reverse: bool = False) -> None:
        """Sort the list in ascending order and return None.

        The sort is in-place (i.e. the list itself is modified) and stable
        (i.e. the order of two equal elements is maintained).

        If a key function is given, apply it once to each list item and sort them,
        ascending or descending, according to their function values.

        The reverse flag can be set to sort in descending order.
        """
        self.__buffer.sort(key=key, reverse=reverse)

    def __add__(self: Vec[T], rhs: Iterable[T]) -> Vec[T]:
        """Return self + value.

        Note:
            if [`rhs`] is a destructible iterable, it will be consumed.

        Raises:
            TypeError: if the vec is strictly typed and the other iterable contains
                values that are not of the same type as this vec.
            TypeError: if the vec is strictly typed and rhs is a vec of a different type.
        """
        if isinstance(rhs, Vec):
            if self.__type__ == rhs.__type__:
                return Vec[self.__type__](self.__buffer + rhs.__buffer)

            raise TypeError(f"Cannot add Vec[{self.__type__}] to Vec[{rhs.__type__}]")

        if self.__type__:
            # is self is typed we need to check the type of the other iterable
            out = []

            for item in rhs:
                self.__check_value(item)
                out.append(item)

            return Vec[self.__type__](self.__buffer.__add__(out))

        return Vec[self.__type__](self.__buffer.__add__(list(rhs)))

    @classmethod
    @functools.cache
    def __class_getitem__(cls, key: T) -> Vec[T]:
        if isinstance(key, type):
            return type(  # type: ignore
                f"Vec[{key.__name__}]",
                (cls,),
                {"__type__": key},
            )

        raise TypeError(f"Vec's type must be a type, not '{type(key)}'")

    def __contains__(self: Vec[T], value: T) -> bool:
        """Return key in self.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.
        """
        self.__check_value(value)
        return self.__buffer.__contains__(value)

    def __delitem__(self: Vec[T], idx: SupportsIndex | slice) -> None:
        """Delete self[key].

        Raises:
            IndexError: if the index is out of range.
        """
        self.__buffer.__delitem__(idx)

    def __eq__(self: Vec[T], rhs: Iterable[T]) -> bool:
        if isinstance(rhs, Vec):
            if self.__type__ == rhs.__type__ or (not self.__type__ and not rhs.__type__):
                return self.__buffer.__eq__(rhs.__buffer)

            # no point in checking if the types are different.
            return False

        return self.__buffer.__eq__(rhs)

    def __getitem__(self: Vec[T], key: SupportsIndex | slice) -> T | Vec[T]:
        if isinstance(key, slice):
            return Vec(self.__buffer.__getitem__(key))

        return self.__buffer.__getitem__(key)

    def __ge__(self: Vec[T], rhs: List[T]) -> bool:
        if isinstance(rhs, Vec):
            if self.__type__ == rhs.__type__ or (not self.__type__ and not rhs.__type__):
                return self.__buffer.__ge__(rhs.__buffer)
            # no point in checking if the types are different.
            return False

        return self.__buffer.__ge__(rhs)

    def __gt__(self: Vec[T], rhs: List[T]) -> bool:
        if isinstance(rhs, Vec):
            if self.__type__ == rhs.__type__ or (not self.__type__ and not rhs.__type__):
                return self.__buffer.__gt__(rhs.__buffer)
            # no point in checking if the types are different.
            return False

        return self.__buffer.__gt__(rhs)

    def __iadd__(self: Vec[T], rhs: Iterable[T]) -> None:
        """Return self + value.

        Note:
            if [`rhs`] is a destructible iterable, it will be consumed.

        Raises:
            TypeError: if the vec is strictly typed and the other iterable contains
        """
        if self.__type__:
            for item in rhs:
                self.__check_value(item)
                self.__buffer.append(item)
        else:
            self.__buffer.extend(rhs)

    def __imul__(self: Vec[T], rhs: int) -> None:
        """Return self * value.
        """
        self.__buffer.__imul__(rhs)

    def __init__(self: Vec[T], seq: Iterable[T] | None = None) -> None:
        """Initialize a new Vector[T].

        Args:
            seq: an iterable to initialize the vector with.
                 note, if the iterable is destructible, it will be consumed.

        Raises:
            TypeError: if the vec is strictly typed and the other iterable contains an item of a different type.
        """
        super().__init__()
        if seq:
            self.extend(seq)

    def __iter__(self: Vec[T]) -> Iterable[T]:
        """return a rust iterator
        """
        # TODO make this return a regular iterator.
        raise NotImplementedError

    def __len__(self: Vec[T]) -> int:
        return self.__buffer.__len__()

    def __le__(self: Vec[T], rhs: List[T]) -> bool:
        if isinstance(rhs, Vec):
            if self.__type__ == rhs.__type__ or (not self.__type__ and not rhs.__type__):
                return self.__buffer.__le__(rhs.__buffer)
            # no point in checking if the types are different.
            return False

        return self.__buffer.__le__(rhs)

    def __lt__(self: Vec[T], rhs: List[T]) -> bool:
        if isinstance(rhs, Vec):
            if self.__type__ == rhs.__type__ or (not self.__type__ and not rhs.__type__):
                return self.__buffer.__lt__(rhs.__buffer)
            # no point in checking if the types are different.
            return False

        return self.__buffer.__lt__(rhs)

    def __mul__(self: Vec[T], rhs: int) -> Vec[T]:
        return Vec[self.__type__](self.__buffer.__mul__(rhs))

    def __ne__(self: Vec[T], rhs: List[T]) -> bool:
        if isinstance(rhs, Vec):
            if self.__type__ == rhs.__type__ or (not self.__type__ and not rhs.__type__):
                return self.__buffer.__ne__(rhs.__buffer)
            # no point in checking if the types are different.
            return False

        return self.__buffer.__ne__(rhs)

    def __repr__(self: Vec[T]) -> str:
        return f"Vec[{self.__type__.__name__}]({self.__buffer!r})"

    def __reversed__(self: Vec[T]) -> Iterable[T]:
        """Return a reverse iterator over the list.
        """
        # TODO make iter() method to return iterator else return iterator
        raise NotImplementedError

    def __rmul__(self: Vec[T], rhs: int) -> Vec[T]:
        return Vec[self.__type__](self.__buffer.__rmul__(rhs))

    def __setitem__(self: Vec[T], key: SupportsIndex, value: T) -> None:
        self.__check_value(value)
        self.__buffer.__setitem__(key, value)

    ###########################################################################
    # Rust vector associative functions
    ###########################################################################

    def iter(self: Vec[T]) -> Iterator[T]:
        """Return a rust iterator
        """
        # TODO change Iterator[T] into Iter[T]
        raise NotImplementedError

    def into_iter(self: Vec[T]) -> Iterator[T]:
        """Return a rust iterator
        """
        # TODO change Iterator[T] into IntoIter[T]
        raise NotImplementedError

    def retain(self: Vec[T], predicate: Callable[[T], bool]) -> None:
        """Retains only the elements specified by the predicate."""
        self.__buffer = list(filter(predicate, self.__buffer))

    def drain(self: Vec[T], rng: slice) -> Vec[T]:
        """Removes a range of elements from the vector and returns them in a new vector.

        Note:
            this modifies the original vector.
        """
        self.__buffer = self.__buffer[:rng.start] + self.__buffer[rng.stop:]
        return Vec[self.__type__](self.__buffer[rng])

    def len(self) -> int:
        return len(self)

    def is_empty(self) -> bool:
        return self.len() == 0

    def split_at(self: Vec[T], idx: int) -> Tuple[Vec[T], Vec[T]]:
        """Splits the collection into two at the given index."""
        self.__buffer = self.__buffer[:idx]
        return self, Vec[self.__type__](self.__buffer[idx:])

    def resize(self: Vec[T], len: int, value: T) -> None:
        """Resizes the vector in-place so that len is equal to new_len.

        If new_len is greater than len, the vector is extended by the difference,
        with each additional slot filled with value.
        If new_len is less than len, the vector is simply truncated.
        """
        if len < self.len():
            self.truncate(len)
        else:
            self.__check_value(value)
            self.extend(value for _ in range(self.len(), len))

    def resize_with(self, len: int, func: Callable[[int], T]) -> None:
        """Resizes the vector in-place so that len is equal to new_len.

        If new_len is greater than len, the vector is extended by the difference,
        with each additional slot filled with the result of calling func with its index.
        If new_len is less than len, the vector is simply truncated.
        """
        if len < self.len():
            self.truncate(len)
        else:
            self.extend(func(i) for i in range(self.len(), len))

    def truncate(self, len: int) -> None:
        """Truncates the vector, removing all elements after len."""
        self.__buffer = self.__buffer[:len]

    ###########################################################################
    # Rust safe alternatives to python functions
    ###########################################################################

    def try_get(self: Vec[T], idx: int) -> Option[T]:
        """Return the item at the specified index, or None if it is out of bounds."""
        return Result.from_(lambda: self.__buffer[idx]).ok()

    def try_index(self: Vec[T], value: T) -> Result[..., ValueError]:
        """A safe alternative to index.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.
        """
        try:
            self.__buffer.index(value)
        except ValueError as e:
            return ok(e)

    def try_insert(self: Vec[T], idx: SupportsIndex, value: T) -> Result[..., IndexError]:
        """A safe alternative to insert.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.
        """
        try:
            self.insert(idx, value)
            return ok(value)
        except IndexError as e:
            return err(e)

    def try_pop(self: Vec[T], idx: SupportsIndex = -1) -> Result[..., IndexError]:
        """A safe alternative to pop.
        """
        try:
            return ok(self.pop(idx))
        except IndexError as e:
            return err(e)

    def try_remove(self: Vec[T], value: T) -> Result[..., ValueError]:
        """A safe alternative to remove.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.
        """
        try:
            self.remove(value)
            return ok(value)
        except ValueError as e:
            return err(e)

    def try_delitem(self: Vec[T], key: SupportsIndex | slice) -> Result[..., IndexError]:
        """A safe alternative to delitem.

        Raises:
            TypeError: if the vec is strictly typed and the value is not of the same type as this vec.
        """
        try:
            self.__delitem__(key)
            return ok(...)
        except IndexError as e:
            return err(e)

    ###########################################################################
    # C# Enumerable methods
    ###########################################################################

    def join(
            self: Vec[T],
            inner: Vec[U],
            outer_key_selector: Callable[[T], TKey] = lambda i: i,
            inner_key_selector: Callable[[U], TKey] = lambda i: i,
            result_selector: Callable[[T, T], V] = lambda o, i: (o, i)
    ) -> Vec[V]:
        """Correlates the elements of two sequences based on matching keys.

        Examples:
            >>> a = Vec[int]([1, 2, 3])
            >>> b = Vec[int]([2, 3, 4])
            >>> a.join(b)
            ... Vec[(1, 2), (2, 2), (2, 3), (3, 3), (3, 4)]

            >>> a = Vec[int]([1, 2, 3])
            >>> b = Vec[int]([2, 3, 4])
            >>> a.join(b, result_selector=lambda x, y: x + y)
            >>> assert a == Vec[int]([3, 5, 7])

            >>> a = Vec[int]([1, 2, 3])
            >>> b = Vec[int]([2, 3, 4])
            >>> c = Vec[int]([3, 4, 5])
            >>> a.join(b, result_selector=int.__add__).join(c, result_selector=int.__add__)
            >>> assert a == Vec[int]([6, 9, 12])
        """
        return Vec[V](
            result_selector(i_outer, i_inner)
            for i_outer in self.__buffer
            for i_inner in inner.__buffer
            if outer_key_selector(i_outer) == inner_key_selector(i_inner)
        )

    def select(self: Vec[T], selector: Callable[[T], U]) -> Vec[U]:
        """Projects each element of a sequence into a new form.
        this is basically map.

        Examples:
            >>> a = Vec[int]([1, 2, 3])
            >>> a.select(str)
            ... Vec[str](['2', '3', '4'])
        """
        return Vec[U](map(selector, self.__buffer))

    def where(self: Vec[T], predicate: Callable[[T], bool]) -> Vec[T]:
        """Filters a sequence of values based on a predicate.
        this is basically filter.

        Examples:
            >>> a = Vec[int]([1, 2, 3])
            >>> a.where(lambda x: x > 1)
            ... Vec[int]([2, 3])
        """
        return Vec[T](filter(predicate, self.__buffer))

    @classmethod
    def repeat(cls: Vec[T], value: T, count: int) -> Vec[T]:
        """Generates a sequence that contains one repeated value.

        Args:
            value: The value to be repeated.
            count: The number of times to repeat the value in the generated sequence.
        """
        return cls[cls.__type__]([value for _ in range(count)])

    @classmethod
    def range(cls: Vec[T], start: int, count: int) -> Vec[T]:
        """Generates a sequence of integral numbers within a specified range.
        """
        return cls[cls.__type__](range(start, start + count))
