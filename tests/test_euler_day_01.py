import pytest
import euler.euler_day_01 as e
from euler.euler_day_01 import Digits, sg


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    e.g_sequence(45)


def test_digits_d1_gen():
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



def test_digits_d1_f():
    assert e.f(Digits(342)) == e.f(342) == 32
    assert e.f(Digits(5)) == 120
    assert e.f(Digits(25)) == 122

def test_d1_sg():
    assert sg(1) == 1
    assert sg(2) == 2
    assert sg(3) == 5
    assert sg(4) == 6
    assert sg(5) == 7
    assert sg(6) == 3
    assert sg(7) == 4
    assert sg(8) == 5
    assert sg(9) == 6
    assert sg(10) == 7
    assert sg(11) == 8
    assert sg(12) == 8
    assert sg(13) == 9
    assert sg(14) == 13
    assert sg(15) == 9
    assert sg(16) == 10
    assert sg(17) == 11
    assert sg(18) == 13
    assert sg(19) == 14
    assert sg(20) == 15
    assert sg(21) == 16
    assert sg(22) == 17
    assert sg(23) == 18
    assert sg(24) == 13
    assert sg(25) == 14
    assert sg(26) == 15
    assert sg(27) == 9
    assert sg(28) == 10
    assert sg(29) == 11
    assert sg(30) == 12
    assert sg(31) == 13
    assert sg(32) == 14
    assert sg(33) == 12
    assert sg(34) == 13
    assert sg(35) == 14
    assert sg(36) == 15
    assert sg(37) == 19
    assert sg(38) == 28
    assert sg(39) == 24
    assert sg(40) == 25
    assert sg(41) == 37
    assert sg(42) == 31
    assert sg(43) == 32
    assert sg(44) == 45


