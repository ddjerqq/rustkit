# Rustkit - A Python library for Rust lovers.

> Rustkit is a Python library for Rust lovers. It provides a set of tools to write
Rust-like code in Python. It's written by a fellow rustacean, who also loves Python.
In my opinion, Python is a great language, but it lacks some features that Rust
has. Rustkit is an attempt to bring some of those features to Python.


# Roadmap

#### as of now, only the following features are implemented:

- [x] Result
- [x] Option

#### with these features on their way in a future release:

- [ ] Vector
- [ ] Iterators


## Installation

```bash
pip install rustkit
```


## Usage

```python
from rustkit import *

# Rust-like optionals
assert some(10).unwrap() == 10
assert some(10).unwrap_or(20) == 10
assert Option.from_(None) == NONE

# Rust-like results, and error handlers
assert ok(10).unwrap() == 10
assert ok(10).unwrap_or(20) == 10
assert Result.from_(lambda: 10 / 0) == err(ZeroDivisionError)
```