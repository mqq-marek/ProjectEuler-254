"""
Euler challenge from HackerRank https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem

Speed improvement in f(n) guessing - Day 3

"""
import cProfile, pstats, io
import math
import time
from collections import defaultdict, namedtuple
from functools import reduce
from itertools import combinations

DEBUG = False
g_cache = {}
sg_cache = {}
PREFIX = {}


def init_prefixes():
    for i1 in range(2):
        for i2 in range(3):
            for i3 in range(4):
                for i4 in range(5):
                    for i5 in range(6):
                        for i6 in range(7):
                            for i7 in range(8):
                                for i8 in range(9):
                                    i = i1 + i2 + i3 + i4 + i5 + i6 + i7 + i8
                                    if i:
                                        prefix = ('1' * i1 + '2' * i2 + '3' * i3 + '4' * i4 +
                                                  '5' * i5 + '6' * i6 + '7' * i7 + '8' * i8)
                                        f_ = f(prefix)
                                        PREFIX[f_] = prefix
    PREFIX[0] = ''


FACTORIALS = [math.factorial(i) for i in range(10)]


def digits_gen(n):
    """
    Yields number n digits in reverse sequence. For n = 342 sequence is 2, 4, 3
    :param n:
    :return:
    """
    while True:
        yield n % 10
        n //= 10
        if not n:
            break


def digits_sum(n):
    if isinstance(n, int):
        return sum([d for d in digits_gen(n)])
    elif isinstance(n, str):
        return sum([ord(d) - ord('0') for d in n])
    else:
        return sum([d for d in n.digits_gen()])


def get_suffix_value(number):
    """ Return list representation of number * 9!. """
    return list(digits_gen(number * FACTORIALS[9]))

N_Number = namedtuple("N_Number", "prefix suffix_len")


def reverse_f(f_value):
    suffix_len, f_prefix = divmod(f_value, FACTORIALS[9])
    prefix = PREFIX[f_prefix]
    return N_Number(prefix, suffix_len)

def smaller_n(n1, n2):
    p1, s1 = n1
    p2, s2 = n2
    p1l = len(str(p1)) + s1
    p2l = len(str(p2)) + s2
    if p1l < p2l:
        return n1
    elif p1l > p2l:
        return n2
    p1 = p1.ljust(36, '9')
    p2 = p2.ljust(36, '9')
    if p1 <= p2:
        return n1
    else:
        return n2


def build_first_number_with(digits_sum):
    """
    Build the smallest number with given sum of digits
    :param digits_sum: 
    :return: list of digits in reverse order
    for digits sum 20 returns: [9, 9, 2], 
    for digits_sum 45 returns : [9, 9, 9, 9, 9]
    """
    n9, d = divmod(digits_sum, 9)
    result = [9] * n9
    if d != 0:
        result += [d]
    return result


class FDigits:
    """
    Iterator class - gives increase sequence of numbers with given sum
    """
    def __init__(self, sum_digits):
        self.sum = sum_digits
        self.initialized = True
        self.cost = 0
        self.num = build_first_number_with(self.sum)

    def __str__(self):
        """ Return number value as str. """
        return ''.join([chr(d + ord('0')) for d in self.num[::-1]])

    def __iter__(self):
        """ Returns itself as an iterator object. """
        return self

    def __next__(self):
        """
        Returns the next number with digits sum equals self.sum.
        """
        if self.initialized:
            # First time do nothing as number is initialized to the lowest one during __init__
            self.initialized = False
        else:
            self.next_number()
        return self

    @property
    def value(self):
        """ Return number value as int """
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def digits_sum(self):
        """
        Sum of all digits.
        """
        return sum(self.num)

    def next_number(self):
        """
        Finds next value with self.sum digits sum
        """

        def increase_digit(need, digit):
            """
            Increase digit by amount needed. Return missing amount and increased digit
            :param need: amount of sum digits needed
            :param digit: current digit value
            :return: missing_amount, increased_digit
            """
            inc = min(need, 9 - digit)
            return need - inc, digit + inc

        def update_value(inc_sum):
            for i in range(len(self.num)):
                inc_sum, self.num[i] = increase_digit(inc_sum, self.num[i])
                if inc_sum == 0:
                    return 0
            return inc_sum

        def get_value_with_sum(needed):
            still_needed = needed - self.digits_sum()
            while still_needed:
                still_needed = update_value(still_needed)
                self.cost += 1
                # If not finished in one update_value call, it means that we need to increase number length
                if still_needed:
                    for i in range(len(self.num)):
                        self.num[i] = 0
                    self.num.append(1)
                    still_needed = needed - 1

        # Get next f_value with self.sum
        self.cost = 0
        next_value = self.value + 1
        # skip all numbers with sum of digits greater than required
        while digits_sum(next_value) > self.sum:
            next_value += 1
            self.cost += 1
        self.num = list(digits_gen(next_value))
        # increase number until we get number with required digits sum
        get_value_with_sum(self.sum)


