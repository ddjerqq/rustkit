import pytest

from src import *

# test from_
# test some
# test none

# test is_some
# test is_some_and
# test is_none

# test expect
# test unwrap
# test unwrap_or
# test unwrap_or_else

# test map
# test inspect
# test map_or
# test map_or_else
# test ok_or
# test ok_or_else

# test and_
# test __and__
# test and_then
# test filter
# test or_
# test __or__
# test or_else
# test xor
# test __xor__

# test __eq__
# test __ne__

# test insert
# test get_or_insert
# test get_or_insert_with

# test take
# test replace
# test contains
# test __contains__
# test zip
# test zip_with
# test transpose
# test flatten

# test __repr__
# test __bool__


def test_from_():
    assert Option.from_(None) == none()
    assert Option.from_(1) == some(1)

    with pytest.raises(RuntimeError):
        Option(1)


def test_some():
    assert Option.some(1) == some(1)


def test_none():
    assert Option.none() == none()
    assert Option.none() == none()
    assert Option.none() == None



def test_is_some():
    assert some(1).is_some()
    assert not none().is_some()


def test_is_some_and():
    assert some(1).is_some_and((1).__eq__)
    assert not some(1).is_some_and((2).__eq__)
    assert not none().is_some_and((1).__eq__)


def test_is_none():
    assert some(1).is_none() is False
    assert none().is_none() is True


def test_expect():
    assert some(1).expect("error") == 1

    with pytest.raises(UnwrapError):
        none().expect('error')


def test_unwrap():
    assert some(1).unwrap() == 1

    with pytest.raises(UnwrapError):
        none().unwrap()


def test_unwrap_or():
    assert some(1).unwrap_or(2) == 1
    assert none().unwrap_or(2) == 2


def test_unwrap_or_else():
    assert some(1).unwrap_or_else(lambda: 2) == 1
    assert none().unwrap_or_else(lambda: 2) == 2



def test_map():
    assert some(1).map(lambda x: x + 1) == some(2)
    assert none().map(lambda x: x + 1) == none()


def test_inspect():
    assert some(1).inspect(lambda x: x + 1) == some(1)
    assert none().inspect(lambda x: x + 1) == none()


def test_map_or():
    assert some(1).map_or(2, lambda x: x + 1) == 2
    assert none().map_or(2, lambda x: x + 1) == 2


def test_map_or_else():
    assert some(1).map_or_else(lambda: 2, lambda x: x + 1) == 2
    assert none().map_or_else(lambda: 2, lambda x: x + 1) == 2


def test_ok_or():
    assert some(1).ok_or(2) == ok(1)
    assert none().ok_or(2) == err(2)


def test_ok_or_else():
    assert some(1).ok_or_else(int) == ok(1)
    assert none().ok_or_else(int) == err(0)



def test_and_():
    assert some(1).and_(some(2)) == some(2)
    assert some(1).and_(none()) == none()
    assert none().and_(some(2)) == none()
    assert none().and_(none()) == none()


def test___and__():
    assert some(1) & some(2) == some(2)
    assert some(1) & none() == none()
    assert none() & some(2) == none()
    assert none() & none() == none()


def test_and_then():
    assert some(1).and_then(lambda x: some(x + 1)) == some(2)
    assert some(1).and_then(lambda x: none()) == none()
    assert none().and_then(lambda x: some(x + 1)) == none()
    assert none().and_then(lambda x: none()) == none()


def test_filter():
    assert some(1).filter((1).__eq__) == some(1)
    assert some(1).filter((2).__eq__) == none()
    assert none().filter((1).__eq__) == none()
    assert none().filter((2).__eq__) == none()


def test_or_():
    assert some(1).or_(some(2)) == some(1)
    assert some(1).or_(none()) == some(1)
    assert none().or_(some(2)) == some(2)
    assert none().or_(none()) == none()


def test___or__():
    assert some(1) | some(2) == some(1)
    assert some(1) | none() == some(1)
    assert none() | some(2) == some(2)
    assert none() | none() == none()


def test_or_else():
    assert some(1).or_else(lambda: some(2)) == some(1)
    assert some(1).or_else(lambda: none()) == some(1)
    assert none().or_else(lambda: some(2)) == some(2)
    assert none().or_else(lambda: none()) == none()


def test_xor():
    assert some(1).xor(some(2)) == none()
    assert some(1).xor(none()) == some(1)
    assert none().xor(some(2)) == some(2)
    assert none().xor(none()) == none()


def test___xor__():
    assert some(1) ^ some(2) == none()
    assert some(1) ^ none() == some(1)
    assert none() ^ some(2) == some(2)
    assert none() ^ none() == none()



def test___eq__():
    assert Option.some(1) == some(1)
    assert none() == none()

    with pytest.raises(TypeError):
        _ = Option.some(1) == 1


def test___ne__():
    assert none() != some(1)
    assert some(1) != none()
    assert some(1) != some(2)

    with pytest.raises(TypeError):
        _ = Option.some(1) != 1



def test_insert():
    assert some(1).insert(2) == 2
    assert none().insert(2) == 2


def test_get_or_insert():
    assert some(1).get_or_insert(2) == 1
    assert none().get_or_insert(2) == 2


def test_get_or_insert_with():
    assert some(1).get_or_insert_with(int) == 1
    assert none().get_or_insert_with(int) == 0



def test_take():
    assert some(1).take() == some(1)
    assert none().take() == none()


def test_replace():
    x = some(1)
    assert x.replace(2) == some(1)
    assert x == some(2)

    y = none()
    assert y.replace(2) == none()
    assert y == some(2)


def test_contains():
    assert some(1).contains(1)
    assert not some(1).contains(2)
    assert not none().contains(1)
    assert not none().contains(2)


def test___contains__():
    assert 1 in some(1)
    assert 2 not in some(1)
    assert 1 not in none()
    assert 2 not in none()


def test_zip():
    assert some(1).zip(some(2)) == some((1, 2))
    assert some(1).zip(none()) == none()
    assert none().zip(some(2)) == none()
    assert none().zip(none()) == none()


def test_zip_with():
    assert some(1).zip_with(some(2), lambda x, y: x + y) == some(3)
    assert some(1).zip_with(none(), lambda x, y: x + y) == none()
    assert none().zip_with(some(2), lambda x, y: x + y) == none()
    assert none().zip_with(none(), lambda x, y: x + y) == none()


def test_transpose():
    assert some(ok(1)).transpose() == ok(some(1))
    assert some(err(1)).transpose() == err(1)  # type: ignore

    assert none().transpose() == ok(none())

    with pytest.raises(TypeError):
        _ = some(1).transpose()


def test_flatten():
    assert some(some(1)).flatten() == some(1)
    assert some(none()).flatten() == none()
    assert none().flatten() == none()



def test___repr__():
    assert repr(some(1)) == "<Option(1)>"
    assert repr(some(some(1))) == "<Option(<Option(1)>)>"
    assert repr(none()) == "<Option(None)>"


def test___bool__():
    assert bool(some(1))
    assert not bool(none())
