import pytest
import euler.euler_day_02 as e
from euler.euler_day_02 import Digits


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    e.g_sequence(45)


def test_digits_gen_2():
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
    for i in range(30):
        assert str(Digits(i)) == str(i)


def test_digits_next():
    print(e.PREFIXES[1])
    print(e.PREFIXES[2])
    d = Digits(1)
    last = d.value
    for i in range(2, 1000):
        i_str = str(i)
        i_sorted = ''.join(sorted(i_str))
        if i_str == i_sorted and i != 11:
            value = d.next().value
            print('Show: ', last, i_str, value)
            assert value == i
            last = value
        else:
            print(i, 'skipped', i_str, i_sorted)

    assert False




