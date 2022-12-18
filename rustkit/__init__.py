"""
# Rustkit - A Python library for Rust lovers.

Rustkit is a Python library for Rust lovers. It provides a set of tools to write
Rust-like code in Python. It's written by a fellow rustacean, who also loves Python.

In my opinion, Python is a great language, but it lacks some features that Rust
has. Rustkit is an attempt to bring some of those features to Python.

Example usage:
    >>> from rustkit import *

    >>> # Rust-like optionals
    >>> assert some(10).unwrap() == 10
    >>> assert some(10).unwrap_or(20) == 10
    >>> assert Option.from_(None) == none()

    >>> # Rust-like results, and error handlers
    >>> assert ok(10).unwrap() == 10
    >>> assert ok(10).unwrap_or(20) == 10
    >>> assert Result.from_(lambda: 10 / 0) == err(ZeroDivisionError)

as of now, only the following features are implemented:
[X] Result
[X] Option
[ ] Vector
[ ] Iterators
"""

from .error import UnwrapError
from .option import Option, some, none
from .result import Result, ok, err


__all__ = (
    "UnwrapError",
    "Option",
    "some",
    "none",
    "Result",
    "ok",
    "err",
)

__version__ = 0, 0, 2