def f(n):
    """
    Define f(n) as the sum of the factorials of the digits of n.
    For example:
        f(342) = 3! + 4! + 2! = 32
    :param n: number
    :return: sum digits factorial of n
    """
    if isinstance(n, str):
        n = int(n)
    if isinstance(n, int):
        return sum([FACTORIALS[d] for d in digits_gen(n)])
    elif isinstance(n, list):
        return sum([FACTORIALS[d] for d in n])
    else:
        return sum([FACTORIALS[d] for d in n.digits_gen()])


def prefix_lt_prefix(prefix1, prefix2):
    p1 = str(prefix1)
    p2 = str(prefix2)
    p_len = max(len(p1), len(p2))
    return p1.ljust(p_len, '9') < p2.ljust(p_len, '9')


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
    return sf_


def g(i):
    """
    Define g(i) to be the smallest positive integer n such that sf(n) == i.
    sf(342) = 5, also sf(25) = 5 and 25 is the smallest number giving sf(i) = 5, so g(5) = 25
    Using cached value. g_sequence with parameter not less than i must be called earlier
    :param i: number
    :return: smallest n such that sf(n) == i
    """
    if sg_cache.get(i) is None:
        g_sequence(i)
    return int(sg_cache[i])


def g_sequence(max_i, *, mod=None):
    """
    Looks for g(i) in range 1..max_i
    Define g(i) to be the smallest positive integer n such that sf(n) == i.
    sf(342) = 5, also sf(25) = 5 and 25 is the smallest number giving sf(i) = 5, so g(5) = 25
    As n start be huge numbers - million and more digits we store in cache sg(n) which is digits sum of n
    Results are in a global cached dictionary
    :param max_i: range for compute g(i) from 1 to max_i
    :return: None
    """

    for i in range(1, max_i + 1):
        if sg_cache.get(i):
            continue
        equal_sum_numbers = FDigits(i)
        first_value = next(equal_sum_numbers).value
        cost = equal_sum_numbers.cost
        best_n = reverse_f(first_value)
        best_f = first_value
        for number in equal_sum_numbers:
            cost += number.cost
            n = reverse_f(number.value)
            best_n = smaller_n(best_n, n)
            if best_n == n:
                best_f = number.value
            # print(f'Best value is {best_n.prefix} {best_n.suffix_len}')
            if n.suffix_len >= best_n.suffix_len + len(best_n.prefix):
                break
        if DEBUG:
            l_str = str(len(str(best_n.prefix)) + best_n.suffix_len)
            if len(l_str) > 19:
                l_str = '...'+l_str[-16:]
            prefix = ''
            if best_n.prefix:
                prefix = best_n.prefix + '+'
            print(
                f'cost: {cost:12}, len={l_str:21}, f(n) = {best_f:40}, '
                f'g({i}) = {prefix}9*{best_n.suffix_len}')
        sg_cache[i] = digits_sum(best_n.prefix) + 9 * best_n.suffix_len
        if mod:
            sg_cache[i] = sg_cache[i] % mod
        g_cache[i] = best_n
    return


def sg(i):
    """
    Define  sg(i) as the sum of the digits of g(i).
    So sg(5) = 2 + 5 = 7 as g(5) = 25.
    :param i:
    :return: sum digits of g(i)
    """
    if sg_cache.get(i) is None:
        g_sequence(i)
    return int(sg_cache[i])


def sum_sg_mod(n, m):
    g_sequence(n, mod=m)
    s = 0
    for i in range(1, n + 1):
        s = (s + sg(i)) % m
    return s


