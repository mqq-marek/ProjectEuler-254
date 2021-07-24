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

    def prefix_digits_sum(self):
        """
        Sum of prefix part digit.
        """
        suffix_sum = sum(self.num[:6])
        return suffix_sum

    def suffix_digits_sum(self):
        """
        Sum of suffix only digits in  n.
        Does not include 6 least significant digits
        :return:
        """
        suffix_sum = sum(self.num[6:])
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
            for i in range(6, len(self.num)):
                inc_sum, self.num[i] = increase_digit(inc_sum, self.num[i])
                if inc_sum == 0:
                    return 0
            return inc_sum

        def get_value_with_sum(needed):
            still_needed = needed - self.suffix_digits_sum()
            while still_needed > 0:
                still_needed = update_value(still_needed)
                if still_needed:
                    self.num.append(1)
                    for i in range(6, len(self.num) - 1):
                        self.num[i] = 0
                    still_needed = needed - 1

        def make_suffix_value():
            for i in range(0, 6):
                self.num[i] = 0
            # defensive check - try all possible values for prefix in a few passes
            current_value = self.value  # + 1000000 - FACTORIALS[9]
            # increase n for passing for all possible FACTORIALS[9] with requested suffix digits amount
            self.n = max(self.n + 1, current_value // FACTORIALS[9])
            self.num = list(digits_gen(self.n * FACTORIALS[9]))
            return self.suffix_digits_sum()

        # Get next suffix value [every 9 digit increase value by 9!]
        next_value = self.value + FACTORIALS[9]
        self.n += 1
        self.num = list(digits_gen(next_value))
        suffix_sum = self.suffix_digits_sum()

        # if increase does not give requested amount of digits, try next value
        while suffix_sum < sum_needed-54:
            get_value_with_sum(sum_needed-54)
            suffix_sum = make_suffix_value()

        self.sum = suffix_sum
        assert self.value % FACTORIALS[9] == 0
        if DEBUG:
            pass
            # print(f"FDigit.next({sum_needed}) => '9'*{self.n}, f_: {self.value} sf_(suffix): {self.sum}")

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
            prefix_part_sum = f_suffix.prefix_digits_sum()
            max_prefix_sum = 54 - prefix_part_sum
            if needed_prefix_sum > max_prefix_sum:
                # get nex prospect
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
            prefix_part_sum = f_suffix.prefix_digits_sum()
            max_prefix_sum = 54 - prefix_part_sum
            if needed_prefix_sum > max_prefix_sum:
                f_suffix.next(i)
                continue
            prefixes = PREFIXES.get(needed_prefix_sum % 9, [])
            suffix_value = f_suffix.value
            suffix_len = f_suffix.n
            for prefix in prefixes:
                cost += 1
                if len(prefix) + suffix_len > max_cnt:
                    break
                if digits_sum(suffix_value + F_PREFIX[prefix]) == i:
                    if DEBUG:
                        print(
                            f'cost: {cost:12}, len={len(str(prefix)) + f_suffix.n:6}, '
                            f'g({i}) = {str(prefix)}+9*{f_suffix.n}')
                    return prefix
            f_suffix.next(i)
        # Not found additional sf(n) = i in requested scope
        return None

    suffix = FDigits(0)
    for i in range(1, max_i + 1):
        if DEBUG:
            pass
            # print(f'G({i}) starts with suffix len {suffix.n}')
        if sg_cache.get(i):
            continue
        more_results = False
        prefix = g_find_first(suffix)
        current_len = len(str(prefix)) + suffix.n
        current_suffix = FDigits(suffix)
        suffix.next(i)
        # Try to find next g(n)=i better than the first one until you get suffix len equal length of current n
        while suffix.n <= current_len:
            tmp_prefix = g_scan_next(suffix, max_cnt=current_len)
            if tmp_prefix is not None:
                more_results = True
                tmp_len = len(str(tmp_prefix)) + suffix.n
                if (tmp_len < current_len) or (tmp_len == current_len and prefix_lt_prefix(tmp_prefix, prefix)):
                    prefix = tmp_prefix
                    current_len = tmp_len
                    current_suffix = FDigits(suffix)
            suffix.next(i)

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
    development_main(2000)
    # assert_gen()
    exit()


    """
Factorials[0..9] = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
3 ['5', '12', '33', '34', '577', '3477', '12333', '34444', '55556', '56666', '334455', '345556', '567777', '1233377', '1234445', '1244556', '3334445', '3334556', '3344556', '12334444', '55556677', '123335556', '334455677', '577777788', '1234445677', '3334445677', '33445555566', '55556777788', '123444555566', '333444555566', '334455777788', '566666677788', '1234445777788', '3334445777788', '3466666677788', '55556666788888', '555566666677777', '1233366666677788', '1244555556666667', '3334555556666667', '3344555556666667', '55556667778888888', '334455555666666777', '555566666777777788', '566666677777778888', '1234445555666666777', '1244555556666677788', '3334445555666666777', '3334555556666677788', '3344555556666677788', '334455555666667777788', '1234445555666667777788', '3334445555666667777788', '334455555666677777778888', '1234445555666677777778888', '3334445555666677777778888']
2 ['2', '1223', '2333', '233377', '234445', '244556', '1224444', '2334444', '23335556', '122334556', '234445677', '23444555566', '234445777788', '233366666677788', '244555556666667', '122334555556666667', '234445555666666777', '244555556666677788', '122334555556666677788', '234445555666667777788', '234445555666677777778888']
5 ['25', '122', '233', '234', '244', '2577', '12235', '23335', '23477', '24477', '122333', '122334', '234444', '244555', '244666', '244888', '255556', '256666', '1223577', '2333577', '2334455', '2344455', '2345556', '2445556', '2447777', '2567777', '12233377', '12233477', '12234445', '12244445', '12244556', '23334445', '23334556', '23335555', '23335666', '23335888', '23344445', '23344556', '23444556', '122334444', '122334555', '122334666', '122334888', '122355556', '122356666', '233355556', '233356666', '233357777', '234445577', '244555677', '244666677', '255556677', '1223334455', '1223335556', '1223345556', '1223347777', '1223567777', '1224444577', '2333567777', '2334444577', '2334455677', '2344455677', '2446777777', '2577777788', '12233344556', '12234445677', '12244445677', '23334445677', '23335555677', '23335666677', '23344445677', '23444555556', '23444555558', '23444556666', '23444556888', '24455566666', '24455588888', '122334555677', '122334666677', '122355556677', '122444455556', '122444456666', '233355556677', '233356777777', '233444455556', '233444456666', '233445555566', '234445555566', '234445567777', '244555667777', '244555777788', '244666777788', '255556777788', '1223334455677', '1223346777777', '1223444555566', '1223577777788', '1224444555566', '1224444567777', '2333444555566', '2333555566666', '2333555588888', '2333577777788', '2334444555566', '2334444567777', '2334455777788', '2344455777788', '2566666677788', '12233455566666', '12233455588888', '12234445777788', '12244445777788', '23334445777788', '23335555667777', '23335555777788', '23335666777788', '23344445777788', '23444555556677', '23444556666677', '23444557788888', '23466666677788', '24466666677788', '122333445555566', '122334555667777', '122334555777788', '122334666777788', '122355556777788', '122444455556677', '233355556777788', '233444455556677', '234445566666678', '234445566777777', '234445577777788', '244555666667888', '244555677777788', '244666666788888', '255556666788888', '1223334455777788', '1223566666677788', '1224444577777788', '2333566666677788', '2334444577777788', '2344455555666666', '2344455555688888', '2446666667777788', '2555566666677777', '12233366666677788', '12233466666677788', '12244555556666667', '23334555556666667', '23335555666667888', '23335555677777788', '23335666666788888', '23344555556666667', '23444555556666667', '23444555556667777', '23444555556777788', '23444556666777788', '122334555666667888', '122334555677777788', '122334666666788888', '122355556666788888', '122444455556777788', '233355556666788888', '233356666667777788', '233444455556777788', '234445566666677788', '234445566666777888', '244555666677788888', '244666667778888888', '255556667778888888', '1223346666667777788', '1223555566666677777', '1224444566666677788', '2333555566666677777', '2334444566666677788', '2334455555666666777', '2344455555666666777', '2445556666667777777', '2446666677777778888', '2555566666777777788', '2566666677777778888', '12233344555556666667', '12234445555666666777', '12244445555666666777', '12244555556666677788', '23334445555666666777', '23334555556666677788', '23335555666677788888', '23335666667778888888', '23344445555666666777', '23344555556666677788', '23444555556666667888', '23444555556666677788', '23444555556666788888', '23444555556677777788', '122334555666677788888', '122334666667778888888', '122355556667778888888', '122444455556666788888', '233355556666667777777', '233355556667778888888', '233356666677777778888', '233444455556666788888', '234445555566666677777', '234445566667777788888', '244555666777778888888', '1223334455555666666777', '1223345556666667777777', '1223346666677777778888', '1223555566666777777788', '1223566666677777778888', '1224444555566666677777', '2333555566666777777788', '2333566666677777778888', '2334444555566666677777', '2334455555666667777788', '2344455555666667777788', '12233344555556666677788', '12234445555666667777788', '12244445555666667777788', '23334445555666667777788', '23335555666777778888888', '23344445555666667777788', '23444555556666677788888', '23444555556667778888888', '23444556666667778888888', '122334555666777778888888', '122444455556667778888888', '233444455556667778888888', '234445555566666777777788', '234445566666677777778888', '234445566677777778888888', '1223334455555666667777788', '1224444555566666777777788', '1224444566666677777778888', '2334444555566666777777788', '2334444566666677777778888', '2334455555666677777778888', '2344455555666677777778888', '12234445555666677777778888', '12244445555666677777778888', '23334445555666677777778888', '23344445555666677777778888', '23444555556666777778888888', '1223334455555666677777778888']
4 ['15', '22', '133', '134', '1577', '2235', '13477', '22333', '22334', '134444', '155556', '156666', '223577', '1334455', '1345556', '1567777', '2233377', '2233477', '2234445', '2244445', '2244556', '13334445', '13334556', '13344556', '22334444', '22334555', '22334666', '22334888', '22355556', '22356666', '155556677', '223334455', '223335556', '223345556', '223347777', '223567777', '224444577', '1334455677', '1577777788', '2233344556', '2234445677', '2244445677', '13334445677', '22334555677', '22334666677', '22355556677', '22444455556', '22444456666', '133445555566', '155556777788', '223334455677', '223346777777', '223444555566', '223577777788', '224444555566', '224444567777', '1333444555566', '1334455777788', '1566666677788', '2233455566666', '2233455588888', '2234445777788', '2244445777788', '13334445777788', '13466666677788', '22333445555566', '22334555667777', '22334555777788', '22334666777788', '22355556777788', '22444455556677', '155556666788888', '223334455777788', '223566666677788', '224444577777788', '1555566666677777', '2233366666677788', '2233466666677788', '2244555556666667', '13334555556666667', '13344555556666667', '22334555666667888', '22334555677777788', '22334666666788888', '22355556666788888', '22444455556777788', '155556667778888888', '223346666667777788', '223555566666677777', '224444566666677788', '1334455555666666777', '1555566666777777788', '1566666677777778888', '2233344555556666667', '2234445555666666777', '2244445555666666777', '2244555556666677788', '13334445555666666777', '13334555556666677788', '13344555556666677788', '22334555666677788888', '22334666667778888888', '22355556667778888888', '22444455556666788888', '223334455555666666777', '223345556666667777777', '223346666677777778888', '223555566666777777788', '223566666677777778888', '224444555566666677777', '1334455555666667777788', '2233344555556666677788', '2234445555666667777788', '2244445555666667777788', '13334445555666667777788', '22334555666777778888888', '22444455556667778888888', '223334455555666667777788', '224444555566666777777788', '224444566666677777778888', '1334455555666677777778888', '2234445555666677777778888', '2244445555666677777778888', '13334445555666677777778888', '223334455555666677777778888']
1 ['1', '223', '224444', '22334556', '22334555556666667', '22334555556666677788']
['12233344445556667778888888']
cost:            2, len=     1, g(1) = 1+9*0
cost:            2, len=     1, g(2) = 2+9*0
cost:            2, len=     1, g(3) = 5+9*0
cost:            2, len=     2, g(4) = 15+9*0
cost:            2, len=     2, g(5) = 25+9*0
cost:            2, len=     1, g(6) = 3+9*0
cost:            2, len=     2, g(7) = 13+9*0
cost:            2, len=     2, g(8) = 23+9*0
cost:            2, len=     1, g(9) = 6+9*0
cost:            3, len=     2, g(10) = 16+9*0
cost:            3, len=     2, g(11) = 26+9*0
cost:            6, len=     2, g(12) = 44+9*0
cost:            2, len=     2, g(12) = 5+9*1
Best result for i=12 is 44+9*0
cost:            6, len=     3, g(13) = 144+9*0
cost:            2, len=     3, g(13) = 15+9*1
Best result for i=13 is 144+9*0
cost:            7, len=     3, g(14) = 256+9*0
cost:            2, len=     3, g(14) = 25+9*1
Best result for i=14 is 256+9*0
cost:            4, len=     2, g(15) = 36+9*0
cost:            4, len=     3, g(16) = 136+9*0
cost:            4, len=     3, g(17) = 236+9*0
cost:            8, len=     2, g(18) = 67+9*0
cost:            2, len=     2, g(18) = 6+9*1
Best result for i=18 is 67+9*0
cost:            9, len=     3, g(19) = 167+9*0
cost:            3, len=     3, g(19) = 16+9*1
Best result for i=19 is 167+9*0
cost:            9, len=     3, g(20) = 267+9*0
cost:            3, len=     3, g(20) = 26+9*1
Best result for i=20 is 267+9*0
cost:           20, len=     3, g(21) = 446+9*0
cost:            5, len=     3, g(21) = 34+9*1
Best result for i=21 is 34+9*1
cost:           20, len=     4, g(22) = 1446+9*0
cost:            5, len=     4, g(22) = 134+9*1
Best result for i=22 is 134+9*1
cost:           25, len=     4, g(23) = 2567+9*0
cost:            5, len=     4, g(23) = 234+9*1
Best result for i=23 is 234+9*1
cost:           15, len=     3, g(24) = 367+9*0
cost:            3, len=     2, g(24) = 4+9*1
Best result for i=24 is 4+9*1
cost:           15, len=     4, g(25) = 1367+9*0
cost:            3, len=     3, g(25) = 14+9*1
Best result for i=25 is 14+9*1
cost:           15, len=     4, g(26) = 2367+9*0
cost:            3, len=     3, g(26) = 24+9*1
Best result for i=26 is 24+9*1
cost:           34, len=     3, g(27) = 788+9*0
cost:            1, len=     1, g(27) = 9*1
Best result for i=27 is 0+9*1
cost:           35, len=     4, g(28) = 1788+9*0
cost:            2, len=     2, g(28) = 1+9*1
Best result for i=28 is 1+9*1
cost:           35, len=     4, g(29) = 2788+9*0
cost:            2, len=     2, g(29) = 2+9*1
Best result for i=29 is 2+9*1
cost:           62, len=     4, g(30) = 4488+9*0
cost:            3, len=     3, g(30) = 12+9*1
cost:            2, len=     3, g(30) = 5+9*2
Best result for i=30 is 12+9*1
cost:           62, len=     5, g(31) = 14488+9*0
cost:            3, len=     3, g(31) = 22+9*1
Best result for i=31 is 22+9*1
cost:           96, len=     6, g(32) = 122788+9*0
cost:            3, len=     4, g(32) = 122+9*1
cost:            2, len=     4, g(32) = 25+9*2
Best result for i=32 is 122+9*1
cost:           54, len=     4, g(33) = 3788+9*0
cost:            2, len=     2, g(33) = 3+9*1
Best result for i=33 is 3+9*1
cost:           54, len=     5, g(34) = 13788+9*0
cost:            2, len=     3, g(34) = 13+9*1
Best result for i=34 is 13+9*1
cost:           54, len=     5, g(35) = 23788+9*0
cost:            2, len=     3, g(35) = 23+9*1
Best result for i=35 is 23+9*1
cost:          210, len=     6, g(36) = 123788+9*0
cost:           13, len=     4, g(36) = 123+9*1
cost:            5, len=     4, g(36) = 35+9*2
Best result for i=36 is 123+9*1
cost:          247, len=     7, g(37) = 1333788+9*0
cost:           16, len=     5, g(37) = 1333+9*1
cost:            6, len=     5, g(37) = 135+9*2
Best result for i=37 is 1333+9*1
cost:          591, len=     8, g(38) = 23577788+9*0
cost:           41, len=     6, g(38) = 12247+9*1
cost:            6, len=     5, g(38) = 235+9*2
Best result for i=38 is 235+9*2
cost:         1084, len=     8, g(39) = 44666788+9*0
cost:           21, len=     4, g(39) = 447+9*1
Best result for i=39 is 447+9*1
cost:         1084, len=     9, g(40) = 144666788+9*0
cost:           21, len=     5, g(40) = 1447+9*1
Best result for i=40 is 1447+9*1
cost:         2214, len=    11, g(41) = 12245666788+9*0
cost:          133, len=     7, g(41) = 235567+9*1
cost:           96, len=     7, g(41) = 2355+9*3
Best result for i=41 is 235567+9*1
cost:         4535, len=    12, g(42) = 123345666788+9*0
cost:          109, len=     6, g(42) = 34447+9*1
Best result for i=42 is 34447+9*1
cost:         5562, len=    13, g(43) = 1344466677788+9*0
cost:          109, len=     7, g(43) = 134447+9*1
Best result for i=43 is 134447+9*1
cost:        12082, len=    16, g(44) = 1224556678888888+9*0
cost:          134, len=     7, g(44) = 237888+9*1
Best result for i=44 is 237888+9*1
cost:        17632, len=    17, g(45) = 12334556678888888+9*0
cost:          423, len=     8, g(45) = 1237888+9*1
Best result for i=45 is 1237888+9*1
cost:        19589, len=    18, g(46) = 134445667778888888+9*0
cost:          491, len=     9, g(46) = 13337888+9*1
Best result for i=46 is 13337888+9*1
cost:        37390, len=    26, g(47) = 12233344445556667778888888+9*0
cost:         1421, len=    11, g(47) = 1224777888+9*1
cost:          588, len=    10, g(47) = 23568888+9*2
cost:          636, len=    10, g(47) = 23578+9*5
Best result for i=47 is 23568888+9*2
cost:        43451, len=    12, g(48) = 12334777888+9*1
cost:         1304, len=    11, g(48) = 123568888+9*2
cost:         2050, len=    11, g(48) = 123578+9*5
Best result for i=48 is 123568888+9*2
cost:        48069, len=    15, g(49) = 13444556777888+9*1
cost:         1479, len=    12, g(49) = 1333568888+9*2
cost:         2480, len=    12, g(49) = 1333578+9*5
Best result for i=49 is 1333568888+9*2
cost:        68342, len=    22, g(50) = 122456666667788888888+9*1
cost:         3422, len=    14, g(50) = 122456778888+9*2
cost:         5701, len=    14, g(50) = 122457778+9*5
Best result for i=50 is 122456778888+9*2
cost:        72879, len=    23, g(51) = 1233456666667788888888+9*1
cost:         5559, len=    14, g(51) = 344466668888+9*2
cost:        11389, len=    14, g(51) = 445788+9*8
Best result for i=51 is 344466668888+9*2
cost:        86201, len=    15, g(52) = 1344466668888+9*2
cost:        13309, len=    15, g(52) = 1445788+9*8
Best result for i=52 is 1344466668888+9*2
cost:       113768, len=    25, g(53) = 12245555566777777888888+9*2
cost:        76238, len=    22, g(53) = 12245555566666688+9*5
cost:        25449, len=    17, g(53) = 122455788+9*8
cost:         1151, len=    17, g(53) = 236667+9*11
Best result for i=53 is 122455788+9*8
cost:       117113, len=    26, g(54) = 123345555566777777888888+9*2
cost:        90983, len=    23, g(54) = 123345555566666688+9*5
cost:        39269, len=    18, g(54) = 1233455788+9*8
cost:         3599, len=    18, g(54) = 1236667+9*11
Best result for i=54 is 1233455788+9*8
cost:       112273, len=    27, g(55) = 1344455556666677778888+9*5
cost:        61647, len=    19, g(55) = 13444577788+9*8
cost:         4262, len=    19, g(55) = 13336667+9*11
Best result for i=55 is 13336667+9*11
cost:       100886, len=    27, g(56) = 1223334444555677788+9*8
cost:        40662, len=    23, g(56) = 122455566667+9*11
cost:         7617, len=    23, g(56) = 2357+9*19
Best result for i=56 is 122455566667+9*11
cost:        87076, len=    24, g(57) = 1233455566667+9*11
cost:        17804, len=    24, g(57) = 12357+9*19
Best result for i=57 is 1233455566667+9*11
cost:        48081, len=    27, g(58) = 13444558888888+9*13
cost:        19519, len=    25, g(58) = 133357+9*19
Best result for i=58 is 133357+9*19
cost:       114845, len=    40, g(59) = 122333444456667777778888+9*16
cost:        69055, len=    31, g(59) = 122333444457+9*19
cost:         5326, len=    30, g(59) = 12245667+9*22
Best result for i=59 is 12245667+9*22
cost:       101414, len=    37, g(60) = 123345666666777788+9*19
cost:        38173, len=    31, g(60) = 123345667+9*22
Best result for i=60 is 123345667+9*22
cost:        82228, len=    32, g(61) = 1344466777+9*22
cost:        78694, len=    51, g(62) = 122333444455555666678888888+9*24
cost:        82561, len=    41, g(62) = 12245555588888+9*27
Best result for i=62 is 12245555588888+9*27
cost:        92074, len=    42, g(63) = 123345555588888+9*27
cost:        83243, len=    66, g(64) = 13444555568+9*55
cost:       107221, len=   103, g(65) = 122333444455566888888+9*82
cost:        87080, len=   123, g(66) = 1233455566688+9*110
cost:        59821, len=   155, g(67) = 134445566668888888+9*137
cost:       100832, len=   184, g(68) = 1223334444566666888+9*165
cost:        67494, len=   212, g(69) = 12334566666688888888+9*192
cost:        82241, len=   230, g(70) = 1344478888+9*220
cost:        91541, len=   264, g(71) = 1223334444555557+9*248
cost:        98231, len=   292, g(72) = 12334555556788888+9*275
cost:        90916, len=   566, g(73) = 134445555666778+9*551
cost:       119066, len=   853, g(74) = 122333444455566666777888888+9*826
cost:        92030, len=  1117, g(75) = 123345557777788+9*1102
cost:        71934, len=  1399, g(76) = 1344455667777778888888+9*1377
cost:       116634, len=  1678, g(77) = 1223334444566667777777888+9*1653
cost:        85170, len=  1941, g(78) = 123345666666+9*1929
cost:        86221, len=  2217, g(79) = 1344467788888+9*2204
cost:       107085, len=  2501, g(80) = 122333444455555667778+9*2480
cost:       117105, len=  2779, g(81) = 123345555566667777888888+9*2755
cost:        93785, len=  5527, g(82) = 1344455556678888+9*5511
cost:       104122, len=  8287, g(83) = 12233344445557777778+9*8267
cost:        75025, len= 11045, g(84) = 12334555666667788888888+9*11022
cost:       112250, len= 13800, g(85) = 1344455666777777788888+9*13778
cost:       100854, len= 16553, g(86) = 1223334444567777888+9*16534
cost:        87036, len= 19303, g(87) = 1233456666668+9*19290
cost:        69224, len= 22066, g(88) = 134446666777778888888+9*22045
cost:       112549, len= 24824, g(89) = 12233344445555567788888+9*24801
cost:       117088, len= 27581, g(90) = 123345555566666677777788+9*27557
cost:       117883, len= 55139, g(91) = 1344455556666667777788888+9*55114
cost:        80474, len= 82702, g(92) = 1223334444555666666777788888888+9*82671
cost:       104710, len=110248, g(93) = 1233455566666677788+9*110229
cost:       106608, len=137806, g(94) = 13444556666667788888+9*137786
cost:        77712, len=165369, g(95) = 12233344445666666788888888+9*165343
cost:        89309, len=192915, g(96) = 12334566666688+9*192901
cost:       112191, len=220480, g(97) = 1344466666677777778888+9*220458
cost:        80614, len=248048, g(98) = 122333444455555666667777778888888+9*248015
cost:       110744, len=275594, g(99) = 123345555566666777778+9*275573
cost:       103460, len=551165, g(100) = 1344455556666777888+9*551146
cost:       110090, len=826741, g(101) = 1223334444555666788888+9*826719
cost:        75035, len=1102315, g(102) = 12334555667777777888888+9*1102292
cost:        69285, len=1377886, g(103) = 134445567777788888888+9*1377865
cost:        89043, len=1653454, g(104) = 122333444457778+9*1653439
cost:        91962, len=1929027, g(105) = 123345666666888+9*1929012
cost:       106567, len=2204605, g(106) = 13444666667777778888+9*2204585
cost:       119776, len=2480186, g(107) = 1223334444555556667777888888+9*2480158
cost:        72968, len=2755753, g(108) = 1233455555667788888888+9*2755731
cost:        77569, len=5511488, g(109) = 1344455556666677778888888+9*5511463
cost:        78763, len=8267222, g(110) = 122333444455567777777888888+9*8267195
cost:       104727, len=11022946, g(111) = 1233455566667888888+9*11022927
cost:        93779, len=13778675, g(112) = 1344455777788888+9*13778659
cost:       114845, len=16534415, g(113) = 122333444456667777778888+9*16534391
cost:        94931, len=19290139, g(114) = 1233456666668888+9*19290123
cost:        86212, len=22045868, g(115) = 1344466777888+9*22045855
cost:       117948, len=24801613, g(116) = 12233344445555566667777788+9*24801587
cost:        85257, len=27557331, g(117) = 123345555588+9*27557319
cost:        88407, len=55114652, g(118) = 13444555568888+9*55114638
cost:       107221, len=82671978, g(119) = 122333444455566888888+9*82671957
cost:        64415, len=110229295, g(120) = 1233455566688888888+9*110229276
cost:        84540, len=137786608, g(121) = 134445566668+9*137786596
cost:       100832, len=165343934, g(122) = 1223334444566666888+9*165343915
cost:        98122, len=192901251, g(123) = 12334566666688888+9*192901234
cost:        45909, len=220458566, g(124) = 1344478888888+9*220458553
cost:        91541, len=248015889, g(125) = 1223334444555557+9*248015873
cost:        89409, len=275573206, g(126) = 12334555556788+9*275573192
cost:       100172, len=551146402, g(127) = 134445555666778888+9*551146384
cost:       119066, len=826719603, g(128) = 122333444455566666777888888+9*826719576
cost:        70407, len=1102292789, g(129) = 123345557777788888888+9*1102292768
cost:        93761, len=1377865977, g(130) = 1344455667777778+9*1377865961
cost:       116634, len=1653439178, g(131) = 1223334444566667777777888+9*1653439153
cost:       101418, len=1929012363, g(132) = 123345666666888888+9*1929012345
cost:        53402, len=2204585553, g(133) = 1344467788888888+9*2204585537
cost:       107085, len=2480158751, g(134) = 122333444455555667778+9*2480158730
cost:       110753, len=2755731943, g(135) = 123345555566667777888+9*2755731922
cost:        63157, len=5511463863, g(136) = 1344455556678888888+9*5511463844
cost:       104122, len=8267195787, g(137) = 12233344445557777778+9*8267195767
cost:       107839, len=11022927709, g(138) = 12334555666667788888+9*11022927689
cost:        77549, len=13778659636, g(139) = 1344455666777777788888888+9*13778659611
cost:       100854, len=16534391553, g(140) = 1223334444567777888+9*16534391534
cost:        64370, len=19290123475, g(141) = 1233456666668888888+9*19290123456
cost:        90835, len=22045855394, g(142) = 134446666777778+9*22045855379
cost:       112549, len=24801587324, g(143) = 12233344445555567788888+9*24801587301
cost:        80534, len=27557319253, g(144) = 123345555566666677777788888888+9*27557319223
cost:        79957, len=55114638475, g(145) = 1344455556666667777788888888+9*55114638447
cost:        80474, len=82671957702, g(146) = 1223334444555666666777788888888+9*82671957671
cost:        78056, len=110229276920, g(147) = 1233455566666677788888888+9*110229276895
cost:        74198, len=137786596142, g(148) = 13444556666667788888888+9*137786596119
cost:        77712, len=165343915369, g(149) = 12233344445666666788888888+9*165343915343
cost:        67494, len=192901234587, g(150) = 12334566666688888888+9*192901234567
cost:        77503, len=220458553816, g(151) = 1344466666677777778888888+9*220458553791
cost:        80614, len=248015873048, g(152) = 122333444455555666667777778888888+9*248015873015
cost:        79714, len=275573192266, g(153) = 123345555566666777778888888+9*275573192239
cost:       112282, len=551146384501, g(154) = 1344455556666777888888+9*551146384479
cost:       110090, len=826719576741, g(155) = 1223334444555666788888+9*826719576719
cost:       107857, len=1102292768979, g(156) = 12334555667777777888+9*1102292768959
cost:        90908, len=1377865961214, g(157) = 134445567777788+9*1377865961199
cost:        89043, len=1653439153454, g(158) = 122333444457778+9*1653439153439
cost:        85170, len=1929012345691, g(159) = 123345666666+9*1929012345679
cost:        74157, len=2204585537941, g(160) = 13444666667777778888888+9*2204585537918
cost:       119776, len=2480158730186, g(161) = 1223334444555556667777888888+9*2480158730158
cost:       104788, len=2755731922417, g(162) = 1233455555667788888+9*2755731922398
cost:       103452, len=5511463844816, g(163) = 1344455556666677778+9*5511463844797
cost:        78763, len=8267195767222, g(164) = 122333444455567777777888888+9*8267195767195
cost:        94976, len=11022927689610, g(165) = 1233455566667888+9*11022927689594
cost:        63137, len=13778659612011, g(166) = 1344455777788888888+9*13778659611992
cost:       114845, len=16534391534415, g(167) = 122333444456667777778888+9*16534391534391
cost:        87036, len=19290123456803, g(168) = 1233456666668+9*19290123456790
cost:        93715, len=22045855379204, g(169) = 1344466777888888+9*22045855379188
cost:       117948, len=24801587301613, g(170) = 12233344445555566667777788+9*24801587301587
cost:        61215, len=27557319224003, g(171) = 123345555588888888+9*27557319223985
cost:        56596, len=55114638447988, g(172) = 13444555568888888+9*55114638447971
cost:       107221, len=82671957671978, g(173) = 122333444455566888888+9*82671957671957
cost:        94983, len=110229276895959, g(174) = 1233455566688888+9*110229276895943
cost:        90892, len=137786596119944, g(175) = 134445566668888+9*137786596119929
cost:       100832, len=165343915343934, g(176) = 1223334444566666888+9*165343915343915
cost:        89309, len=192901234567915, g(177) = 12334566666688+9*192901234567901
cost:        80893, len=220458553791894, g(178) = 1344478+9*220458553791887
cost:        91541, len=248015873015889, g(179) = 1223334444555557+9*248015873015873
cost:        67598, len=275573192239878, g(180) = 12334555556788888888+9*275573192239858
cost:        69313, len=551146384479738, g(181) = 134445555666778888888+9*551146384479717
cost:       119066, len=826719576719603, g(182) = 122333444455566666777888888+9*826719576719576
cost:       101484, len=1102292768959453, g(183) = 123345557777788888+9*1102292768959435
cost:       103445, len=1377865961199313, g(184) = 1344455667777778888+9*1377865961199294
cost:       116634, len=1653439153439178, g(185) = 1223334444566667777777888+9*1653439153439153
cost:        91962, len=1929012345679027, g(186) = 123345666666888+9*1929012345679012
cost:        82234, len=2204585537918881, g(187) = 1344467788+9*2204585537918871
cost:       107085, len=2480158730158751, g(188) = 122333444455555667778+9*2480158730158730
cost:       101502, len=2755731922398607, g(189) = 123345555566667777+9*2755731922398589
cost:        86275, len=5511463844797191, g(190) = 1344455556678+9*5511463844797178
cost:       104122, len=8267195767195787, g(191) = 12233344445557777778+9*8267195767195767
cost:        98157, len=11022927689594373, g(192) = 12334555666667788+9*11022927689594356
cost:       103437, len=13778659611992964, g(193) = 1344455666777777788+9*13778659611992945
cost:       100854, len=16534391534391553, g(194) = 1223334444567777888+9*16534391534391534
cost:        94931, len=19290123456790139, g(195) = 1233456666668888+9*19290123456790123
cost:       100089, len=22045855379188730, g(196) = 134446666777778888+9*22045855379188712
cost:       112549, len=24801587301587324, g(197) = 12233344445555567788888+9*24801587301587301
cost:       120028, len=27557319223985917, g(198) = 123345555566666677777788888+9*27557319223985890
cost:       112264, len=55114638447971803, g(199) = 1344455556666667777788+9*55114638447971781
cost:        80474, len=82671957671957702, g(200) = 1223334444555666666777788888888+9*82671957671957671
sum_sg(200) is 2728174603174619234 computed in 61.76 seconds
"""
