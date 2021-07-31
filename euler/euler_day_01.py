"""
Euler challenge from HackerRank https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem

Simple optimizations - Day 1

"""
import math
import time
from functools import reduce

DEBUG = False
FACTORIALS = [math.factorial(i) for i in range(10)]
sf_cache = {}

def digits_gen(n):
    """
    Yields number n digits in reverse sequence. For n = 342 sequence is 2, 4, 3.
    :param n:
    :return:
    """
    while True:
        yield n % 10
        n //= 10
        if not n:
            break


def digits_sum(n):
    """
    Returns sum of digits of number n.
    For example:
        digits_sum(245) = 2 + 4 + 5
    :param n: n
    :return: sum of digits
    """
    return sum(int(ch) for ch in str(n))


class Digits:
    """
    Class implements number as reverse order list of decimal digits.
    """
    def __init__(self, number):
        self.num = [int(ch) for ch in str(number)[::-1]]

    def __str__(self):
        """ Return number value as str. """
        return ''.join(str(d) for d in self.num[::-1])

    def __int__(self):
        """ Return number value as int. """
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def next(self, start_digit=0):
        """ Return next number being candidate for g(i) result. """
        def set_after_carry_on(k):
            """ Set digits after carry on 1.
            Instead of  0 fill with updated digit
            Eg. 2999 + 1 is 3333 not 3000
            """
            filler = self.num[k]
            for ii in range(k-1, start_digit - 1, -1):
                self.num[ii] = filler

        ndx = start_digit
        while True:
            if self.num[ndx] < 9:
                # Non 9 digit so increase it
                self.num[ndx] += 1
                # Set all less significant digits to the same value as digits are in non-decrease order
                set_after_carry_on(ndx)
                return
            elif ndx < len(self.num) - 1:
                # Digit 9, but not the highest one,  then go to next digit
                self.num[ndx] = 0
                ndx += 1
            else:
                # if all digits are 9, then add 1 as the next digit
                self.num.append(1)
                self.num[ndx] = 0
                set_after_carry_on(ndx+1)
                return


def f(n):
    """
    Define f(n) as the sum of the factorials of the digits of n.
    For example:
        f(342) = 3! + 4! + 2! = 32
    :param n: number
    :return: sum digits factorial of n
    """
    if isinstance(n, Digits):
        return sum(FACTORIALS[d] for d in n.num)
    else:
        return sum(FACTORIALS[d] for d in digits_gen(int(n)))


def sf(n):
    """
    Compute sf(n) as the sum of the digits of f(n).
    Store in sf_cache the value n for which the reached the first time key sf(n)
    So:
    sf(144) = 4 + 9 = 13 as f(144) is 1!+4!+4! = 49
    For n = 144 is minimum n such that sf(n) = 13 so sf_cache[13] = 144
    :param n: number
    :return: sum digits of f(n)
    """

    sf_ = digits_sum(f(n))
    sf_cache.setdefault(sf_, str(n))
    return sf_


def g(i):
    """
    Define g(i) to be the smallest positive integer n such that sf(n) == i.
    sf(342) = 5, also sf(25) = 5 and 25 is the smallest number giving sf(i) = 5, so g(5) = 25
    Using cached value. g_sequence with parameter not less than i must be called earlier
    :param i: number
    :return: smallest n such that sf(n) == i
    """
    if sf_cache.get(i) is None:
        g_sequence(i)
    return int(sf_cache[i])


def g_sequence(max_i):
    """
    Looks for g(i) in range 1..max_i
    Define g(i) to be the smallest positive integer n such that sf(n) == i.
    Results are in a global cached dictionary
    sf(342) = 5, also sf(25) = 5 and 25 is the smallest number giving sf(i) = 5, so g(5) = 25
    :param max_i: range for compute g(i) from 1 to max_i
    :return: None
    """
    n = Digits(1)
    for i in range(1, max_i + 1):
        if not sf_cache.get(i):
            start_time = time.perf_counter()
            while sf(n) != i:
                n.next()
            stop_time = time.perf_counter()
            if DEBUG:
                print(
                    f"For n = {str(n):40} sf(n) = {i:2}. "
                    f"sg({i:2}) = {digits_sum(n):2}. "
                    f"Time: {stop_time-start_time:8.4f} seconds"
                )
        else:
            if DEBUG:
                print(
                    f"For n = {sf_cache[i]:40} sf(n) = {i:2}. "
                    f"sg({i:2}) = {digits_sum(sf_cache[i]):2}. "
                    f"Time: Computed in earlier step"
                )
    return


def sg(i):
    """
    Define  sg(i) as the sum of the digits of g(i).
    So sg(5) = 2 + 5 = 7 as g(5) = 25.
    :param i:
    :return: sum digits of g(i)
    """
    return digits_sum(sf_cache[i])


def sum_sg(n, m=None):
    """
    Define sum_sg as sum sg in range 1 to n modulo m.
    :param n:
    :param m: if present - result modulo m
    :return:
    """
    g_sequence(n)
    sum_sg_ = sum([sg(i) for i in range(1, n + 1)])
    if m:
        sum_sg_ %= m
    return sum_sg_


if __name__ == "__main__":
    DEBUG = True
    pgm_start = time.perf_counter()
    nn = 60
    total = sum_sg(nn)
    pgm_stop = time.perf_counter()
    print(f"sum_sg({nn}) is {total} computed in {pgm_stop-pgm_start:.2f} seconds")

    """

    """
