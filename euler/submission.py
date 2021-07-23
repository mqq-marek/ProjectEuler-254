"""
Euler challenge from HackerRank https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem

Final submission

"""
import cProfile
import io
import math
import pstats
import time
from collections import defaultdict
from functools import reduce
from itertools import zip_longest

DEBUG = False

PREFIX_V = {}
PREFIX_INFO = defaultdict(list)
sg_cache = {}


def digits_gen(n):
    """
    Yields number n digits in reverse sequence. For n = 342 sequence is 2, 4, 3
    :param n:
    :return:
    """
    '''
    n, d = divmod(n, 10)
    yield d
    while n:
        n, d = divmod(n, 10)
        yield d

    while True:
        yield n % 10
        n //= 10
        if not n:
            break
    '''
    return (ord(ch) - ord('0') for ch in str(n)[::-1])


def digits_sum(n):
    return sum([d for d in digits_gen(n)])


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
                                    PREFIX_INFO[fs_ % 9].append((prefix, list(digits_gen(f_))))
                                    PREFIX_V[f_] = prefix
    for k in PREFIX_INFO.keys():
        PREFIX_INFO[k].sort(key=lambda x: int(x[0]))


FACTORIALS = [math.factorial(i) for i in range(10)]
FACTORIAL9_DIGITS = [d for d in digits_gen(FACTORIALS[9])]


def find_fn(digits_sum):
    cost = 0
    for i_str in gen_prospect_fn(digits_sum):
        cost += 1
        i = int(i_str)
        n9 = i // FACTORIALS[9]
        distance = i - n9 * FACTORIALS[9]
        if distance <= 299999:
            return i_str, n9, distance
            cost = 0
    raise Exception('fn not found')