def sum_sg(n):
    g_sequence(n)
    return sum([sg(i) for i in range(1, n + 1)])


def assert_sg():
    sg_table = [1, 2, 5, 6, 7, 3, 4, 5, 6, 7, 8, 8, 9, 13, 9, 10, 11, 13, 14, 15, 16, 17, 18, 13, 14, 15, 9, 10, 11, 12,
                13, 14, 12, 13, 14, 15, 19, 28, 24, 25, 37, 31, 32, 45, 46, 50, 66, 67, 71, 84, 89, 90, 114, 118, 134,
                154, 158, 193, 231, 235, 247, 317, 321, 545, 843, 1052, 1339, 1574, 1846, 2035, 2294, 2566, 5035, 7578,
                9997, 12529, 15009, 17415, 19912, 22416, 24933, 49686, 74498, 99334, 124135, 148899, 173672, 198536,
                223324, 248145, 496173, 744212, 992162, 1240190, 1488229, 1736179, 1984255, 2232318, 2480268, 4960419,
                7440581, 9920765, 12400916, 14881015, 17361186, 19841385, 22321571, 24801707, 49603317, 74404903,
                99206450, 124008025, 148809646, 173611193, 198412768, 223214413, 248015925, 496031816, 744047718,
                992063594, 1240079422, 1488095324, 1736111200, 1984127056, 2232142919, 2480158795, 4960317556,
                7440476328, 9920635039, 12400793737, 14880952509, 17361111207, 19841269933, 22321428666, 24801587412,
                49603174707, 74404761998, 99206349313, 124007936656, 148809523899, 173611111214, 198412698494,
                223214285824, 248015873187, 496031746194, 744047619212, 992063492204, 1240079365211, 1488095238229,
                1736111111221, 1984126984276, 2232142857318, 2480158730310, 4960317460440, 7440476190581, 9920634920744,
                12400793650874, 14880952381015, 17361111111165, 19841269841406, 22321428571571, 24801587301686,
                49603174603275, 74404761904903, 99206349206429, 124007936508046, 148809523809646, 173611111111172,
                198412698412789, 223214285714413, 248015873015967, 496031746031837, 744047619047718, 992063492063573,
                1240079365079443, 1488095238095324, 1736111111111179, 1984126984127014, 2232142857142919,
                2480158730158837, 4960317460317577, 7440476190476328, 9920634920635018, 12400793650793758,
                14880952380952509, 17361111111111186, 19841269841269891, 22321428571428666, 24801587301587391,
                49603174603174665, 74404761904761998, 99206349206349292, 124007936507936614, 148809523809523899,
                173611111111111193, 198412698412698515, 223214285714285824, 248015873015873166, 496031746031746152,
                744047619047619212]

    for i, sg_sum in enumerate(sg_table, 1):
        if sg_cache.get(i) and sg_cache.get(i) != sg_sum:
            print(f'Assertion error sg({i}) is {sg_cache.get(i, 0)} while expected {sg_sum}')


def assert_gen():
    assert_list = []
    for i in range(1, 1000):
        if sg_cache.get(i):
            assert_list.append(sg_cache[i])
        else:
            break
    print(f'sg_table = {assert_list}')


def hacker_main():
    init_prefixes()
    q = int(input())
    for _ in range(q):
        n, m = map(int, input().split())
        r = sum_sg_mod(n, m)
        print(r)


def profile_main(size=200):
    with cProfile.Profile() as pr:
        init_prefixes()
        sum_sg(size)

    s = io.StringIO()
    sort_by = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.print_stats()
    print(s.getvalue())


def development_main(size=200):
    pgm_start = time.perf_counter()
    init_prefixes()
    print(FACTORIALS)
    pgm_stop = time.perf_counter()
    print(f"Init prefixes - {pgm_stop - pgm_start:.2f} seconds")
    total = sum_sg(size)
    pgm_stop = time.perf_counter()
    print(f"sum_sg({size}) is {total} computed in {pgm_stop - pgm_start:.2f} seconds")
    assert_sg()
    # print computed sg values
    # sg_list = [sg(i) for i in range(1, size+1)]
    # print(sg_list)


if __name__ == "__main__":
    # DEBUG = True
    # hacker_main()
    # profile_main(100)
    development_main(200)
    # assert_gen()
    exit()

"""

"""
