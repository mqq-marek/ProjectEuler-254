"""
Euler challenge from HackerRank https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem

Speed improvement in f(n) guessing - Day 3

"""
import cProfile, pstats, io
import math
import time
from collections import defaultdict
from functools import reduce
from itertools import combinations

DEBUG = False

PREFIXES = defaultdict(list)
F_PREFIX = {}
# f_cache = {}
# sf_cache = {}
# g_cache = {}
sg_cache = {}


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
                                    if not i:
                                        continue
                                    prefix = ('1' * i1 + '2' * i2 + '3' * i3 + '4' * i4 +
                                              '5' * i5 + '6' * i6 + '7' * i7 + '8' * i8)
                                    f_ = f(prefix)
                                    fs_ = sf(prefix)
                                    F_PREFIX[prefix] = f_
                                    PREFIXES[fs_ % 9].append(prefix)
    for k in PREFIXES.keys():
        PREFIXES[k].sort(key=lambda x: int(x))


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


def get_new_suffix_value(number):
    """ Return list representation of number * 9!. """
    return list(digits_gen(number * FACTORIALS[9]))


class FDigits:
    def __init__(self, number):
        if isinstance(number, str):
            if not number:
                number = '0'
            number = int(number)
        if isinstance(number, int):
            self.n = number
            self.num = get_new_suffix_value(number)
        else:
            self.num = number.num[:]
            self.n = number.n
        self.sum = self.suffix_digits_sum()

    def __str__(self):
        """ Return number value as str """
        return ''.join([chr(d + ord('0')) for d in self.num[::-1]])

    @property
    def value(self):
        """ Return number value as int """
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def digits_sum(self):
        """
        Sum of all digits.
        """
        return sum(self.num)

    def suffix_digits_sum(self):
        """
        Sum of suffix only digits in  n.
        Does not include 5 least significant digits and max 7 on the 6th least significant digits.
        :return:
        """
        suffix_sum = min(7, sum(self.num[5:6]))
        suffix_sum += sum(self.num[6:])
        return suffix_sum

    def next(self, sum_needed):
        """
        Finds next suffix with the same or greater suffix_digit_sum
        """

        def increase_digit(need, digit, *, max_digit=9):
            """
            Increase digit by amount needed. Return Missing amount and increased digit
            :param need: amount of sum digits needed
            :param digit: current digit value
            :param max_digit: maximum digit value
            :return: missing_amount, increased_digit
            """
            inc = min(need, max_digit - digit)
            return need - inc, digit + inc

        def update_value(inc_sum):
            # inc_sum = max(0, self.sum - self.suffix_digits_sum())
            # try to increase digit po position 5 up to 7
            inc_sum, self.num[5] = increase_digit(inc_sum, self.num[5], max_digit=7)
            for i in range(6, len(self.num)):
                inc_sum, self.num[i] = increase_digit(inc_sum, self.num[i])
                if inc_sum == 0:
                    return 0
            return inc_sum

        def next_value_with_sum(needed):
            still_needed = needed - self.suffix_digits_sum()
            while still_needed > 0:
                old_needed = still_needed
                still_needed = update_value(still_needed)
                # print(f'Needed: {old_needed} gives: {self.value} missing: {still_needed}')
                if still_needed:
                    self.num.append(1)
                    for i in range(0, len(self.num) - 1):
                        self.num[i] = 0
                    still_needed = needed - self.suffix_digits_sum()
                    # print(f'Needed: {old_needed} gives: {self.value} missing: {still_needed}')

        def make_suffix_value():
            current_value = self.value
            self.n = max(self.n + 1, current_value // FACTORIALS[9])
            self.num = list(digits_gen(self.n * FACTORIALS[9]))
            return self.suffix_digits_sum()

        # Get next suffix value [one 9 digit more so sum is increase by 9!]
        next_value = self.value + FACTORIALS[9]
        self.n += 1
        self.num = list(digits_gen(next_value))
        suffix_sum = self.suffix_digits_sum()
        if DEBUG:
            pass
            # print(f'Suffix: len:{self.n}, sum: {self.digits_sum()}, s_sum:{suffix_sum}, {self.value}')

        while suffix_sum < sum_needed-47:
            next_value_with_sum(sum_needed-47)
            suffix_sum = make_suffix_value()
            if DEBUG:
                pass
                # print(f'Suffix: len:{self.n}, sum: {self.digits_sum()}, s_sum:{suffix_sum}, {self.value}')

        self.sum = suffix_sum
        assert self.value % FACTORIALS[9] == 0
        self.n = self.value // FACTORIALS[9]

    def digits_gen(self):
        """"  Number digits generator """
        for d in self.num:
            yield d


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

    def g_find_first(f_suffix):
        """
        Founds n such that sf(n) == i
        :param f_suffix: start with n being '9' suffix length f_suffix.n
        :return: prefix which form with suffix n such sf(n) == i
        """
        cost = 0
        while True:
            cost += 1
            f_sum = f_suffix.digits_sum()
            if f_sum == i:
                # found sf(n) = i, where n contains only digits 9
                if DEBUG:
                    print(f'cost: {cost:12}, len={f_suffix.n:6}, g({i}) = 9*{f_suffix.n}')
                return 0

            needed_prefix_sum = i - f_sum
            prefix_part_sum = sum(f_suffix.num[0:5])
            max_prefix_sum = 47 - prefix_part_sum
            if needed_prefix_sum > max_prefix_sum:
                f_suffix.next(i)
                continue
            prefixes = PREFIXES.get(needed_prefix_sum % 9, [])
            suffix_value = f_suffix.value
            for prefix in prefixes:
                cost += 1
                if digits_sum(suffix_value + F_PREFIX[prefix]) == i:
                    if DEBUG:
                        print(
                            f'cost: {cost:12}, len={len(str(prefix)) + f_suffix.n:6}, '
                            f'g({i}) = {str(prefix)}+9*{f_suffix.n}')
                    return prefix
            if prefixes:
                if DEBUG:
                    pass
                    # print(f'Not found matched prefix for i={i} with 9*{f_suffix.n} '
                    #       f'and missing digits sum={needed_prefix_sum}')
            else:
                if DEBUG:
                    pass
                    # print(f'Missing prefix for i={i}  with 9*{f_suffix.n} and missing digits sum={needed_prefix_sum}')
            f_suffix.next(i)

    def g_scan_next(f_suffix, *, max_cnt=None):
        """
        Founds next n such that sf(n) == i
        :param f_suffix: start with n being '9' suffix length f_suffix.n
        :param max_cnt: limit for stop scanning
        :return: prefix which form with suffix n such sf(n) == i or None if not found
        """
        cost = 0
        while f_suffix.n < max_cnt:
            # exit in case of limit for amount of '9' digits in suffix
            cost += 1
            f_sum = f_suffix.digits_sum()
            if f_sum == i:
                # found sf(n) = i, where n contains only digits 9
                if DEBUG:
                    print(f'cost: {cost:12}, len={f_suffix.n:6}, g({i}) = 9*{f_suffix.n}')
                return 0

            needed_prefix_sum = i - f_sum
            while needed_prefix_sum < 0:
                needed_prefix_sum += 9
            prefix_part_sum = sum(f_suffix.num[0:5])
            max_prefix_sum = 47 - prefix_part_sum
            # print(f'f_sum {f_sum}, f_prefix_part: {prefix_part_sum}, needed: {needed_prefix_sum}/{i-f_sum}, max_prefix_sum: {max_prefix_sum}')
            if needed_prefix_sum > max_prefix_sum:
                # print(f'Too small prefix for i={i}  with 9*{f_suffix.n} and missing digits sum={needed_prefix_sum}')
                f_suffix.next(i)
                continue
            # print(i, f_suffix.value, needed_prefix_sum)
            prefixes = PREFIXES.get(needed_prefix_sum % 9, [])
            suffix_value = f_suffix.value
            suffix_len = f_suffix.n
            for prefix in prefixes:
                cost += 1
                # print(prefix, f(prefix))
                if len(prefix) + suffix_len > max_cnt:
                    break
                if digits_sum(suffix_value + F_PREFIX[prefix]) == i:
                    if DEBUG:
                        print(
                            f'cost: {cost:12}, len={len(str(prefix)) + f_suffix.n:6}, '
                            f'g({i}) = {str(prefix)}+9*{f_suffix.n}')
                    return prefix
            if prefixes:
                if DEBUG:
                    pass
                    # print(f'Not found matched prefix for i={i} with 9*{f_suffix.n} '
                    #       f'and missing digits sum={needed_prefix_sum}')
            else:
                if DEBUG:
                    pass
                    # print(f'Missing prefix for i={i}  with 9*{f_suffix.n} and missing digits sum={needed_prefix_sum}')
            f_suffix.next(i)
        # Not found sf(n) = i
        return None

    suffix = FDigits(0)
    for i in range(1, max_i + 1):
        if DEBUG:
            print(f'G({i}) starts with suffix len {suffix.n}')
        if sg_cache.get(i):
            continue
        more_results = False
        prefix = g_find_first(suffix)
        current_len = len(str(prefix)) + suffix.n
        current_suffix = FDigits(suffix)
        suffix.next(i)
        while suffix.n <= current_len:
            # print(f'TryNext {suffix.n}, {current_len}')
            tmp_prefix = g_scan_next(suffix, max_cnt=current_len)
            if tmp_prefix is not None:
                more_results = True
                tmp_len = len(str(tmp_prefix)) + suffix.n
                '''
                print(f'curlen {current_len}, tmp len {tmp_len}, prefix {prefix}, tmp_prefix {tmp_prefix}, '
                      f'compare {prefix_lt_prefix(tmp_prefix, prefix)}')
                '''
                if (tmp_len < current_len) or (tmp_len == current_len and prefix_lt_prefix(tmp_prefix, prefix)):
                    prefix = tmp_prefix
                    current_len = tmp_len
                    current_suffix = FDigits(suffix)
            suffix.next(i)

        # sf_cache[i] = str(prefix) + '9' * current_suffix.n
        sg_cache[i] = digits_sum(prefix) + 9 * current_suffix.n
        if mod:
            sg_cache[i] = sg_cache[i] % mod
        if more_results and DEBUG:
            print(f'Best result for i={i} is {str(prefix)}+9*{current_suffix.n}')
        suffix = FDigits(max(0, current_suffix.n-10))
    return sg_cache


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
    sg_table = [1, 2, 5, 6, 7, 3, 4, 5, 6, 7, 8, 8, 9, 13, 9, 10, 11, 13, 14, 15, 16, 17, 18, 13, 14, 15, 9, 10,
                11, 12, 13, 14, 12, 13, 14, 15, 19, 28, 24, 25, 37, 31, 32, 45, 46, 50, 66, 67, 71, 84, 89, 90, 114,
                118, 134, 154, 158, 193, 231, 235, 247, 317, 321, 545, 843, 1052, 1339, 1574, 2034, 2035, 2294, 2566,
                5035, 7578, 9997, 14937, 15009, 17415, 19912, 22416, 24933, 49686, 74498, 121603, 124135, 148899,
                173672, 220757, 223324, 248145, 496173, 967389, 992162, 1240190, 1711406, 1736179, 1984255, 2455447,
                2480268, 4960419, 7440581, 9920765, 14856251, 14881015, 17361186, 19841385, 22321571, 47123166,
                71924693, 74404903, 99206450, 124008025, 148809646, 173611193, 198412768, 223214413, 248015925,
                496031816, 744047718, 1215277860, 1240079422, 1488095324, 1736111200, 1984127056, 2232142919,
                2480158795, 4960317556, 7440476328, 12375992162, 12400793737, 14880952509, 17361111207,
                22296627021, 22321428666, 24801587412, 49603174707, 74404761998, 99206349313, 146329365162,
                148809523899, 173611111214, 198412698494, 223214285824, 471230158816, 719246031823, 967261904889,
                1215277777881, 1463293650888, 1711309523906, 1959325396898, 2207341269905, 2455357142947,
                4712301587433, 4960317460440, 7440476190581, 9920634920744, 12400793650874, 14880952381015,
                17361111111165, 22073412698529, 22321428571571, 24801587301686, 49603174603275, 74404761904903,
                99206349206429, 146329365079457, 148809523809646, 173611111111172, 198412698412789, 223214285714413,
                471230158730268, 496031746031837, 744047619047718, 992063492063573, 1240079365079443,
                1488095238095324, 1736111111111179, 1984126984127014, 2232142857142919, 4935515873015925,
                4960317460317577, 7440476190476328, 9920634920635018, 12400793650793758, 14880952380952509,
                17361111111111186, 19841269841269891, 22321428571428666, 24801587301587391, 49603174603174665,
                74404761904761998, 99206349206349292, 124007936507936614, 148809523809523899, 173611111111111193,
                198412698412698515, 223214285714285824, 248015873015873166, 496031746031746152, 967261904761904889]

    for i, sg_sum in enumerate(sg_table, 1):
        if sg_cache.get(i) and sg_cache.get(i) != sg_sum:
            print(f'Assertion error sg({i}) is {sg_cache.get(i, 0)} while expected {sg_sum}')


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
    exit()


    """
Factorials[0..9] = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
3 ['5', '12', '33', '34', '577', '3477', '12333', '34444', '55556', '56666', '334455', '345556', '567777', '1233377', '1234445', '1244556', '3334445', '3334556', '3344556', '12334444', '55556677', '123335556', '334455677', '577777788', '1234445677', '3334445677', '33445555566', '55556777788', '123444555566', '333444555566', '334455777788', '566666677788', '1234445777788', '3334445777788', '3466666677788', '55556666788888', '555566666677777', '1233366666677788', '1244555556666667', '3334555556666667', '3344555556666667', '55556667778888888', '334455555666666777', '555566666777777788', '566666677777778888', '1234445555666666777', '1244555556666677788', '3334445555666666777', '3334555556666677788', '3344555556666677788', '334455555666667777788', '1234445555666667777788', '3334445555666667777788', '334455555666677777778888', '1234445555666677777778888', '3334445555666677777778888']
2 ['2', '1223', '2333', '233377', '234445', '244556', '1224444', '2334444', '23335556', '122334556', '234445677', '23444555566', '234445777788', '233366666677788', '244555556666667', '122334555556666667', '234445555666666777', '244555556666677788', '122334555556666677788', '234445555666667777788', '234445555666677777778888']
5 ['25', '122', '233', '234', '244', '2577', '12235', '23335', '23477', '24477', '122333', '122334', '234444', '244555', '244666', '244888', '255556', '256666', '1223577', '2333577', '2334455', '2344455', '2345556', '2445556', '2447777', '2567777', '12233377', '12233477', '12234445', '12244445', '12244556', '23334445', '23334556', '23335555', '23335666', '23335888', '23344445', '23344556', '23444556', '122334444', '122334555', '122334666', '122334888', '122355556', '122356666', '233355556', '233356666', '233357777', '234445577', '244555677', '244666677', '255556677', '1223334455', '1223335556', '1223345556', '1223347777', '1223567777', '1224444577', '2333567777', '2334444577', '2334455677', '2344455677', '2446777777', '2577777788', '12233344556', '12234445677', '12244445677', '23334445677', '23335555677', '23335666677', '23344445677', '23444555556', '23444555558', '23444556666', '23444556888', '24455566666', '24455588888', '122334555677', '122334666677', '122355556677', '122444455556', '122444456666', '233355556677', '233356777777', '233444455556', '233444456666', '233445555566', '234445555566', '234445567777', '244555667777', '244555777788', '244666777788', '255556777788', '1223334455677', '1223346777777', '1223444555566', '1223577777788', '1224444555566', '1224444567777', '2333444555566', '2333555566666', '2333555588888', '2333577777788', '2334444555566', '2334444567777', '2334455777788', '2344455777788', '2566666677788', '12233455566666', '12233455588888', '12234445777788', '12244445777788', '23334445777788', '23335555667777', '23335555777788', '23335666777788', '23344445777788', '23444555556677', '23444556666677', '23444557788888', '23466666677788', '24466666677788', '122333445555566', '122334555667777', '122334555777788', '122334666777788', '122355556777788', '122444455556677', '233355556777788', '233444455556677', '234445566666678', '234445566777777', '234445577777788', '244555666667888', '244555677777788', '244666666788888', '255556666788888', '1223334455777788', '1223566666677788', '1224444577777788', '2333566666677788', '2334444577777788', '2344455555666666', '2344455555688888', '2446666667777788', '2555566666677777', '12233366666677788', '12233466666677788', '12244555556666667', '23334555556666667', '23335555666667888', '23335555677777788', '23335666666788888', '23344555556666667', '23444555556666667', '23444555556667777', '23444555556777788', '23444556666777788', '122334555666667888', '122334555677777788', '122334666666788888', '122355556666788888', '122444455556777788', '233355556666788888', '233356666667777788', '233444455556777788', '234445566666677788', '234445566666777888', '244555666677788888', '244666667778888888', '255556667778888888', '1223346666667777788', '1223555566666677777', '1224444566666677788', '2333555566666677777', '2334444566666677788', '2334455555666666777', '2344455555666666777', '2445556666667777777', '2446666677777778888', '2555566666777777788', '2566666677777778888', '12233344555556666667', '12234445555666666777', '12244445555666666777', '12244555556666677788', '23334445555666666777', '23334555556666677788', '23335555666677788888', '23335666667778888888', '23344445555666666777', '23344555556666677788', '23444555556666667888', '23444555556666677788', '23444555556666788888', '23444555556677777788', '122334555666677788888', '122334666667778888888', '122355556667778888888', '122444455556666788888', '233355556666667777777', '233355556667778888888', '233356666677777778888', '233444455556666788888', '234445555566666677777', '234445566667777788888', '244555666777778888888', '1223334455555666666777', '1223345556666667777777', '1223346666677777778888', '1223555566666777777788', '1223566666677777778888', '1224444555566666677777', '2333555566666777777788', '2333566666677777778888', '2334444555566666677777', '2334455555666667777788', '2344455555666667777788', '12233344555556666677788', '12234445555666667777788', '12244445555666667777788', '23334445555666667777788', '23335555666777778888888', '23344445555666667777788', '23444555556666677788888', '23444555556667778888888', '23444556666667778888888', '122334555666777778888888', '122444455556667778888888', '233444455556667778888888', '234445555566666777777788', '234445566666677777778888', '234445566677777778888888', '1223334455555666667777788', '1224444555566666777777788', '1224444566666677777778888', '2334444555566666777777788', '2334444566666677777778888', '2334455555666677777778888', '2344455555666677777778888', '12234445555666677777778888', '12244445555666677777778888', '23334445555666677777778888', '23344445555666677777778888', '23444555556666777778888888', '1223334455555666677777778888']
4 ['15', '22', '133', '134', '1577', '2235', '13477', '22333', '22334', '134444', '155556', '156666', '223577', '1334455', '1345556', '1567777', '2233377', '2233477', '2234445', '2244445', '2244556', '13334445', '13334556', '13344556', '22334444', '22334555', '22334666', '22334888', '22355556', '22356666', '155556677', '223334455', '223335556', '223345556', '223347777', '223567777', '224444577', '1334455677', '1577777788', '2233344556', '2234445677', '2244445677', '13334445677', '22334555677', '22334666677', '22355556677', '22444455556', '22444456666', '133445555566', '155556777788', '223334455677', '223346777777', '223444555566', '223577777788', '224444555566', '224444567777', '1333444555566', '1334455777788', '1566666677788', '2233455566666', '2233455588888', '2234445777788', '2244445777788', '13334445777788', '13466666677788', '22333445555566', '22334555667777', '22334555777788', '22334666777788', '22355556777788', '22444455556677', '155556666788888', '223334455777788', '223566666677788', '224444577777788', '1555566666677777', '2233366666677788', '2233466666677788', '2244555556666667', '13334555556666667', '13344555556666667', '22334555666667888', '22334555677777788', '22334666666788888', '22355556666788888', '22444455556777788', '155556667778888888', '223346666667777788', '223555566666677777', '224444566666677788', '1334455555666666777', '1555566666777777788', '1566666677777778888', '2233344555556666667', '2234445555666666777', '2244445555666666777', '2244555556666677788', '13334445555666666777', '13334555556666677788', '13344555556666677788', '22334555666677788888', '22334666667778888888', '22355556667778888888', '22444455556666788888', '223334455555666666777', '223345556666667777777', '223346666677777778888', '223555566666777777788', '223566666677777778888', '224444555566666677777', '1334455555666667777788', '2233344555556666677788', '2234445555666667777788', '2244445555666667777788', '13334445555666667777788', '22334555666777778888888', '22444455556667778888888', '223334455555666667777788', '224444555566666777777788', '224444566666677777778888', '1334455555666677777778888', '2234445555666677777778888', '2244445555666677777778888', '13334445555666677777778888', '223334455555666677777778888']
1 ['1', '223', '224444', '22334556', '22334555556666667', '22334555556666677788']
['12233344445556667778888888']
cost:            1, len=     1, g(1) = 1+9*0
cost:            1, len=     1, g(2) = 2+9*0
cost:            1, len=     1, g(3) = 5+9*0
cost:            1, len=     2, g(4) = 15+9*0
cost:            1, len=     2, g(5) = 25+9*0
cost:            1, len=     1, g(6) = 3+9*0
cost:            1, len=     2, g(7) = 13+9*0
cost:            1, len=     2, g(8) = 23+9*0
cost:            1, len=     1, g(9) = 6+9*0
cost:            1, len=     2, g(10) = 16+9*0
cost:            1, len=     2, g(11) = 26+9*0
cost:            1, len=     2, g(12) = 44+9*0
cost:            1, len=     3, g(13) = 144+9*0
cost:            1, len=     3, g(14) = 256+9*0
cost:            1, len=     2, g(15) = 36+9*0
cost:            1, len=     3, g(16) = 136+9*0
cost:            1, len=     3, g(17) = 236+9*0
cost:            1, len=     2, g(18) = 67+9*0
cost:            1, len=     3, g(19) = 167+9*0
cost:            1, len=     3, g(20) = 267+9*0
cost:            1, len=     3, g(21) = 446+9*0
cost:            1, len=     4, g(22) = 1446+9*0
cost:            1, len=     4, g(23) = 2567+9*0
cost:            1, len=     3, g(24) = 367+9*0
cost:            1, len=     4, g(25) = 1367+9*0
cost:            1, len=     4, g(26) = 2367+9*0
cost:            1, len=     3, g(27) = 788+9*0
cost:            0, len=     1, g(27) = 9*1
Best result for i=27 is 0+9*1
cost:            1, len=     2, g(28) = 1+9*1
cost:            1, len=     2, g(29) = 2+9*1
cost:            2, len=     3, g(30) = 12+9*1
cost:            1, len=     3, g(30) = 5+9*2
Best result for i=30 is 12+9*1
cost:            2, len=     3, g(31) = 22+9*1
cost:            1, len=     4, g(31) = 15+9*2
Best result for i=31 is 22+9*1
cost:            2, len=     4, g(32) = 122+9*1
cost:            1, len=     4, g(32) = 25+9*2
cost:            1, len=     5, g(32) = 25+9*3
Best result for i=32 is 122+9*1
cost:            1, len=     2, g(33) = 3+9*1
cost:            1, len=     3, g(34) = 13+9*1
cost:            1, len=     4, g(34) = 13+9*2
Best result for i=34 is 13+9*1
cost:            1, len=     3, g(35) = 23+9*1
cost:            1, len=     4, g(35) = 23+9*2
Best result for i=35 is 23+9*1
cost:            9, len=     4, g(36) = 123+9*1
cost:            4, len=     4, g(36) = 35+9*2
cost:            4, len=     5, g(36) = 35+9*3
Best result for i=36 is 123+9*1
cost:           10, len=     5, g(37) = 1333+9*1
cost:            4, len=     5, g(37) = 135+9*2
cost:            4, len=     6, g(37) = 135+9*3
cost:            2, len=     7, g(37) = 178+9*4
Best result for i=37 is 1333+9*1
cost:           28, len=     6, g(38) = 24447+9*1
cost:            4, len=     5, g(38) = 235+9*2
cost:            4, len=     6, g(38) = 235+9*3
cost:            2, len=     7, g(38) = 278+9*4
Best result for i=38 is 235+9*2
cost:           18, len=     6, g(39) = 1235+9*2
cost:            1, len=     5, g(39) = 44+9*3
cost:            3, len=     7, g(39) = 448+9*4
Best result for i=39 is 44+9*3
cost:            1, len=     6, g(40) = 144+9*3
cost:            3, len=     8, g(40) = 1448+9*4
cost:            2, len=     9, g(40) = 1447+9*5
Best result for i=40 is 144+9*3
cost:           13, len=     7, g(41) = 2355+9*3
cost:            5, len=     9, g(41) = 12278+9*4
cost:            2, len=     9, g(41) = 2578+9*5
cost:           85, len=    12, g(41) = 245566+9*6
Best result for i=41 is 2355+9*3
cost:           49, len=     8, g(42) = 12355+9*3
cost:            2, len=     7, g(42) = 378+9*4
cost:            2, len=     8, g(42) = 378+9*5
cost:           81, len=    11, g(42) = 44566+9*6
Best result for i=42 is 378+9*4
cost:            2, len=     8, g(43) = 1378+9*4
cost:            2, len=     9, g(43) = 1378+9*5
cost:           80, len=    12, g(43) = 144566+9*6
cost:           31, len=    13, g(43) = 136678+9*7
Best result for i=43 is 1378+9*4
cost:            2, len=     8, g(44) = 2378+9*4
cost:            2, len=     9, g(44) = 2378+9*5
cost:           88, len=    12, g(44) = 246888+9*6
cost:           27, len=    13, g(44) = 236678+9*7
Best result for i=44 is 2378+9*4
cost:            7, len=     9, g(45) = 12378+9*4
cost:            3, len=     9, g(45) = 3578+9*5
cost:          252, len=    13, g(45) = 1246888+9*6
cost:           68, len=    14, g(45) = 1236678+9*7
cost:            8, len=    13, g(45) = 12388+9*8
Best result for i=45 is 12378+9*4
cost:           10, len=    10, g(46) = 133378+9*4
cost:            3, len=    10, g(46) = 13578+9*5
cost:          248, len=    13, g(46) = 2246888+9*6
cost:           58, len=    14, g(46) = 2246678+9*7
cost:           11, len=    14, g(46) = 133388+9*8
cost:          465, len=    17, g(46) = 22477888+9*9
Best result for i=46 is 133378+9*4
cost:          155, len=    13, g(47) = 235666678+9*4
cost:            3, len=    10, g(47) = 23578+9*5
cost:          235, len=    14, g(47) = 12246888+9*6
cost:           48, len=    15, g(47) = 12246678+9*7
cost:           15, len=    14, g(47) = 235788+9*8
cost:          445, len=    18, g(47) = 122477888+9*9
Best result for i=47 is 23578+9*5
cost:            7, len=    11, g(48) = 123578+9*5
cost:          628, len=    15, g(48) = 123346888+9*6
cost:          132, len=    16, g(48) = 123346678+9*7
cost:            5, len=    13, g(48) = 44788+9*8
cost:         1092, len=    19, g(48) = 1233477888+9*9
cost:           21, len=    14, g(48) = 4468+9*10
Best result for i=48 is 123578+9*5
cost:            8, len=    12, g(49) = 1333578+9*5
cost:         1542, len=    17, g(49) = 14488888888+9*6
cost:          389, len=    18, g(49) = 14466666678+9*7
cost:            5, len=    14, g(49) = 144788+9*8
cost:         3114, len=    22, g(49) = 1344455677888+9*9
cost:           21, len=    15, g(49) = 14468+9*10
cost:           32, len=    16, g(49) = 14557+9*11
Best result for i=49 is 1333578+9*5
cost:           29, len=    14, g(50) = 122457778+9*5
cost:         2655, len=    19, g(50) = 1224588888888+9*6
cost:          561, len=    20, g(50) = 1224566666678+9*7
cost:            6, len=    15, g(50) = 2355788+9*8
cost:         3793, len=    23, g(50) = 12245666677888+9*9
cost:           65, len=    17, g(50) = 1224568+9*10
cost:           36, len=    16, g(50) = 24557+9*11
cost:          142, len=    20, g(50) = 12234478+9*12
cost:          155, len=    21, g(50) = 12245688+9*13
Best result for i=50 is 122457778+9*5
cost:          107, len=    15, g(51) = 1233457778+9*5
cost:          892, len=    21, g(51) = 12334566666678+9*7
cost:            3, len=    14, g(51) = 445788+9*8
cost:         5397, len=    23, g(51) = 34446688888888+9*9
cost:          241, len=    18, g(51) = 12334568+9*10
cost:           32, len=    15, g(51) = 4457+9*11
cost:           73, len=    18, g(51) = 344478+9*12
cost:           96, len=    19, g(51) = 445688+9*13
Best result for i=51 is 445788+9*8
cost:            3, len=    15, g(52) = 1445788+9*8
cost:         5108, len=    24, g(52) = 134446688888888+9*9
cost:          317, len=    19, g(52) = 134446778+9*10
cost:           32, len=    16, g(52) = 14457+9*11
cost:           70, len=    19, g(52) = 1344478+9*12
cost:           93, len=    20, g(52) = 1445688+9*13
cost:         1873, len=    31, g(52) = 13444666677788888+9*14
Best result for i=52 is 1445788+9*8
cost:           10, len=    17, g(53) = 122455788+9*8
cost:         5653, len=    26, g(53) = 1224555557777778+9*10
cost:           69, len=    17, g(53) = 236667+9*11
cost:        10678, len=    31, g(53) = 1224555556666888888+9*12
cost:          156, len=    21, g(53) = 24444688+9*13
cost:          332, len=    29, g(53) = 12245555567778+9*15
cost:           63, len=    23, g(53) = 2366688+9*16
Best result for i=53 is 122455788+9*8
cost:           30, len=    18, g(54) = 1233455788+9*8
cost:         7797, len=    27, g(54) = 12334555557777778+9*10
cost:          233, len=    18, g(54) = 1236667+9*11
cost:        12659, len=    32, g(54) = 12334555556666888888+9*12
cost:          217, len=    21, g(54) = 34445688+9*13
cost:          514, len=    30, g(54) = 123345555567778+9*15
cost:          153, len=    24, g(54) = 12366688+9*16
cost:        10074, len=    36, g(54) = 1233455666788888888+9*17
Best result for i=54 is 1233455788+9*8
cost:           45, len=    19, g(55) = 13444577788+9*8
cost:        10921, len=    30, g(55) = 13444555566666678888+9*10
cost:          262, len=    19, g(55) = 13336667+9*11
cost:          182, len=    22, g(55) = 134445688+9*13
cost:         1174, len=    34, g(55) = 1344455557777777888+9*15
cost:          150, len=    25, g(55) = 133366688+9*16
cost:          339, len=    28, g(55) = 1333678888+9*18
Best result for i=55 is 13444577788+9*8
cost:          591, len=    27, g(56) = 1223334444555677788+9*8
cost:        15432, len=    39, g(56) = 12233344445556666677777888888+9*10
cost:         1913, len=    23, g(56) = 122455566667+9*11
cost:         1532, len=    26, g(56) = 2444458888888+9*13
cost:         1649, len=    41, g(56) = 12245556666677777788888888+9*15
cost:          466, len=    27, g(56) = 12246667788+9*16
cost:         1867, len=    32, g(56) = 12245556678888+9*18
cost:            5, len=    23, g(56) = 2357+9*19
cost:         7086, len=    39, g(56) = 1223334444555888888+9*20
cost:          806, len=    33, g(56) = 122466678888+9*21
cost:           67, len=    28, g(56) = 235667+9*22
Best result for i=56 is 122455566667+9*11
cost:         3627, len=    24, g(57) = 1233455566667+9*11
cost:         1719, len=    26, g(57) = 3444558888888+9*13
cost:          844, len=    28, g(57) = 123346667788+9*16
cost:         2846, len=    33, g(57) = 123345556678888+9*18
cost:           29, len=    24, g(57) = 12357+9*19
cost:         1335, len=    34, g(57) = 1233466678888+9*21
cost:           59, len=    27, g(57) = 44667+9*22
cost:         1993, len=    37, g(57) = 12334677888888+9*23
Best result for i=57 is 1233455566667+9*11
cost:        22896, len=    27, g(58) = 13444558888888+9*13
cost:         2092, len=    31, g(58) = 134445566667788+9*16
cost:         5948, len=    37, g(58) = 1344455677777888888+9*18
cost:           37, len=    25, g(58) = 133357+9*19
cost:         2750, len=    37, g(58) = 1333566667778888+9*21
cost:           56, len=    28, g(58) = 144667+9*22
cost:         3871, len=    40, g(58) = 13444556677888888+9*23
cost:            9, len=    31, g(58) = 1333588+9*24
Best result for i=58 is 133357+9*19
cost:         1525, len=    31, g(59) = 122333444457+9*19
cost:         6323, len=    42, g(59) = 122456667777777888888+9*21
cost:          151, len=    30, g(59) = 12245667+9*22
cost:           30, len=    33, g(59) = 122457788+9*24
cost:        12011, len=    45, g(59) = 1224566667777888888+9*26
cost:          363, len=    36, g(59) = 122344666+9*27
Best result for i=59 is 12245667+9*22
cost:          465, len=    31, g(60) = 123345667+9*22
cost:          108, len=    34, g(60) = 1233457788+9*24
cost:        14774, len=    46, g(60) = 12334566667777888888+9*26
cost:          285, len=    34, g(60) = 3444666+9*27
Best result for i=60 is 123345667+9*22
cost:          612, len=    32, g(61) = 1344466777+9*22
cost:         3648, len=    44, g(61) = 13444666666777778888+9*24
cost:          288, len=    35, g(61) = 13444666+9*27
Best result for i=61 is 1344466777+9*22
cost:        25078, len=    51, g(62) = 122333444455555666678888888+9*24
cost:         3178, len=    41, g(62) = 12245555588888+9*27
Best result for i=62 is 12245555588888+9*27
cost:         5375, len=    42, g(63) = 123345555588888+9*27
cost:        18334, len=    66, g(64) = 13444555568+9*55
cost:        41295, len=   103, g(65) = 122333444455566888888+9*82
cost:        15072, len=   123, g(66) = 1233455566688+9*110
cost:        38798, len=   155, g(67) = 134445566668888888+9*137
cost:         4060, len=   184, g(68) = 1223334444566666888+9*165
cost:        35037, len=   235, g(69) = 123345666677888888+9*217
cost:           75, len=   229, g(69) = 344478888+9*220
Best result for i=69 is 344478888+9*220
cost:           68, len=   230, g(70) = 1344478888+9*220
cost:        14588, len=   264, g(71) = 1223334444555557+9*248
cost:        39560, len=   292, g(72) = 12334555556788888+9*275
cost:        40484, len=   566, g(73) = 134445555666778+9*551
cost:        55122, len=   853, g(74) = 122333444455566666777888888+9*826
cost:        21264, len=  1117, g(75) = 123345557777788+9*1102
cost:        69219, len=  1665, g(76) = 134445567888888+9*1650
cost:         2928, len=  1669, g(76) = 1344455666667778+9*1653
Best result for i=76 is 134445567888888+9*1650
cost:         8558, len=  1678, g(77) = 1223334444566667777777888+9*1653
cost:        54003, len=  1941, g(78) = 123345666666+9*1929
cost:        42207, len=  2217, g(79) = 1344467788888+9*2204
cost:        28090, len=  2501, g(80) = 122333444455555667778+9*2480
cost:        25970, len=  2779, g(81) = 123345555566667777888888+9*2755
cost:        25117, len=  5527, g(82) = 1344455556678888+9*5511
cost:        76558, len=  8287, g(83) = 12233344445557777778+9*8267
cost:        84263, len= 13518, g(84) = 123345556777777+9*13503
cost:        63604, len= 13800, g(85) = 1344455666777777788888+9*13778
cost:        53089, len= 16553, g(86) = 1223334444567777888+9*16534
cost:        66622, len= 19303, g(87) = 1233456666668+9*19290
cost:        83328, len= 24532, g(88) = 134447+9*24526
cost:        70846, len= 24824, g(89) = 12233344445555567788888+9*24801
cost:        75076, len= 27581, g(90) = 123345555566666677777788+9*27557
cost:       121877, len= 55139, g(91) = 1344455556666667777788888+9*55114
cost:       150268, len=107498, g(92) = 1223334444555677777778888+9*107473
cost:        63137, len=110248, g(93) = 1233455566666677788+9*110229
cost:       113150, len=137806, g(94) = 13444556666667788888+9*137786
cost:       142003, len=190165, g(95) = 12233344445677778888+9*190145
cost:        58103, len=192915, g(96) = 12334566666688+9*192901
cost:       121440, len=220480, g(97) = 1344466666677777778888+9*220458
cost:       144514, len=272837, g(98) = 12233344445555578888+9*272817
cost:        83004, len=275594, g(99) = 123345555566666777778+9*275573
cost:       107604, len=551165, g(100) = 1344455556666777888+9*551146
sum_sg(100) is 20563682 computed in 19.60 seconds    
"""