def gen_prospect_fn(digits_sum):
    """ Build suffix which gives g(i) = i """
    n9, d = divmod(digits_sum, 9)
    if d == 0:
        first = ''
        next = '1'
    else:
        first = chr(d+ord('0'))
        next = chr(d + 1 + ord('0'))

    yield first + '9' * n9
    for i in range(n9):
        yield next+'9'*i+'8'+'9'*(n9-i-1)


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

    def missing_prefix(self):
        """ Return number value as int """
        return 999999 - reduce(lambda x, y: x * 10 + y, self.num[:6][::-1])

    def digits_sum(self):
        """
        Sum of all digits.
        """
        return sum(self.num)

    def combined_digits_sum(self, other_num, sum6):
        """
        Sum of all digits.
        """
        total = 0
        carry = 0
        for i, (a, b) in enumerate(zip_longest(self.num, other_num, fillvalue=0)):
            if i == 6 and carry == 0:
                return total + sum6

            s = a + b + carry
            carry = 0
            if s > 9:
                s -= 10
                carry = 1
            total += s
        if carry:
            total += 1
        return total

    def suffix_digits_sum(self):
        """
        Sum of suffix only digits in  n.
        Does not include 5 least significant digits and max 7 on the 6th least significant digits.
        :return:
        """
        suffix_sum = min(7, sum(self.num[5:6])) + self.suffix6_digits_sum()
        return suffix_sum

    def suffix6_digits_sum(self):
        """
        Sum of suffix only digits in  n.
        Does not include 5 least significant digits and max 7 on the 6th least significant digits.
        :return:
        """
        return sum(self.num[6:])

    def add2(self, number):
        self.num = list(digits_gen(self.value + number))

    def add(self, number):
        new = []
        carry = 0
        for a, b in zip_longest(self.num, number, fillvalue=0):
            s = a + b + carry
            carry = 0
            if s > 9:
                s -= 10
                carry = 1
            new.append(s)
        if carry:
            new.append(1)
        self.num = new

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

        def update_value(need_digits_sum):
            """ Increase digits in number for reaching needed digits sum value. """
            # try to increase digit po position 5 up to 7
            # need_digits_sum, self.num[5] = increase_digit(need_digits_sum, self.num[5], max_digit=7)
            # increase other digits up to 9 if necessary
            max_digit = 7
            for i in range(5, len(self.num)):
                inc = min(need_digits_sum, max_digit - self.num[i])
                max_digit = 9
                # need_digits_sum, self.num[i] = increase_digit(need_digits_sum, self.num[i])
                need_digits_sum, self.num[i] = need_digits_sum - inc, self.num[i] + inc
                if need_digits_sum == 0:
                    return 0
            return need_digits_sum

        def next_value_with_sum(needed):
            """ Find next number value with needed suffix sum. """
            still_needed = needed - self.suffix_digits_sum()
            while still_needed > 0:
                still_needed = update_value(still_needed)
                if still_needed:
                    # increase number length if not fulfill with the current number length
                    self.num.append(1)
                    for i in range(0, len(self.num) - 1):
                        self.num[i] = 0
                    still_needed = needed - self.suffix_digits_sum()
                    # print(f'Needed: {old_needed} gives: {self.value} missing: {still_needed}')

        def make_suffix_value():
            """ Round value up to next 9! multiply. """
            self.n = max(self.n + 1, self.value // FACTORIALS[9])
            self.num = list(digits_gen(self.n * FACTORIALS[9]))
            return self.suffix_digits_sum()

        # Get next suffix value [one 9 digit more so sum is increase by 9!]
        self.add(FACTORIAL9_DIGITS)
        # self.add2(FACTORIALS[9])
        self.n += 1
        suffix_sum = self.suffix_digits_sum()
        if DEBUG:
            pass
            # print(f'Suffix: len:{self.n}, sum: {self.digits_sum()}, s_sum:{suffix_sum}, {self.value}')

        while suffix_sum < sum_needed - 47:
            next_value_with_sum(sum_needed - 47)
            suffix_sum = make_suffix_value()
            if DEBUG:
                pass
                # print(f'Suffix: len:{self.n}, sum: {self.digits_sum()}, s_sum:{suffix_sum}, {self.value}')

        self.sum = suffix_sum
        assert self.value % FACTORIALS[9] == 0

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
                    print(f'cost: {cost:12}, '
                          f'f(n)={f_suffix.value: 40}, '
                          f'len={f_suffix.n:8}, '
                          f'g({i:5})=9*{f_suffix.n}',
                          )
                return 0

            needed_prefix_sum = i - f_sum
            prefix_part_sum = sum(f_suffix.num[0:5])
            max_prefix_sum = 47 - prefix_part_sum
            if needed_prefix_sum > max_prefix_sum:
                f_suffix.next(i)
                continue
            suffix6_sum = f_suffix.suffix6_digits_sum()
            if i - suffix6_sum == 54:
                if DEBUG:
                    print(f'cost: {-1:12}, '
                          f'f(n)={f_suffix.value + f_suffix.missing_prefix(): 40}, '
                          f'len={len(PREFIX_V[f_suffix.missing_prefix()]) + f_suffix.n:8}, '
                          f'g({i:5})={PREFIX_V[f_suffix.missing_prefix()]}+9*{f_suffix.n}')
                return PREFIX_V[f_suffix.missing_prefix()]
            prefixes = PREFIX_INFO.get(needed_prefix_sum % 9, [])
            # suffix_value = f_suffix.value

            for prefix in prefixes:
                cost += 1
                # if digits_sum(suffix_value + F_PREFIX[prefix]) == i:
                if f_suffix.combined_digits_sum(prefix[1], suffix6_sum) == i:
                    # print(i, i-suffix6_sum, prefix[0])
                    if DEBUG:
                        print(f'cost: {cost:12}, '
                              f'f(n)={f_suffix.value + f(prefix[0]): 40}, '
                              f'len={len(str(prefix[0])) + f_suffix.n:8}, '
                              f'g({i:5})={str(prefix[0])}+9*{f_suffix.n}')
                    return prefix[0]
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
                    print(f'cost: {cost:12}, '
                          f'f(n)={f_suffix.value: 40}, '
                          f'len={f_suffix.n:8}, '
                          f'g({i:5})=9*{f_suffix.n}')
                return 0

            needed_prefix_sum = i - f_sum
            while needed_prefix_sum < 0:
                needed_prefix_sum += 9
            prefix_part_sum = sum(f_suffix.num[0:5])
            max_prefix_sum = 47 - prefix_part_sum
            if needed_prefix_sum > max_prefix_sum:
                # print(f'Too small prefix for i={i}  with 9*{f_suffix.n} and missing digits sum={needed_prefix_sum}')
                f_suffix.next(i)
                continue
            # print(i, f_suffix.value, needed_prefix_sum)
            prefixes = PREFIX_INFO.get(needed_prefix_sum % 9, [])
            # suffix_value = f_suffix.value
            suffix6_sum = f_suffix.suffix6_digits_sum()
            suffix_len = f_suffix.n
            for prefix in prefixes:
                cost += 1
                # print(prefix, f(prefix))
                if len(prefix[0]) + suffix_len > max_cnt:
                    break
                # if digits_sum(suffix_value + F_PREFIX[prefix]) == i:
                if f_suffix.combined_digits_sum(prefix[1], suffix6_sum) == i:
                    if DEBUG:
                        print(f'cost: {cost:12}, '
                              f'f(n)={f_suffix.value + f(prefix[0]): 40}, '
                              f'len={len(str(prefix[0])) + f_suffix.n:8}, '
                              f'g({i:5})={str(prefix[0])}+9*{f_suffix.n}')
                    return prefix[0]
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
            pass
            # print(f'G({i}) starts with suffix len {suffix.n}')
        if sg_cache.get(i):
            continue
        if i >= 70:
            fv, n9, d = find_fn(i)
            prefix = PREFIX_V[d]
            if DEBUG:
                print(f'cost: {-2:12}, '
                      f'f(n)={fv:40}, '
                      f'len={len(prefix) + n9:8}, '
                      f'g({i:5})={prefix}+9*{n9}')
            sg_cache[i] = digits_sum(int(prefix)) + 9 * n9
            if mod:
                sg_cache[i] = sg_cache[i] % mod
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
                if (tmp_len < current_len) or (tmp_len == current_len and prefix_lt_prefix(tmp_prefix, prefix)):
                    prefix = tmp_prefix
                    current_len = tmp_len
                    current_suffix = FDigits(suffix)
            suffix.next(i)

        # sf_cache[i] = str(prefix) + '9' * current_suffix.n
        sg_cache[i] = digits_sum(int(prefix)) + 9 * current_suffix.n
        if mod:
            sg_cache[i] = sg_cache[i] % mod
        if more_results and DEBUG:
            print(f'Best result for i={i} is {str(prefix)}+9*{current_suffix.n}')
        suffix = FDigits(max(0, current_suffix.n - 10))
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


def assert_sg(cache=None):
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
        if sg_cache.get(i):
            if sg_cache.get(i) != sg_sum:
                print(f'Assertion error sg({i}) is {sg_cache.get(i, 0)} while expected {sg_sum}')
        else:
            if cache:
                sg_cache[i] = sg_sum


def hacker_main():
    init_prefixes()
    assert_sg(cache=True)
    q = int(input())
    for _ in range(q):
        n, m = map(int, input().split())
        r = sum_sg_mod(n, m)
        print(r)


def profile_main(size=200):
    with cProfile.Profile() as pr:
        init_prefixes()
        assert_sg(cache=True)
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
    print(f"sum_sg({size}) has length {len(str(total))} last digits are {total % 1000000000000000000000000000000000}"
          f"computed in {pgm_stop - pgm_start:.2f} seconds")
    assert_sg()
    # print computed sg values
    # sg_list = [sg(i) for i in range(1, size+1)]
    # print(sg_list)


if __name__ == "__main__":
    # DEBUG = True
    # hacker_main()
    # profile_main(150000)
    development_main(100)
    exit()
