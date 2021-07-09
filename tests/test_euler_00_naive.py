import euler.euler_00_naive as e


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
    assert e.sg(1) == 1
    assert e.sg(2) == 2
    assert e.sg(3) == 5
    assert e.sg(4) == 6
    assert e.sg(5) == 7
    assert e.sg(10) == 7
    assert e.sg(20) == 15
    assert e.sg(40) == 25


def test_sum_sg():
    assert e.sum_sg(5) == 21
    assert e.sum_sg(10) == 46
    assert e.sum_sg(20) == 156
    assert e.sum_sg(40) == 468
