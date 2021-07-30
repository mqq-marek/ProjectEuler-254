import pytest
import euler.euler_day_03 as e
from euler.euler_day_03 import FDigits, sg


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    e.init_prefixes()
    e.g_sequence(55)


def test_digits_gen_3():
    assert list(e.digits_gen(0)) == [0]
    assert list(e.digits_gen(10)) == [0, 1]
    assert list(e.digits_gen(342)) == [2, 4, 3]
    # check list representation
    for i in range(10):
        assert list(e.digits_gen(i*e.FACTORIALS[9])) == FDigits(i).num
    for i in range(10):
        assert list(e.digits_gen(i*e.FACTORIALS[9])) == list(FDigits(i).digits_gen())
    # check number representation
    for i in range(10):
        assert FDigits(i).value == i * e.FACTORIALS[9]
    # check string representation
    for i in range(30):
        assert str(FDigits(i)) == str(i * e.FACTORIALS[9])


def test_digits_next():
    d = FDigits(0)
    for i in range(10):
        print(f'n={d.n}, value={d.value}')
        d.next()
    for i in range(1, 71):
        print(i, e.sg(i))
    assert False

def test_sg_3():
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
    assert sg(45) == 46
    assert sg(46) == 50
    assert sg(47) == 66
    assert sg(48) == 67
    assert sg(49) == 71
    assert sg(50) == 84
    assert sg(51) == 89
    assert sg(52) == 90
    assert sg(53) == 114
    assert sg(54) == 118




