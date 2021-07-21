import euler.euler_00_naive as e
from euler.euler_00_naive import sg


def test_f():
    assert e.f(342) == 32
    assert e.f(5) == 120
    assert e.f(25) == 122


def test_sf():
    assert e.sf(342) == 5
    assert e.sf(5) == 3
    assert e.sf(25) == 5


def test_g():
    assert e.g(1) == 1
    assert e.g(2) == 2
    assert e.g(3) == 5
    assert e.g(4) == 15
    assert e.g(5) == 25
    assert e.g(20) == 267


def test_sg():
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



def test_sum_sg():
    assert e.sum_sg(5) == 21
    assert e.sum_sg(10) == 46
    assert e.sum_sg(20) == 156
    assert e.sum_sg(40) == 468
