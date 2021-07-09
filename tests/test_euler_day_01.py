import pytest
import euler.euler_day_01 as e
from euler.euler_day_01 import Digits


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    e.g_sequence(45)


def test_digits_gen():
    assert list(e.digits_gen(0)) == [0]
    assert list(e.digits_gen(10)) == [0, 1]
    assert list(e.digits_gen(342)) == [2, 4, 3]
    # check list representation
    for i in range(10):
        assert list(e.digits_gen(i)) == Digits(i).num
    for i in range(10):
        assert list(e.digits_gen(i)) == list(Digits(i).digits_gen())
    # check number representation
    for i in range(10):
        assert Digits(i).value == i
    # check string representation
    for i in range(10):
        assert str(Digits(i)) == str(i)
    assert Digits(1).next().value == 2
    assert Digits(2).next().value == 3
    assert Digits(9).next().value == 11
    assert Digits(10).next().value == 11
    assert Digits(11).next().value == 12
    assert Digits(12).next().value == 13
    assert Digits(19).next().value == 22
    assert Digits(29).next().value == 33
    assert Digits(39).next().value == 44
    assert Digits(49).next().value == 55
    assert Digits(89).next().value == 99
    assert Digits(99).next().value == 111



def test_digits_f():
    assert e.f(Digits(342)) == e.f(342) == 32
    assert e.f(Digits(5)) == 120
    assert e.f(Digits(25)) == 122

