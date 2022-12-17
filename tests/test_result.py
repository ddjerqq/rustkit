import pytest

from src import *

# test from_
# test ok
# test err

# test is_ok
# test is_ok_and
# test is_err
# test is_err_and

# test map
# test map_or
# test map_or_else
# test map_err
# test inspect
# test inspect_err

# test ok
# test err
# test expect
# test expect_err
# test unwrap
# test unwrap_err
# test unwrap_or
# test unwrap_or_else

# test and_
# test __and__
# test and_then
# test filter
# test or_
# test __or__
# test or_else

# test __eq__
# test __ne__

# test contains
# test __contains__
# test contains_err
# transpose
# flatten

# test __repr__
# test __bool__


def test_from_():
    assert Result.from_(int).is_ok()

    async def good():
        return 1

    assert Result.from_(good).is_ok()
    assert Result.from_(good()).is_ok()

    async def bad():
        raise Exception()

    assert Result.from_(bad).is_err()
    assert Result.from_(bad()).is_err()

    assert Result.from_(lambda: 1/0).is_err()

    assert Result.from_(sum, (1, 2, 3)).is_ok()

    with pytest.raises(TypeError):
        Result.from_(10)  # type: ignore

    with pytest.raises(RuntimeError):
        _ = Result(True, 10)


def test_ok():
    assert ok(10).is_ok()
    assert ok(10).unwrap() == 10


def test_err():
    assert err(10).is_err()
    assert err(10).unwrap_err() == 10



def test_is_ok():
    assert ok(10).is_ok()
    assert not err(10).is_ok()


def test_is_ok_and():
    assert ok(10).is_ok_and(lambda x: x == 10)
    assert not ok(10).is_ok_and(lambda x: x == 11)
    assert not err(10).is_ok_and(lambda x: x == 10)


def test_is_err():
    assert err(10).is_err()
    assert not ok(10).is_err()


def test_is_err_and():
    assert err(10).is_err_and(lambda x: x == 10)
    assert not err(10).is_err_and(lambda x: x == 11)
    assert not ok(10).is_err_and(lambda x: x == 10)



def test_map():
    assert ok(10).map(lambda x: x + 1).unwrap() == 11
    assert err(10).map(lambda x: x + 1).unwrap_err() == 10


def test_map_or():
    assert ok(10).map_or(0, lambda x: x + 1) == 11
    assert err(10).map_or(0, lambda x: x + 1) == 0


def test_map_or_else():
    assert ok(10).map_or_else(int, lambda x: x + 1) == 11
    assert err(10).map_or_else(lambda error_variant: error_variant + 10, lambda x: x + 1) == 20


def test_map_err():
    assert ok(10).map_err(lambda x: x + 1).unwrap() == 10
    assert err(10).map_err(lambda x: x + 1).unwrap_err() == 11


def test_inspect():
    assert ok(10).inspect(lambda x: x + 1).unwrap() == 10
    assert err(10).inspect_err(lambda x: x + 1).unwrap_err() == 10


def test_inspect_err():
    assert ok(10).inspect(lambda x: x + 1).unwrap() == 10
    assert err(10).inspect_err(lambda x: x + 1).unwrap_err() == 10



def test_result_ok():
    assert ok(10).ok() == some(10)
    assert err(10).ok() == none()


def test_result_err():
    assert ok(10).err() == none()
    assert err(10).err() == some(10)


def test_expect():
    assert ok(10).expect("test") == 10

    with pytest.raises(UnwrapError):
        err(10).expect("test")


def test_expect_err():
    assert err(10).expect_err("test") == 10

    with pytest.raises(UnwrapError):
        ok(10).expect_err("test")


def test_unwrap():
    assert ok(10).unwrap() == 10

    with pytest.raises(UnwrapError):
        err(10).unwrap()


def test_unwrap_err():
    assert err(10).unwrap_err() == 10

    with pytest.raises(UnwrapError):
        ok(10).unwrap_err()


def test_unwrap_or():
    assert ok(10).unwrap_or(0) == 10
    assert err(10).unwrap_or(0) == 0


def test_unwrap_or_else():
    assert ok(10).unwrap_or_else(int) == 10
    assert err("10").unwrap_or_else(int) == 10



def test_and_():
    assert ok(10).and_(ok(20)).unwrap() == 20
    assert ok(10).and_(err(20)).unwrap_err() == 20
    assert err(10).and_(ok(20)).unwrap_err() == 10
    assert err(10).and_(err(20)).unwrap_err() == 10


def test___and__():
    assert ok(10) & ok(20) == ok(20)
    assert ok(10) & err(20) == err(20)
    assert err(10) & ok(20) == err(10)
    assert err(10) & err(20) == err(10)


def test_and_then():
    assert ok(10).and_then(ok).unwrap() == 10
    assert ok(10).and_then(err).unwrap_err() == 10
    assert err(10).and_then(ok).unwrap_err() == 10
    assert err(10).and_then(err).unwrap_err() == 10


def test_filter():
    assert ok(10).filter(lambda x: x == 10).unwrap() == 10
    assert ok(10).filter(lambda x: x == 11).is_err()
    assert err(10).filter(lambda x: x == 10).is_err()


def test_or_():
    assert ok(10).or_(ok(20)).unwrap() == 10
    assert ok(10).or_(err(20)).unwrap() == 10
    assert err(10).or_(ok(20)).unwrap() == 20
    assert err(10).or_(err(20)).unwrap_err() == 20


def test___or__():
    assert ok(10) | ok(20) == ok(10)
    assert ok(10) | err(20) == ok(10)
    assert err(10) | ok(20) == ok(20)
    assert err(10) | err(20) == err(20)


def test_or_else():
    assert ok(10).or_else(ok).unwrap() == 10
    assert ok(10).or_else(err).unwrap() == 10
    assert err(10).or_else(ok).unwrap() == 10
    assert err(10).or_else(err).unwrap_err() == 10


def test___eq__():
    assert ok(10) == ok(10)
    assert err(10) == err(10)

    with pytest.raises(TypeError):
        assert ok(10) == 10


def test___ne__():
    assert ok(10) != ok(11)
    assert err(10) != err(11)
    assert ok(10) != err(10)
    assert err(10) != ok(10)

    with pytest.raises(TypeError):
        assert ok(10) != 10



def test_contains():
    assert ok(10).contains(10)
    assert not err(10).contains(10)


def test___contains__():
    assert 10 in ok(10)
    assert 10 in err(10)


def test_contains_err():
    assert err(10).contains_err(10)
    assert not ok(10).contains_err(10)


def test_transpose():
    assert ok(some(2)).transpose() == some(ok(2))
    assert ok(none()).transpose() == none()
    assert err(some(10)).transpose() == some(err(10))
    assert err(none()).transpose() == none()

    with pytest.raises(TypeError):
        err(10).transpose()


def test_flatten():
    assert ok(ok(10)).flatten().unwrap() == 10
    assert ok(err(10)).flatten().unwrap_err() == 10
    assert err(10).flatten().unwrap_err() == 10



def test___repr__():
    assert repr(ok(10)) == "<Ok(10)>"
    assert repr(err(10)) == "<Err(10)>"


def test___bool__():
    assert bool(ok(10))
    assert not bool(err(10))
