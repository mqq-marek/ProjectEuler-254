"""
Euler challenge from HackerRank https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem

Speed, speed, ... improvement - Day 4

"""
import cProfile, pstats, io
import math
import time
from collections import defaultdict
from functools import reduce
from itertools import zip_longest
from itertools import combinations

DEBUG = False

PREFIX_INFO = defaultdict(list)
PREFIX_V = {}
# f_cache = {}
# sf_cache = {}
g_cache = {}
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
                                    # F_PREFIX[prefix] = f_
                                    # PREFIXES[fs_ % 9].append(prefix)
                                    PREFIX_V[f_] = prefix
                                    PREFIX_INFO[fs_ % 9].append((prefix, list(digits_gen(f_))))
    for k in PREFIX_INFO.keys():
        PREFIX_INFO[k].sort(key=lambda x: int(x[0]))


FACTORIALS = [math.factorial(i) for i in range(10)]
FACTORIAL9_DIGITS = [d for d in digits_gen(FACTORIALS[9])]


def find_fn(digits_sum):
    for i_str in gen_prospect_fn(digits_sum):
        i = int(i_str)
        n9 = i // FACTORIALS[9]
        distance = i - n9 * FACTORIALS[9]
        return i_str, n9, distance
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

    def prefix_digits_sum(self):
        """
        Sum of prefix part digit.
        """
        suffix_sum = sum(self.num[:6])
        return suffix_sum

    def suffix_digits_sum(self):
        """
        Sum of suffix only digits in  n.
        Does not include 5 least significant digits and max 7 on the 6th least significant digits.
        :return:
        """
        suffix_sum = self.suffix6_digits_sum()
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
        while suffix_sum < sum_needed - 54:
            get_value_with_sum(sum_needed - 54)
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
                    print(f'f(n)={f_suffix.value: 60}, '
                          f'len={f_suffix.n:8}, '
                          f'g({i:5})=9*{f_suffix.n}',
                          )
                return 0

            needed_prefix_sum = i - f_sum
            prefix_part_sum = f_suffix.prefix_digits_sum()
            max_prefix_sum = 54 - prefix_part_sum
            if needed_prefix_sum > max_prefix_sum:
                f_suffix.next(i)
                continue
            suffix6_sum = f_suffix.suffix_digits_sum()
            if (i - suffix6_sum == 54 and
                    PREFIX_V.get(f_suffix.missing_prefix())):
                if DEBUG:
                    print(f'f(n)={f_suffix.value + f_suffix.missing_prefix(): 60}, '
                          f'len={len(PREFIX_V[f_suffix.missing_prefix()]) + f_suffix.n:8}, '
                          f'g({i:5})={PREFIX_V[f_suffix.missing_prefix()]}+9*{f_suffix.n}')
                return PREFIX_V[f_suffix.missing_prefix()]

            prefixes = PREFIX_INFO.get(needed_prefix_sum % 9, [])
            for prefix in prefixes:
                cost += 1
                # if digits_sum(suffix_value + F_PREFIX[prefix]) == i:
                if f_suffix.combined_digits_sum(prefix[1], suffix6_sum) == i:
                    # print(i, i-suffix6_sum, prefix[0])
                    if DEBUG:
                        print(f'f(n)={f_suffix.value + f(prefix[0]): 60}, '
                              f'len={len(str(prefix[0])) + f_suffix.n:8}, '
                              f'g({i:5})={str(prefix[0])}+9*{f_suffix.n}')
                    return prefix[0]
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
                    print(f'f(n)={f_suffix.value: 60}, '
                          f'len={f_suffix.n:8}, '
                          f'g({i:5})=9*{f_suffix.n}')
                return 0

            needed_prefix_sum = i - f_sum
            while needed_prefix_sum < 0:
                needed_prefix_sum += 9
            prefix_part_sum = f_suffix.prefix_digits_sum()
            max_prefix_sum = 54 - prefix_part_sum
            if needed_prefix_sum > max_prefix_sum:
                f_suffix.next(i)
                continue
            prefixes = PREFIX_INFO.get(needed_prefix_sum % 9, [])
            suffix6_sum = f_suffix.suffix6_digits_sum()
            suffix_len = f_suffix.n
            for prefix in prefixes:
                cost += 1
                if len(prefix[0]) + suffix_len > max_cnt:
                    break
                if f_suffix.combined_digits_sum(prefix[1], suffix6_sum) == i:
                    if DEBUG:
                        print(f'f(n)={f_suffix.value + f(prefix[0]): 60}, '
                              f'len={len(str(prefix[0])) + f_suffix.n:8}, '
                              f'g({i:5})={str(prefix[0])}+9*{f_suffix.n}')
                    return prefix[0]
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

        """            
        if i > 250:
            fv, n9, d = find_fn(i)
            prefix = PREFIX_V[d]
            if DEBUG:
                print(f'cost: {-2:12}, '
                      f'f(n)={int(fv):40}, '
                      f'len={len(prefix) + n9:8}, '
                      f'g({i:5})={prefix}+9*{n9}')
            sg_cache[i] = digits_sum(int(prefix)) + 9 * n9
            if mod:
                sg_cache[i] = sg_cache[i] % mod
            g_cache[i] = f"{prefix}:{n9}"
            continue
        """

        more_results = False
        prefix = g_find_first(suffix)
        current_len = len(str(prefix)) + suffix.n
        current_suffix = FDigits(suffix)
        suffix.next(i)
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

        sg_cache[i] = digits_sum(int(prefix)) + 9 * current_suffix.n
        if mod:
            sg_cache[i] = sg_cache[i] % mod
        g_cache[i] = f"{prefix}:{current_suffix.n}"

        if more_results and DEBUG:
            print(f'Best result for i={i} is {str(prefix)}+9*{current_suffix.n}')
        suffix = FDigits(max(0, current_suffix.n - 10))
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


def assert_sg(cache=None):
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
        if sg_cache.get(i):
            if sg_cache.get(i) != sg_sum:
                print(f'Assertion error sg({i}) is {sg_cache.get(i, 0)} while expected {sg_sum}')
        else:
            if cache:
                sg_cache[i] = sg_sum


def dic_as_list(dic, *, seq=True):
    lst = []
    for k in range(1, max(dic.keys())+1):
        if dic.get(k):
            lst.append(dic[k])
        elif seq:
            break
        else:
            lst.append(None)
    return lst

def make_sgi_mod_table(base_value=181):
    # init_prefixes()
    di = defaultdict(list)
    dv = defaultdict(set)
    dist = set()
    for i in range(base_value, 50001):
        x, y, z = find_fn(i)
        dist.add(z)
        if y * 9 > 1000000000000:
            v = y * 9 % 1000000000000
            dv[z].add(v)
        di[z].append(i)
    distances = sorted(list(dist))

    dic = {}
    for d in distances:
        vl = list(dv[d])
        v = ""
        if len(vl) == 1:
            v = str(vl[0])
        else:
            v = vl
        dd = defaultdict(int)
        for i in range(1, len(di[d])):
            dd[di[d][i] - di[d][i - 1]] += 1
        s = ""
        if len(dd) == 1:
            s = list(dd.keys())[0]
        elif len(dd) == 2:
            dic[di[d][1]] = (d, di[d][3] - di[d][1])
            s = di[d][2] - di[d][0]
        else:
            s = dd
        dic[di[d][0]] = (d, s)
    min_pos = min(dic.keys())
    max_pos = max(dic.keys())
    for p in range(min_pos, max_pos):
        d, step = dic[p]
        if p + step < max_pos and not dic.get(p + step):
            dic[p + step] = (d, step)

    sgi_mod_table = []
    for p, (d, s) in sorted(dic.items()):
        sgi_mod_table.append((p, d, PREFIX_V[d], sf(PREFIX_V[d])))
    return sgi_mod_table


def print_const_tables():
    print(f'g_table = {dic_as_list(g_cache)}')
    print(f'sg_table = {dic_as_list(sg_cache)}')
    # prefixes = [sf(p) for p in dic_as_list(PREFIX_V)]
    # print(f'p_table = {prefixes}')
    hook_value = 181
    print(f'sgi_mod_table = {make_sgi_mod_table(hook_value)}')


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
    print(f"sum_sg({size}) has length {len(str(total))} last digits are {total % 1000000000000000} "
          f"computed in {pgm_stop - pgm_start:.2f} seconds")
    assert_sg()
    print_const_tables()


if __name__ == "__main__":
    DEBUG = True
    # hacker_main()
    # profile_main(15000)
    development_main(500)
    exit()

"""
Init prefixes - 6.15 seconds
f(n)=                                                           1, len=       1, g(    1)=1+9*0
f(n)=                                                           2, len=       1, g(    2)=2+9*0
f(n)=                                                         120, len=       1, g(    3)=5+9*0
f(n)=                                                         121, len=       2, g(    4)=15+9*0
f(n)=                                                         122, len=       2, g(    5)=25+9*0
f(n)=                                                           6, len=       1, g(    6)=3+9*0
f(n)=                                                           7, len=       2, g(    7)=13+9*0
f(n)=                                                           8, len=       2, g(    8)=23+9*0
f(n)=                                                         720, len=       1, g(    9)=6+9*0
f(n)=                                                         721, len=       2, g(   10)=16+9*0
f(n)=                                                         722, len=       2, g(   11)=26+9*0
f(n)=                                                          48, len=       2, g(   12)=44+9*0
f(n)=                                                      363000, len=       2, g(   12)=5+9*1
Best result for i=12 is 44+9*0
f(n)=                                                          49, len=       3, g(   13)=144+9*0
f(n)=                                                      363001, len=       3, g(   13)=15+9*1
Best result for i=13 is 144+9*0
f(n)=                                                         842, len=       3, g(   14)=256+9*0
f(n)=                                                      363002, len=       3, g(   14)=25+9*1
Best result for i=14 is 256+9*0
f(n)=                                                         726, len=       2, g(   15)=36+9*0
f(n)=                                                         727, len=       3, g(   16)=136+9*0
f(n)=                                                         728, len=       3, g(   17)=236+9*0
f(n)=                                                        5760, len=       2, g(   18)=67+9*0
f(n)=                                                      363600, len=       2, g(   18)=6+9*1
Best result for i=18 is 67+9*0
f(n)=                                                        5761, len=       3, g(   19)=167+9*0
f(n)=                                                      363601, len=       3, g(   19)=16+9*1
Best result for i=19 is 167+9*0
f(n)=                                                        5762, len=       3, g(   20)=267+9*0
f(n)=                                                      363602, len=       3, g(   20)=26+9*1
Best result for i=20 is 267+9*0
f(n)=                                                         768, len=       3, g(   21)=446+9*0
f(n)=                                                      362910, len=       3, g(   21)=34+9*1
Best result for i=21 is 34+9*1
f(n)=                                                         769, len=       4, g(   22)=1446+9*0
f(n)=                                                      362911, len=       4, g(   22)=134+9*1
Best result for i=22 is 134+9*1
f(n)=                                                        5882, len=       4, g(   23)=2567+9*0
f(n)=                                                      362912, len=       4, g(   23)=234+9*1
Best result for i=23 is 234+9*1
f(n)=                                                        5766, len=       3, g(   24)=367+9*0
f(n)=                                                      362904, len=       2, g(   24)=4+9*1
Best result for i=24 is 4+9*1
f(n)=                                                        5767, len=       4, g(   25)=1367+9*0
f(n)=                                                      362905, len=       3, g(   25)=14+9*1
Best result for i=25 is 14+9*1
f(n)=                                                        5768, len=       4, g(   26)=2367+9*0
f(n)=                                                      362906, len=       3, g(   26)=24+9*1
Best result for i=26 is 24+9*1
f(n)=                                                       85680, len=       3, g(   27)=788+9*0
f(n)=                                                      362880, len=       1, g(   27)=9*1
Best result for i=27 is 0+9*1
f(n)=                                                       85681, len=       4, g(   28)=1788+9*0
f(n)=                                                      362881, len=       2, g(   28)=1+9*1
Best result for i=28 is 1+9*1
f(n)=                                                       85682, len=       4, g(   29)=2788+9*0
f(n)=                                                      362882, len=       2, g(   29)=2+9*1
Best result for i=29 is 2+9*1
f(n)=                                                       80688, len=       4, g(   30)=4488+9*0
f(n)=                                                      362883, len=       3, g(   30)=12+9*1
f(n)=                                                      725880, len=       3, g(   30)=5+9*2
Best result for i=30 is 12+9*1
f(n)=                                                       80689, len=       5, g(   31)=14488+9*0
f(n)=                                                      362884, len=       3, g(   31)=22+9*1
Best result for i=31 is 22+9*1
f(n)=                                                       85685, len=       6, g(   32)=122788+9*0
f(n)=                                                      362885, len=       4, g(   32)=122+9*1
f(n)=                                                      725882, len=       4, g(   32)=25+9*2
Best result for i=32 is 122+9*1
f(n)=                                                       85686, len=       4, g(   33)=3788+9*0
f(n)=                                                      362886, len=       2, g(   33)=3+9*1
Best result for i=33 is 3+9*1
f(n)=                                                       85687, len=       5, g(   34)=13788+9*0
f(n)=                                                      362887, len=       3, g(   34)=13+9*1
Best result for i=34 is 13+9*1
f(n)=                                                       85688, len=       5, g(   35)=23788+9*0
f(n)=                                                      362888, len=       3, g(   35)=23+9*1
Best result for i=35 is 23+9*1
f(n)=                                                       85689, len=       6, g(   36)=123788+9*0
f(n)=                                                      362889, len=       4, g(   36)=123+9*1
f(n)=                                                      725886, len=       4, g(   36)=35+9*2
Best result for i=36 is 123+9*1
f(n)=                                                       85699, len=       7, g(   37)=1333788+9*0
f(n)=                                                      362899, len=       5, g(   37)=1333+9*1
f(n)=                                                      725887, len=       5, g(   37)=135+9*2
Best result for i=37 is 1333+9*1
f(n)=                                                       95888, len=       8, g(   38)=23577788+9*0
f(n)=                                                      367949, len=       6, g(   38)=12247+9*1
f(n)=                                                      725888, len=       5, g(   38)=235+9*2
Best result for i=38 is 235+9*2
f(n)=                                                       87888, len=       8, g(   39)=44666788+9*0
f(n)=                                                      367968, len=       4, g(   39)=447+9*1
Best result for i=39 is 447+9*1
f(n)=                                                       87889, len=       9, g(   40)=144666788+9*0
f(n)=                                                      367969, len=       5, g(   40)=1447+9*1
Best result for i=40 is 1447+9*1
f(n)=                                                       87989, len=      11, g(   41)=12245666788+9*0
f(n)=                                                      368888, len=       7, g(   41)=235567+9*1
f(n)=                                                     1088888, len=       7, g(   41)=2355+9*3
Best result for i=41 is 235567+9*1
f(n)=                                                       87999, len=      12, g(   42)=123345666788+9*0
f(n)=                                                      367998, len=       6, g(   42)=34447+9*1
Best result for i=42 is 34447+9*1
f(n)=                                                       97999, len=      13, g(   43)=1344466677788+9*0
f(n)=                                                      367999, len=       7, g(   43)=134447+9*1
Best result for i=43 is 134447+9*1
f(n)=                                                      288989, len=      16, g(   44)=1224556678888888+9*0
f(n)=                                                      488888, len=       7, g(   44)=237888+9*1
Best result for i=44 is 237888+9*1
f(n)=                                                      288999, len=      17, g(   45)=12334556678888888+9*0
f(n)=                                                      488889, len=       8, g(   45)=1237888+9*1
Best result for i=45 is 1237888+9*1
f(n)=                                                      298999, len=      18, g(   46)=134445667778888888+9*0
f(n)=                                                      488899, len=       9, g(   46)=13337888+9*1
Best result for i=46 is 13337888+9*1
f(n)=                                                      299999, len=      26, g(   47)=12233344445556667778888888+9*0
f(n)=                                                      498989, len=      11, g(   47)=1224777888+9*1
f(n)=                                                      887888, len=      10, g(   47)=23568888+9*2
f(n)=                                                     1859888, len=      10, g(   47)=23578+9*5
Best result for i=47 is 23568888+9*2
f(n)=                                                      498999, len=      12, g(   48)=12334777888+9*1
f(n)=                                                      887889, len=      11, g(   48)=123568888+9*2
f(n)=                                                     1859889, len=      11, g(   48)=123578+9*5
Best result for i=48 is 123568888+9*2
f(n)=                                                      499999, len=      15, g(   49)=13444556777888+9*1
f(n)=                                                      887899, len=      12, g(   49)=1333568888+9*2
f(n)=                                                     1859899, len=      12, g(   49)=1333578+9*5
Best result for i=49 is 1333568888+9*2
f(n)=                                                      699989, len=      22, g(   50)=122456666667788888888+9*1
f(n)=                                                      897989, len=      14, g(   50)=122456778888+9*2
f(n)=                                                     1869989, len=      14, g(   50)=122457778+9*5
Best result for i=50 is 122456778888+9*2
f(n)=                                                      699999, len=      23, g(   51)=1233456666667788888888+9*1
f(n)=                                                      889998, len=      14, g(   51)=344466668888+9*2
f(n)=                                                     2988888, len=      14, g(   51)=445788+9*8
Best result for i=51 is 344466668888+9*2
f(n)=                                                      889999, len=      15, g(   52)=1344466668888+9*2
f(n)=                                                     2988889, len=      15, g(   52)=1445788+9*8
Best result for i=52 is 1344466668888+9*2
f(n)=                                                      999989, len=      25, g(   53)=12245555566777777888888+9*2
f(n)=                                                     1899989, len=      22, g(   53)=12245555566666688+9*5
f(n)=                                                     2988989, len=      17, g(   53)=122455788+9*8
f(n)=                                                     3998888, len=      17, g(   53)=236667+9*11
Best result for i=53 is 122455788+9*8
f(n)=                                                      999999, len=      26, g(   54)=123345555566777777888888+9*2
f(n)=                                                     1899999, len=      23, g(   54)=123345555566666688+9*5
f(n)=                                                     2988999, len=      18, g(   54)=1233455788+9*8
f(n)=                                                     3998889, len=      18, g(   54)=1236667+9*11
Best result for i=54 is 1233455788+9*8
f(n)=                                                     1999999, len=      27, g(   55)=1344455556666677778888+9*5
f(n)=                                                     2998999, len=      19, g(   55)=13444577788+9*8
f(n)=                                                     3998899, len=      19, g(   55)=13336667+9*11
Best result for i=55 is 13336667+9*11
f(n)=                                                     2999999, len=      27, g(   56)=1223334444555677788+9*8
f(n)=                                                     3999989, len=      23, g(   56)=122455566667+9*11
f(n)=                                                     6899888, len=      23, g(   56)=2357+9*19
Best result for i=56 is 122455566667+9*11
f(n)=                                                     3999999, len=      24, g(   57)=1233455566667+9*11
f(n)=                                                     6899889, len=      24, g(   57)=12357+9*19
Best result for i=57 is 1233455566667+9*11
f(n)=                                                     4999999, len=      27, g(   58)=13444558888888+9*13
f(n)=                                                     6899899, len=      25, g(   58)=133357+9*19
Best result for i=58 is 133357+9*19
f(n)=                                                     5999999, len=      40, g(   59)=122333444456667777778888+9*16
f(n)=                                                     6899999, len=      31, g(   59)=122333444457+9*19
f(n)=                                                     7989989, len=      30, g(   59)=12245667+9*22
Best result for i=59 is 12245667+9*22
f(n)=                                                     6999999, len=      37, g(   60)=123345666666777788+9*19
f(n)=                                                     7989999, len=      31, g(   60)=123345667+9*22
Best result for i=60 is 123345667+9*22
f(n)=                                                     7999999, len=      32, g(   61)=1344466777+9*22
f(n)=                                                     8999999, len=      51, g(   62)=122333444455555666678888888+9*24
f(n)=                                                     9999989, len=      41, g(   62)=12245555588888+9*27
Best result for i=62 is 12245555588888+9*27
f(n)=                                                     9999999, len=      42, g(   63)=123345555588888+9*27
f(n)=                                                    19999999, len=      66, g(   64)=13444555568+9*55
f(n)=                                                    29999999, len=     103, g(   65)=122333444455566888888+9*82
f(n)=                                                    39999999, len=     123, g(   66)=1233455566688+9*110
f(n)=                                                    49999999, len=     155, g(   67)=134445566668888888+9*137
f(n)=                                                    59999999, len=     184, g(   68)=1223334444566666888+9*165
f(n)=                                                    69999999, len=     212, g(   69)=12334566666688888888+9*192
f(n)=                                                    79999999, len=     230, g(   70)=1344478888+9*220
f(n)=                                                    89999999, len=     264, g(   71)=1223334444555557+9*248
f(n)=                                                    99999999, len=     292, g(   72)=12334555556788888+9*275
f(n)=                                                   199999999, len=     566, g(   73)=134445555666778+9*551
f(n)=                                                   299999999, len=     853, g(   74)=122333444455566666777888888+9*826
f(n)=                                                   399999999, len=    1117, g(   75)=123345557777788+9*1102
f(n)=                                                   499999999, len=    1399, g(   76)=1344455667777778888888+9*1377
f(n)=                                                   599999999, len=    1678, g(   77)=1223334444566667777777888+9*1653
f(n)=                                                   699999999, len=    1941, g(   78)=123345666666+9*1929
f(n)=                                                   799999999, len=    2217, g(   79)=1344467788888+9*2204
f(n)=                                                   899999999, len=    2501, g(   80)=122333444455555667778+9*2480
f(n)=                                                   999999999, len=    2779, g(   81)=123345555566667777888888+9*2755
f(n)=                                                  1999999999, len=    5527, g(   82)=1344455556678888+9*5511
f(n)=                                                  2999999999, len=    8287, g(   83)=12233344445557777778+9*8267
f(n)=                                                  3999999999, len=   11045, g(   84)=12334555666667788888888+9*11022
f(n)=                                                  4999999999, len=   13800, g(   85)=1344455666777777788888+9*13778
f(n)=                                                  5999999999, len=   16553, g(   86)=1223334444567777888+9*16534
f(n)=                                                  6999999999, len=   19303, g(   87)=1233456666668+9*19290
f(n)=                                                  7999999999, len=   22066, g(   88)=134446666777778888888+9*22045
f(n)=                                                  8999999999, len=   24824, g(   89)=12233344445555567788888+9*24801
f(n)=                                                  9999999999, len=   27581, g(   90)=123345555566666677777788+9*27557
f(n)=                                                 19999999999, len=   55139, g(   91)=1344455556666667777788888+9*55114
f(n)=                                                 29999999999, len=   82702, g(   92)=1223334444555666666777788888888+9*82671
f(n)=                                                 39999999999, len=  110248, g(   93)=1233455566666677788+9*110229
f(n)=                                                 49999999999, len=  137806, g(   94)=13444556666667788888+9*137786
f(n)=                                                 59999999999, len=  165369, g(   95)=12233344445666666788888888+9*165343
f(n)=                                                 69999999999, len=  192915, g(   96)=12334566666688+9*192901
f(n)=                                                 79999999999, len=  220480, g(   97)=1344466666677777778888+9*220458
f(n)=                                                 89999999999, len=  248048, g(   98)=122333444455555666667777778888888+9*248015
f(n)=                                                 99999999999, len=  275594, g(   99)=123345555566666777778+9*275573
f(n)=                                                199999999999, len=  551165, g(  100)=1344455556666777888+9*551146
f(n)=                                                299999999999, len=  826741, g(  101)=1223334444555666788888+9*826719
f(n)=                                                399999999999, len= 1102315, g(  102)=12334555667777777888888+9*1102292
f(n)=                                                499999999999, len= 1377886, g(  103)=134445567777788888888+9*1377865
f(n)=                                                599999999999, len= 1653454, g(  104)=122333444457778+9*1653439
f(n)=                                                699999999999, len= 1929027, g(  105)=123345666666888+9*1929012
f(n)=                                                799999999999, len= 2204605, g(  106)=13444666667777778888+9*2204585
f(n)=                                                899999999999, len= 2480186, g(  107)=1223334444555556667777888888+9*2480158
f(n)=                                                999999999999, len= 2755753, g(  108)=1233455555667788888888+9*2755731
f(n)=                                               1999999999999, len= 5511488, g(  109)=1344455556666677778888888+9*5511463
f(n)=                                               2999999999999, len= 8267222, g(  110)=122333444455567777777888888+9*8267195
f(n)=                                               3999999999999, len=11022946, g(  111)=1233455566667888888+9*11022927
f(n)=                                               4999999999999, len=13778675, g(  112)=1344455777788888+9*13778659
f(n)=                                               5999999999999, len=16534415, g(  113)=122333444456667777778888+9*16534391
f(n)=                                               6999999999999, len=19290139, g(  114)=1233456666668888+9*19290123
f(n)=                                               7999999999999, len=22045868, g(  115)=1344466777888+9*22045855
f(n)=                                               8999999999999, len=24801613, g(  116)=12233344445555566667777788+9*24801587
f(n)=                                               9999999999999, len=27557331, g(  117)=123345555588+9*27557319
f(n)=                                              19999999999999, len=55114652, g(  118)=13444555568888+9*55114638
f(n)=                                              29999999999999, len=82671978, g(  119)=122333444455566888888+9*82671957
f(n)=                                              39999999999999, len=110229295, g(  120)=1233455566688888888+9*110229276
f(n)=                                              49999999999999, len=137786608, g(  121)=134445566668+9*137786596
f(n)=                                              59999999999999, len=165343934, g(  122)=1223334444566666888+9*165343915
f(n)=                                              69999999999999, len=192901251, g(  123)=12334566666688888+9*192901234
f(n)=                                              79999999999999, len=220458566, g(  124)=1344478888888+9*220458553
f(n)=                                              89999999999999, len=248015889, g(  125)=1223334444555557+9*248015873
f(n)=                                              99999999999999, len=275573206, g(  126)=12334555556788+9*275573192
f(n)=                                             199999999999999, len=551146402, g(  127)=134445555666778888+9*551146384
f(n)=                                             299999999999999, len=826719603, g(  128)=122333444455566666777888888+9*826719576
f(n)=                                             399999999999999, len=1102292789, g(  129)=123345557777788888888+9*1102292768
f(n)=                                             499999999999999, len=1377865977, g(  130)=1344455667777778+9*1377865961
f(n)=                                             599999999999999, len=1653439178, g(  131)=1223334444566667777777888+9*1653439153
f(n)=                                             699999999999999, len=1929012363, g(  132)=123345666666888888+9*1929012345
f(n)=                                             799999999999999, len=2204585553, g(  133)=1344467788888888+9*2204585537
f(n)=                                             899999999999999, len=2480158751, g(  134)=122333444455555667778+9*2480158730
f(n)=                                             999999999999999, len=2755731943, g(  135)=123345555566667777888+9*2755731922
f(n)=                                            1999999999999999, len=5511463863, g(  136)=1344455556678888888+9*5511463844
f(n)=                                            2999999999999999, len=8267195787, g(  137)=12233344445557777778+9*8267195767
f(n)=                                            3999999999999999, len=11022927709, g(  138)=12334555666667788888+9*11022927689
f(n)=                                            4999999999999999, len=13778659636, g(  139)=1344455666777777788888888+9*13778659611
f(n)=                                            5999999999999999, len=16534391553, g(  140)=1223334444567777888+9*16534391534
f(n)=                                            6999999999999999, len=19290123475, g(  141)=1233456666668888888+9*19290123456
f(n)=                                            7999999999999999, len=22045855394, g(  142)=134446666777778+9*22045855379
f(n)=                                            8999999999999999, len=24801587324, g(  143)=12233344445555567788888+9*24801587301
f(n)=                                            9999999999999999, len=27557319253, g(  144)=123345555566666677777788888888+9*27557319223
f(n)=                                           19999999999999999, len=55114638475, g(  145)=1344455556666667777788888888+9*55114638447
f(n)=                                           29999999999999999, len=82671957702, g(  146)=1223334444555666666777788888888+9*82671957671
f(n)=                                           39999999999999999, len=110229276920, g(  147)=1233455566666677788888888+9*110229276895
f(n)=                                           49999999999999999, len=137786596142, g(  148)=13444556666667788888888+9*137786596119
f(n)=                                           59999999999999999, len=165343915369, g(  149)=12233344445666666788888888+9*165343915343
f(n)=                                           69999999999999999, len=192901234587, g(  150)=12334566666688888888+9*192901234567
f(n)=                                           79999999999999999, len=220458553816, g(  151)=1344466666677777778888888+9*220458553791
f(n)=                                           89999999999999999, len=248015873048, g(  152)=122333444455555666667777778888888+9*248015873015
f(n)=                                           99999999999999999, len=275573192266, g(  153)=123345555566666777778888888+9*275573192239
f(n)=                                          199999999999999999, len=551146384501, g(  154)=1344455556666777888888+9*551146384479
f(n)=                                          299999999999999999, len=826719576741, g(  155)=1223334444555666788888+9*826719576719
f(n)=                                          399999999999999999, len=1102292768979, g(  156)=12334555667777777888+9*1102292768959
f(n)=                                          499999999999999999, len=1377865961214, g(  157)=134445567777788+9*1377865961199
f(n)=                                          599999999999999999, len=1653439153454, g(  158)=122333444457778+9*1653439153439
f(n)=                                          699999999999999999, len=1929012345691, g(  159)=123345666666+9*1929012345679
f(n)=                                          799999999999999999, len=2204585537941, g(  160)=13444666667777778888888+9*2204585537918
f(n)=                                          899999999999999999, len=2480158730186, g(  161)=1223334444555556667777888888+9*2480158730158
f(n)=                                          999999999999999999, len=2755731922417, g(  162)=1233455555667788888+9*2755731922398
f(n)=                                         1999999999999999999, len=5511463844816, g(  163)=1344455556666677778+9*5511463844797
f(n)=                                         2999999999999999999, len=8267195767222, g(  164)=122333444455567777777888888+9*8267195767195
f(n)=                                         3999999999999999999, len=11022927689610, g(  165)=1233455566667888+9*11022927689594
f(n)=                                         4999999999999999999, len=13778659612011, g(  166)=1344455777788888888+9*13778659611992
f(n)=                                         5999999999999999999, len=16534391534415, g(  167)=122333444456667777778888+9*16534391534391
f(n)=                                         6999999999999999999, len=19290123456803, g(  168)=1233456666668+9*19290123456790
f(n)=                                         7999999999999999999, len=22045855379204, g(  169)=1344466777888888+9*22045855379188
f(n)=                                         8999999999999999999, len=24801587301613, g(  170)=12233344445555566667777788+9*24801587301587
f(n)=                                         9999999999999999999, len=27557319224003, g(  171)=123345555588888888+9*27557319223985
f(n)=                                        19999999999999999999, len=55114638447988, g(  172)=13444555568888888+9*55114638447971
f(n)=                                        29999999999999999999, len=82671957671978, g(  173)=122333444455566888888+9*82671957671957
f(n)=                                        39999999999999999999, len=110229276895959, g(  174)=1233455566688888+9*110229276895943
f(n)=                                        49999999999999999999, len=137786596119944, g(  175)=134445566668888+9*137786596119929
f(n)=                                        59999999999999999999, len=165343915343934, g(  176)=1223334444566666888+9*165343915343915
f(n)=                                        69999999999999999999, len=192901234567915, g(  177)=12334566666688+9*192901234567901
f(n)=                                        79999999999999999999, len=220458553791894, g(  178)=1344478+9*220458553791887
f(n)=                                        89999999999999999999, len=248015873015889, g(  179)=1223334444555557+9*248015873015873
f(n)=                                        99999999999999999999, len=275573192239878, g(  180)=12334555556788888888+9*275573192239858
f(n)=                                       199999999999999999999, len=551146384479738, g(  181)=134445555666778888888+9*551146384479717
f(n)=                                       299999999999999999999, len=826719576719603, g(  182)=122333444455566666777888888+9*826719576719576
f(n)=                                       399999999999999999999, len=1102292768959453, g(  183)=123345557777788888+9*1102292768959435
f(n)=                                       499999999999999999999, len=1377865961199313, g(  184)=1344455667777778888+9*1377865961199294
f(n)=                                       599999999999999999999, len=1653439153439178, g(  185)=1223334444566667777777888+9*1653439153439153
f(n)=                                       699999999999999999999, len=1929012345679027, g(  186)=123345666666888+9*1929012345679012
f(n)=                                       799999999999999999999, len=2204585537918881, g(  187)=1344467788+9*2204585537918871
f(n)=                                       899999999999999999999, len=2480158730158751, g(  188)=122333444455555667778+9*2480158730158730
f(n)=                                       999999999999999999999, len=2755731922398607, g(  189)=123345555566667777+9*2755731922398589
f(n)=                                      1999999999999999999999, len=5511463844797191, g(  190)=1344455556678+9*5511463844797178
f(n)=                                      2999999999999999999999, len=8267195767195787, g(  191)=12233344445557777778+9*8267195767195767
f(n)=                                      3999999999999999999999, len=11022927689594373, g(  192)=12334555666667788+9*11022927689594356
f(n)=                                      4999999999999999999999, len=13778659611992964, g(  193)=1344455666777777788+9*13778659611992945
f(n)=                                      5999999999999999999999, len=16534391534391553, g(  194)=1223334444567777888+9*16534391534391534
f(n)=                                      6999999999999999999999, len=19290123456790139, g(  195)=1233456666668888+9*19290123456790123
f(n)=                                      7999999999999999999999, len=22045855379188730, g(  196)=134446666777778888+9*22045855379188712
f(n)=                                      8999999999999999999999, len=24801587301587324, g(  197)=12233344445555567788888+9*24801587301587301
f(n)=                                      9999999999999999999999, len=27557319223985917, g(  198)=123345555566666677777788888+9*27557319223985890
f(n)=                                     19999999999999999999999, len=55114638447971803, g(  199)=1344455556666667777788+9*55114638447971781
f(n)=                                     29999999999999999999999, len=82671957671957702, g(  200)=1223334444555666666777788888888+9*82671957671957671
f(n)=                                     39999999999999999999999, len=110229276895943584, g(  201)=1233455566666677788888+9*110229276895943562
f(n)=                                     49999999999999999999999, len=137786596119929470, g(  202)=13444556666667788+9*137786596119929453
f(n)=                                     59999999999999999999999, len=165343915343915369, g(  203)=12233344445666666788888888+9*165343915343915343
f(n)=                                     69999999999999999999999, len=192901234567901251, g(  204)=12334566666688888+9*192901234567901234
f(n)=                                     79999999999999999999999, len=220458553791887144, g(  205)=1344466666677777778+9*220458553791887125
f(n)=                                     89999999999999999999999, len=248015873015873048, g(  206)=122333444455555666667777778888888+9*248015873015873015
f(n)=                                     99999999999999999999999, len=275573192239858930, g(  207)=123345555566666777778888+9*275573192239858906
f(n)=                                    199999999999999999999999, len=551146384479717829, g(  208)=1344455556666777+9*551146384479717813
f(n)=                                    299999999999999999999999, len=826719576719576741, g(  209)=1223334444555666788888+9*826719576719576719
f(n)=                                    399999999999999999999999, len=1102292768959435643, g(  210)=12334555667777777+9*1102292768959435626
f(n)=                                    499999999999999999999999, len=1377865961199294550, g(  211)=134445567777788888+9*1377865961199294532
f(n)=                                    599999999999999999999999, len=1653439153439153454, g(  212)=122333444457778+9*1653439153439153439
f(n)=                                    699999999999999999999999, len=1929012345679012363, g(  213)=123345666666888888+9*1929012345679012345
f(n)=                                    799999999999999999999999, len=2204585537918871269, g(  214)=13444666667777778+9*2204585537918871252
f(n)=                                    899999999999999999999999, len=2480158730158730186, g(  215)=1223334444555556667777888888+9*2480158730158730158
f(n)=                                    999999999999999999999999, len=2755731922398589081, g(  216)=1233455555667788+9*2755731922398589065
f(n)=                                   1999999999999999999999999, len=5511463844797178152, g(  217)=1344455556666677778888+9*5511463844797178130
f(n)=                                   2999999999999999999999999, len=8267195767195767222, g(  218)=122333444455567777777888888+9*8267195767195767195
f(n)=                                   3999999999999999999999999, len=11022927689594356274, g(  219)=1233455566667+9*11022927689594356261
f(n)=                                   4999999999999999999999999, len=13778659611992945339, g(  220)=1344455777788+9*13778659611992945326
f(n)=                                   5999999999999999999999999, len=16534391534391534415, g(  221)=122333444456667777778888+9*16534391534391534391
f(n)=                                   6999999999999999999999999, len=19290123456790123475, g(  222)=1233456666668888888+9*19290123456790123456
f(n)=                                   7999999999999999999999999, len=22045855379188712532, g(  223)=1344466777+9*22045855379188712522
f(n)=                                   8999999999999999999999999, len=24801587301587301613, g(  224)=12233344445555566667777788+9*24801587301587301587
f(n)=                                   9999999999999999999999999, len=27557319223985890667, g(  225)=123345555588888+9*27557319223985890652
f(n)=                                  19999999999999999999999999, len=55114638447971781316, g(  226)=13444555568+9*55114638447971781305
f(n)=                                  29999999999999999999999999, len=82671957671957671978, g(  227)=122333444455566888888+9*82671957671957671957
f(n)=                                  39999999999999999999999999, len=110229276895943562623, g(  228)=1233455566688+9*110229276895943562610
f(n)=                                  49999999999999999999999999, len=137786596119929453280, g(  229)=134445566668888888+9*137786596119929453262
f(n)=                                  59999999999999999999999999, len=165343915343915343934, g(  230)=1223334444566666888+9*165343915343915343915
f(n)=                                  69999999999999999999999999, len=192901234567901234587, g(  231)=12334566666688888888+9*192901234567901234567
f(n)=                                  79999999999999999999999999, len=220458553791887125230, g(  232)=1344478888+9*220458553791887125220
f(n)=                                  89999999999999999999999999, len=248015873015873015889, g(  233)=1223334444555557+9*248015873015873015873
f(n)=                                  99999999999999999999999999, len=275573192239858906542, g(  234)=12334555556788888+9*275573192239858906525
f(n)=                                 199999999999999999999999999, len=551146384479717813066, g(  235)=134445555666778+9*551146384479717813051
f(n)=                                 299999999999999999999999999, len=826719576719576719603, g(  236)=122333444455566666777888888+9*826719576719576719576
f(n)=                                 399999999999999999999999999, len=1102292768959435626117, g(  237)=123345557777788+9*1102292768959435626102
f(n)=                                 499999999999999999999999999, len=1377865961199294532649, g(  238)=1344455667777778888888+9*1377865961199294532627
f(n)=                                 599999999999999999999999999, len=1653439153439153439178, g(  239)=1223334444566667777777888+9*1653439153439153439153
f(n)=                                 699999999999999999999999999, len=1929012345679012345691, g(  240)=123345666666+9*1929012345679012345679
f(n)=                                 799999999999999999999999999, len=2204585537918871252217, g(  241)=1344467788888+9*2204585537918871252204
f(n)=                                 899999999999999999999999999, len=2480158730158730158751, g(  242)=122333444455555667778+9*2480158730158730158730
f(n)=                                 999999999999999999999999999, len=2755731922398589065279, g(  243)=123345555566667777888888+9*2755731922398589065255
f(n)=                                1999999999999999999999999999, len=5511463844797178130527, g(  244)=1344455556678888+9*5511463844797178130511
f(n)=                                2999999999999999999999999999, len=8267195767195767195787, g(  245)=12233344445557777778+9*8267195767195767195767
f(n)=                                3999999999999999999999999999, len=11022927689594356261045, g(  246)=12334555666667788888888+9*11022927689594356261022
f(n)=                                4999999999999999999999999999, len=13778659611992945326300, g(  247)=1344455666777777788888+9*13778659611992945326278
f(n)=                                5999999999999999999999999999, len=16534391534391534391553, g(  248)=1223334444567777888+9*16534391534391534391534
f(n)=                                6999999999999999999999999999, len=19290123456790123456803, g(  249)=1233456666668+9*19290123456790123456790
f(n)=                                7999999999999999999999999999, len=22045855379188712522066, g(  250)=134446666777778888888+9*22045855379188712522045
f(n)=                                8999999999999999999999999999, len=24801587301587301587324, g(  251)=12233344445555567788888+9*24801587301587301587301
f(n)=                                9999999999999999999999999999, len=27557319223985890652581, g(  252)=123345555566666677777788+9*27557319223985890652557
f(n)=                               19999999999999999999999999999, len=55114638447971781305139, g(  253)=1344455556666667777788888+9*55114638447971781305114
f(n)=                               29999999999999999999999999999, len=82671957671957671957702, g(  254)=1223334444555666666777788888888+9*82671957671957671957671
f(n)=                               39999999999999999999999999999, len=110229276895943562610248, g(  255)=1233455566666677788+9*110229276895943562610229
f(n)=                               49999999999999999999999999999, len=137786596119929453262806, g(  256)=13444556666667788888+9*137786596119929453262786
f(n)=                               59999999999999999999999999999, len=165343915343915343915369, g(  257)=12233344445666666788888888+9*165343915343915343915343
f(n)=                               69999999999999999999999999999, len=192901234567901234567915, g(  258)=12334566666688+9*192901234567901234567901
f(n)=                               79999999999999999999999999999, len=220458553791887125220480, g(  259)=1344466666677777778888+9*220458553791887125220458
f(n)=                               89999999999999999999999999999, len=248015873015873015873048, g(  260)=122333444455555666667777778888888+9*248015873015873015873015
f(n)=                               99999999999999999999999999999, len=275573192239858906525594, g(  261)=123345555566666777778+9*275573192239858906525573
f(n)=                              199999999999999999999999999999, len=551146384479717813051165, g(  262)=1344455556666777888+9*551146384479717813051146
f(n)=                              299999999999999999999999999999, len=826719576719576719576741, g(  263)=1223334444555666788888+9*826719576719576719576719
f(n)=                              399999999999999999999999999999, len=1102292768959435626102315, g(  264)=12334555667777777888888+9*1102292768959435626102292
f(n)=                              499999999999999999999999999999, len=1377865961199294532627886, g(  265)=134445567777788888888+9*1377865961199294532627865
f(n)=                              599999999999999999999999999999, len=1653439153439153439153454, g(  266)=122333444457778+9*1653439153439153439153439
f(n)=                              699999999999999999999999999999, len=1929012345679012345679027, g(  267)=123345666666888+9*1929012345679012345679012
f(n)=                              799999999999999999999999999999, len=2204585537918871252204605, g(  268)=13444666667777778888+9*2204585537918871252204585
f(n)=                              899999999999999999999999999999, len=2480158730158730158730186, g(  269)=1223334444555556667777888888+9*2480158730158730158730158
f(n)=                              999999999999999999999999999999, len=2755731922398589065255753, g(  270)=1233455555667788888888+9*2755731922398589065255731
f(n)=                             1999999999999999999999999999999, len=5511463844797178130511488, g(  271)=1344455556666677778888888+9*5511463844797178130511463
f(n)=                             2999999999999999999999999999999, len=8267195767195767195767222, g(  272)=122333444455567777777888888+9*8267195767195767195767195
f(n)=                             3999999999999999999999999999999, len=11022927689594356261022946, g(  273)=1233455566667888888+9*11022927689594356261022927
f(n)=                             4999999999999999999999999999999, len=13778659611992945326278675, g(  274)=1344455777788888+9*13778659611992945326278659
f(n)=                             5999999999999999999999999999999, len=16534391534391534391534415, g(  275)=122333444456667777778888+9*16534391534391534391534391
f(n)=                             6999999999999999999999999999999, len=19290123456790123456790139, g(  276)=1233456666668888+9*19290123456790123456790123
f(n)=                             7999999999999999999999999999999, len=22045855379188712522045868, g(  277)=1344466777888+9*22045855379188712522045855
f(n)=                             8999999999999999999999999999999, len=24801587301587301587301613, g(  278)=12233344445555566667777788+9*24801587301587301587301587
f(n)=                             9999999999999999999999999999999, len=27557319223985890652557331, g(  279)=123345555588+9*27557319223985890652557319
f(n)=                            19999999999999999999999999999999, len=55114638447971781305114652, g(  280)=13444555568888+9*55114638447971781305114638
f(n)=                            29999999999999999999999999999999, len=82671957671957671957671978, g(  281)=122333444455566888888+9*82671957671957671957671957
f(n)=                            39999999999999999999999999999999, len=110229276895943562610229295, g(  282)=1233455566688888888+9*110229276895943562610229276
f(n)=                            49999999999999999999999999999999, len=137786596119929453262786608, g(  283)=134445566668+9*137786596119929453262786596
f(n)=                            59999999999999999999999999999999, len=165343915343915343915343934, g(  284)=1223334444566666888+9*165343915343915343915343915
f(n)=                            69999999999999999999999999999999, len=192901234567901234567901251, g(  285)=12334566666688888+9*192901234567901234567901234
f(n)=                            79999999999999999999999999999999, len=220458553791887125220458566, g(  286)=1344478888888+9*220458553791887125220458553
f(n)=                            89999999999999999999999999999999, len=248015873015873015873015889, g(  287)=1223334444555557+9*248015873015873015873015873
f(n)=                            99999999999999999999999999999999, len=275573192239858906525573206, g(  288)=12334555556788+9*275573192239858906525573192
f(n)=                           199999999999999999999999999999999, len=551146384479717813051146402, g(  289)=134445555666778888+9*551146384479717813051146384
f(n)=                           299999999999999999999999999999999, len=826719576719576719576719603, g(  290)=122333444455566666777888888+9*826719576719576719576719576
f(n)=                           399999999999999999999999999999999, len=1102292768959435626102292789, g(  291)=123345557777788888888+9*1102292768959435626102292768
f(n)=                           499999999999999999999999999999999, len=1377865961199294532627865977, g(  292)=1344455667777778+9*1377865961199294532627865961
f(n)=                           599999999999999999999999999999999, len=1653439153439153439153439178, g(  293)=1223334444566667777777888+9*1653439153439153439153439153
f(n)=                           699999999999999999999999999999999, len=1929012345679012345679012363, g(  294)=123345666666888888+9*1929012345679012345679012345
f(n)=                           799999999999999999999999999999999, len=2204585537918871252204585553, g(  295)=1344467788888888+9*2204585537918871252204585537
f(n)=                           899999999999999999999999999999999, len=2480158730158730158730158751, g(  296)=122333444455555667778+9*2480158730158730158730158730
f(n)=                           999999999999999999999999999999999, len=2755731922398589065255731943, g(  297)=123345555566667777888+9*2755731922398589065255731922
f(n)=                          1999999999999999999999999999999999, len=5511463844797178130511463863, g(  298)=1344455556678888888+9*5511463844797178130511463844
f(n)=                          2999999999999999999999999999999999, len=8267195767195767195767195787, g(  299)=12233344445557777778+9*8267195767195767195767195767
f(n)=                          3999999999999999999999999999999999, len=11022927689594356261022927709, g(  300)=12334555666667788888+9*11022927689594356261022927689
f(n)=                          4999999999999999999999999999999999, len=13778659611992945326278659636, g(  301)=1344455666777777788888888+9*13778659611992945326278659611
f(n)=                          5999999999999999999999999999999999, len=16534391534391534391534391553, g(  302)=1223334444567777888+9*16534391534391534391534391534
f(n)=                          6999999999999999999999999999999999, len=19290123456790123456790123475, g(  303)=1233456666668888888+9*19290123456790123456790123456
f(n)=                          7999999999999999999999999999999999, len=22045855379188712522045855394, g(  304)=134446666777778+9*22045855379188712522045855379
f(n)=                          8999999999999999999999999999999999, len=24801587301587301587301587324, g(  305)=12233344445555567788888+9*24801587301587301587301587301
f(n)=                          9999999999999999999999999999999999, len=27557319223985890652557319253, g(  306)=123345555566666677777788888888+9*27557319223985890652557319223
f(n)=                         19999999999999999999999999999999999, len=55114638447971781305114638475, g(  307)=1344455556666667777788888888+9*55114638447971781305114638447
f(n)=                         29999999999999999999999999999999999, len=82671957671957671957671957702, g(  308)=1223334444555666666777788888888+9*82671957671957671957671957671
f(n)=                         39999999999999999999999999999999999, len=110229276895943562610229276920, g(  309)=1233455566666677788888888+9*110229276895943562610229276895
f(n)=                         49999999999999999999999999999999999, len=137786596119929453262786596142, g(  310)=13444556666667788888888+9*137786596119929453262786596119
f(n)=                         59999999999999999999999999999999999, len=165343915343915343915343915369, g(  311)=12233344445666666788888888+9*165343915343915343915343915343
f(n)=                         69999999999999999999999999999999999, len=192901234567901234567901234587, g(  312)=12334566666688888888+9*192901234567901234567901234567
f(n)=                         79999999999999999999999999999999999, len=220458553791887125220458553816, g(  313)=1344466666677777778888888+9*220458553791887125220458553791
f(n)=                         89999999999999999999999999999999999, len=248015873015873015873015873048, g(  314)=122333444455555666667777778888888+9*248015873015873015873015873015
f(n)=                         99999999999999999999999999999999999, len=275573192239858906525573192266, g(  315)=123345555566666777778888888+9*275573192239858906525573192239
f(n)=                        199999999999999999999999999999999999, len=551146384479717813051146384501, g(  316)=1344455556666777888888+9*551146384479717813051146384479
f(n)=                        299999999999999999999999999999999999, len=826719576719576719576719576741, g(  317)=1223334444555666788888+9*826719576719576719576719576719
f(n)=                        399999999999999999999999999999999999, len=1102292768959435626102292768979, g(  318)=12334555667777777888+9*1102292768959435626102292768959
f(n)=                        499999999999999999999999999999999999, len=1377865961199294532627865961214, g(  319)=134445567777788+9*1377865961199294532627865961199
f(n)=                        599999999999999999999999999999999999, len=1653439153439153439153439153454, g(  320)=122333444457778+9*1653439153439153439153439153439
f(n)=                        699999999999999999999999999999999999, len=1929012345679012345679012345691, g(  321)=123345666666+9*1929012345679012345679012345679
f(n)=                        799999999999999999999999999999999999, len=2204585537918871252204585537941, g(  322)=13444666667777778888888+9*2204585537918871252204585537918
f(n)=                        899999999999999999999999999999999999, len=2480158730158730158730158730186, g(  323)=1223334444555556667777888888+9*2480158730158730158730158730158
f(n)=                        999999999999999999999999999999999999, len=2755731922398589065255731922417, g(  324)=1233455555667788888+9*2755731922398589065255731922398
f(n)=                       1999999999999999999999999999999999999, len=5511463844797178130511463844816, g(  325)=1344455556666677778+9*5511463844797178130511463844797
f(n)=                       2999999999999999999999999999999999999, len=8267195767195767195767195767222, g(  326)=122333444455567777777888888+9*8267195767195767195767195767195
f(n)=                       3999999999999999999999999999999999999, len=11022927689594356261022927689610, g(  327)=1233455566667888+9*11022927689594356261022927689594
f(n)=                       4999999999999999999999999999999999999, len=13778659611992945326278659612011, g(  328)=1344455777788888888+9*13778659611992945326278659611992
f(n)=                       5999999999999999999999999999999999999, len=16534391534391534391534391534415, g(  329)=122333444456667777778888+9*16534391534391534391534391534391
f(n)=                       6999999999999999999999999999999999999, len=19290123456790123456790123456803, g(  330)=1233456666668+9*19290123456790123456790123456790
f(n)=                       7999999999999999999999999999999999999, len=22045855379188712522045855379204, g(  331)=1344466777888888+9*22045855379188712522045855379188
f(n)=                       8999999999999999999999999999999999999, len=24801587301587301587301587301613, g(  332)=12233344445555566667777788+9*24801587301587301587301587301587
f(n)=                       9999999999999999999999999999999999999, len=27557319223985890652557319224003, g(  333)=123345555588888888+9*27557319223985890652557319223985
f(n)=                      19999999999999999999999999999999999999, len=55114638447971781305114638447988, g(  334)=13444555568888888+9*55114638447971781305114638447971
f(n)=                      29999999999999999999999999999999999999, len=82671957671957671957671957671978, g(  335)=122333444455566888888+9*82671957671957671957671957671957
f(n)=                      39999999999999999999999999999999999999, len=110229276895943562610229276895959, g(  336)=1233455566688888+9*110229276895943562610229276895943
f(n)=                      49999999999999999999999999999999999999, len=137786596119929453262786596119944, g(  337)=134445566668888+9*137786596119929453262786596119929
f(n)=                      59999999999999999999999999999999999999, len=165343915343915343915343915343934, g(  338)=1223334444566666888+9*165343915343915343915343915343915
f(n)=                      69999999999999999999999999999999999999, len=192901234567901234567901234567915, g(  339)=12334566666688+9*192901234567901234567901234567901
f(n)=                      79999999999999999999999999999999999999, len=220458553791887125220458553791894, g(  340)=1344478+9*220458553791887125220458553791887
f(n)=                      89999999999999999999999999999999999999, len=248015873015873015873015873015889, g(  341)=1223334444555557+9*248015873015873015873015873015873
f(n)=                      99999999999999999999999999999999999999, len=275573192239858906525573192239878, g(  342)=12334555556788888888+9*275573192239858906525573192239858
f(n)=                     199999999999999999999999999999999999999, len=551146384479717813051146384479738, g(  343)=134445555666778888888+9*551146384479717813051146384479717
f(n)=                     299999999999999999999999999999999999999, len=826719576719576719576719576719603, g(  344)=122333444455566666777888888+9*826719576719576719576719576719576
f(n)=                     399999999999999999999999999999999999999, len=1102292768959435626102292768959453, g(  345)=123345557777788888+9*1102292768959435626102292768959435
f(n)=                     499999999999999999999999999999999999999, len=1377865961199294532627865961199313, g(  346)=1344455667777778888+9*1377865961199294532627865961199294
f(n)=                     599999999999999999999999999999999999999, len=1653439153439153439153439153439178, g(  347)=1223334444566667777777888+9*1653439153439153439153439153439153
f(n)=                     699999999999999999999999999999999999999, len=1929012345679012345679012345679027, g(  348)=123345666666888+9*1929012345679012345679012345679012
f(n)=                     799999999999999999999999999999999999999, len=2204585537918871252204585537918881, g(  349)=1344467788+9*2204585537918871252204585537918871
f(n)=                     899999999999999999999999999999999999999, len=2480158730158730158730158730158751, g(  350)=122333444455555667778+9*2480158730158730158730158730158730
f(n)=                     999999999999999999999999999999999999999, len=2755731922398589065255731922398607, g(  351)=123345555566667777+9*2755731922398589065255731922398589
f(n)=                    1999999999999999999999999999999999999999, len=5511463844797178130511463844797191, g(  352)=1344455556678+9*5511463844797178130511463844797178
f(n)=                    2999999999999999999999999999999999999999, len=8267195767195767195767195767195787, g(  353)=12233344445557777778+9*8267195767195767195767195767195767
f(n)=                    3999999999999999999999999999999999999999, len=11022927689594356261022927689594373, g(  354)=12334555666667788+9*11022927689594356261022927689594356
f(n)=                    4999999999999999999999999999999999999999, len=13778659611992945326278659611992964, g(  355)=1344455666777777788+9*13778659611992945326278659611992945
f(n)=                    5999999999999999999999999999999999999999, len=16534391534391534391534391534391553, g(  356)=1223334444567777888+9*16534391534391534391534391534391534
f(n)=                    6999999999999999999999999999999999999999, len=19290123456790123456790123456790139, g(  357)=1233456666668888+9*19290123456790123456790123456790123
f(n)=                    7999999999999999999999999999999999999999, len=22045855379188712522045855379188730, g(  358)=134446666777778888+9*22045855379188712522045855379188712
f(n)=                    8999999999999999999999999999999999999999, len=24801587301587301587301587301587324, g(  359)=12233344445555567788888+9*24801587301587301587301587301587301
f(n)=                    9999999999999999999999999999999999999999, len=27557319223985890652557319223985917, g(  360)=123345555566666677777788888+9*27557319223985890652557319223985890
f(n)=                   19999999999999999999999999999999999999999, len=55114638447971781305114638447971803, g(  361)=1344455556666667777788+9*55114638447971781305114638447971781
f(n)=                   29999999999999999999999999999999999999999, len=82671957671957671957671957671957702, g(  362)=1223334444555666666777788888888+9*82671957671957671957671957671957671
f(n)=                   39999999999999999999999999999999999999999, len=110229276895943562610229276895943584, g(  363)=1233455566666677788888+9*110229276895943562610229276895943562
f(n)=                   49999999999999999999999999999999999999999, len=137786596119929453262786596119929470, g(  364)=13444556666667788+9*137786596119929453262786596119929453
f(n)=                   59999999999999999999999999999999999999999, len=165343915343915343915343915343915369, g(  365)=12233344445666666788888888+9*165343915343915343915343915343915343
f(n)=                   69999999999999999999999999999999999999999, len=192901234567901234567901234567901251, g(  366)=12334566666688888+9*192901234567901234567901234567901234
f(n)=                   79999999999999999999999999999999999999999, len=220458553791887125220458553791887144, g(  367)=1344466666677777778+9*220458553791887125220458553791887125
f(n)=                   89999999999999999999999999999999999999999, len=248015873015873015873015873015873048, g(  368)=122333444455555666667777778888888+9*248015873015873015873015873015873015
f(n)=                   99999999999999999999999999999999999999999, len=275573192239858906525573192239858930, g(  369)=123345555566666777778888+9*275573192239858906525573192239858906
f(n)=                  199999999999999999999999999999999999999999, len=551146384479717813051146384479717829, g(  370)=1344455556666777+9*551146384479717813051146384479717813
f(n)=                  299999999999999999999999999999999999999999, len=826719576719576719576719576719576741, g(  371)=1223334444555666788888+9*826719576719576719576719576719576719
f(n)=                  399999999999999999999999999999999999999999, len=1102292768959435626102292768959435643, g(  372)=12334555667777777+9*1102292768959435626102292768959435626
f(n)=                  499999999999999999999999999999999999999999, len=1377865961199294532627865961199294550, g(  373)=134445567777788888+9*1377865961199294532627865961199294532
f(n)=                  599999999999999999999999999999999999999999, len=1653439153439153439153439153439153454, g(  374)=122333444457778+9*1653439153439153439153439153439153439
f(n)=                  699999999999999999999999999999999999999999, len=1929012345679012345679012345679012363, g(  375)=123345666666888888+9*1929012345679012345679012345679012345
f(n)=                  799999999999999999999999999999999999999999, len=2204585537918871252204585537918871269, g(  376)=13444666667777778+9*2204585537918871252204585537918871252
f(n)=                  899999999999999999999999999999999999999999, len=2480158730158730158730158730158730186, g(  377)=1223334444555556667777888888+9*2480158730158730158730158730158730158
f(n)=                  999999999999999999999999999999999999999999, len=2755731922398589065255731922398589081, g(  378)=1233455555667788+9*2755731922398589065255731922398589065
f(n)=                 1999999999999999999999999999999999999999999, len=5511463844797178130511463844797178152, g(  379)=1344455556666677778888+9*5511463844797178130511463844797178130
f(n)=                 2999999999999999999999999999999999999999999, len=8267195767195767195767195767195767222, g(  380)=122333444455567777777888888+9*8267195767195767195767195767195767195
f(n)=                 3999999999999999999999999999999999999999999, len=11022927689594356261022927689594356274, g(  381)=1233455566667+9*11022927689594356261022927689594356261
f(n)=                 4999999999999999999999999999999999999999999, len=13778659611992945326278659611992945339, g(  382)=1344455777788+9*13778659611992945326278659611992945326
f(n)=                 5999999999999999999999999999999999999999999, len=16534391534391534391534391534391534415, g(  383)=122333444456667777778888+9*16534391534391534391534391534391534391
f(n)=                 6999999999999999999999999999999999999999999, len=19290123456790123456790123456790123475, g(  384)=1233456666668888888+9*19290123456790123456790123456790123456
f(n)=                 7999999999999999999999999999999999999999999, len=22045855379188712522045855379188712532, g(  385)=1344466777+9*22045855379188712522045855379188712522
f(n)=                 8999999999999999999999999999999999999999999, len=24801587301587301587301587301587301613, g(  386)=12233344445555566667777788+9*24801587301587301587301587301587301587
f(n)=                 9999999999999999999999999999999999999999999, len=27557319223985890652557319223985890667, g(  387)=123345555588888+9*27557319223985890652557319223985890652
f(n)=                19999999999999999999999999999999999999999999, len=55114638447971781305114638447971781316, g(  388)=13444555568+9*55114638447971781305114638447971781305
f(n)=                29999999999999999999999999999999999999999999, len=82671957671957671957671957671957671978, g(  389)=122333444455566888888+9*82671957671957671957671957671957671957
f(n)=                39999999999999999999999999999999999999999999, len=110229276895943562610229276895943562623, g(  390)=1233455566688+9*110229276895943562610229276895943562610
f(n)=                49999999999999999999999999999999999999999999, len=137786596119929453262786596119929453280, g(  391)=134445566668888888+9*137786596119929453262786596119929453262
f(n)=                59999999999999999999999999999999999999999999, len=165343915343915343915343915343915343934, g(  392)=1223334444566666888+9*165343915343915343915343915343915343915
f(n)=                69999999999999999999999999999999999999999999, len=192901234567901234567901234567901234587, g(  393)=12334566666688888888+9*192901234567901234567901234567901234567
f(n)=                79999999999999999999999999999999999999999999, len=220458553791887125220458553791887125230, g(  394)=1344478888+9*220458553791887125220458553791887125220
f(n)=                89999999999999999999999999999999999999999999, len=248015873015873015873015873015873015889, g(  395)=1223334444555557+9*248015873015873015873015873015873015873
f(n)=                99999999999999999999999999999999999999999999, len=275573192239858906525573192239858906542, g(  396)=12334555556788888+9*275573192239858906525573192239858906525
f(n)=               199999999999999999999999999999999999999999999, len=551146384479717813051146384479717813066, g(  397)=134445555666778+9*551146384479717813051146384479717813051
f(n)=               299999999999999999999999999999999999999999999, len=826719576719576719576719576719576719603, g(  398)=122333444455566666777888888+9*826719576719576719576719576719576719576
f(n)=               399999999999999999999999999999999999999999999, len=1102292768959435626102292768959435626117, g(  399)=123345557777788+9*1102292768959435626102292768959435626102
f(n)=               499999999999999999999999999999999999999999999, len=1377865961199294532627865961199294532649, g(  400)=1344455667777778888888+9*1377865961199294532627865961199294532627
f(n)=               599999999999999999999999999999999999999999999, len=1653439153439153439153439153439153439178, g(  401)=1223334444566667777777888+9*1653439153439153439153439153439153439153
f(n)=               699999999999999999999999999999999999999999999, len=1929012345679012345679012345679012345691, g(  402)=123345666666+9*1929012345679012345679012345679012345679
f(n)=               799999999999999999999999999999999999999999999, len=2204585537918871252204585537918871252217, g(  403)=1344467788888+9*2204585537918871252204585537918871252204
f(n)=               899999999999999999999999999999999999999999999, len=2480158730158730158730158730158730158751, g(  404)=122333444455555667778+9*2480158730158730158730158730158730158730
f(n)=               999999999999999999999999999999999999999999999, len=2755731922398589065255731922398589065279, g(  405)=123345555566667777888888+9*2755731922398589065255731922398589065255
f(n)=              1999999999999999999999999999999999999999999999, len=5511463844797178130511463844797178130527, g(  406)=1344455556678888+9*5511463844797178130511463844797178130511
f(n)=              2999999999999999999999999999999999999999999999, len=8267195767195767195767195767195767195787, g(  407)=12233344445557777778+9*8267195767195767195767195767195767195767
f(n)=              3999999999999999999999999999999999999999999999, len=11022927689594356261022927689594356261045, g(  408)=12334555666667788888888+9*11022927689594356261022927689594356261022
f(n)=              4999999999999999999999999999999999999999999999, len=13778659611992945326278659611992945326300, g(  409)=1344455666777777788888+9*13778659611992945326278659611992945326278
f(n)=              5999999999999999999999999999999999999999999999, len=16534391534391534391534391534391534391553, g(  410)=1223334444567777888+9*16534391534391534391534391534391534391534
f(n)=              6999999999999999999999999999999999999999999999, len=19290123456790123456790123456790123456803, g(  411)=1233456666668+9*19290123456790123456790123456790123456790
f(n)=              7999999999999999999999999999999999999999999999, len=22045855379188712522045855379188712522066, g(  412)=134446666777778888888+9*22045855379188712522045855379188712522045
f(n)=              8999999999999999999999999999999999999999999999, len=24801587301587301587301587301587301587324, g(  413)=12233344445555567788888+9*24801587301587301587301587301587301587301
f(n)=              9999999999999999999999999999999999999999999999, len=27557319223985890652557319223985890652581, g(  414)=123345555566666677777788+9*27557319223985890652557319223985890652557
f(n)=             19999999999999999999999999999999999999999999999, len=55114638447971781305114638447971781305139, g(  415)=1344455556666667777788888+9*55114638447971781305114638447971781305114
f(n)=             29999999999999999999999999999999999999999999999, len=82671957671957671957671957671957671957702, g(  416)=1223334444555666666777788888888+9*82671957671957671957671957671957671957671
f(n)=             39999999999999999999999999999999999999999999999, len=110229276895943562610229276895943562610248, g(  417)=1233455566666677788+9*110229276895943562610229276895943562610229
f(n)=             49999999999999999999999999999999999999999999999, len=137786596119929453262786596119929453262806, g(  418)=13444556666667788888+9*137786596119929453262786596119929453262786
f(n)=             59999999999999999999999999999999999999999999999, len=165343915343915343915343915343915343915369, g(  419)=12233344445666666788888888+9*165343915343915343915343915343915343915343
f(n)=             69999999999999999999999999999999999999999999999, len=192901234567901234567901234567901234567915, g(  420)=12334566666688+9*192901234567901234567901234567901234567901
f(n)=             79999999999999999999999999999999999999999999999, len=220458553791887125220458553791887125220480, g(  421)=1344466666677777778888+9*220458553791887125220458553791887125220458
f(n)=             89999999999999999999999999999999999999999999999, len=248015873015873015873015873015873015873048, g(  422)=122333444455555666667777778888888+9*248015873015873015873015873015873015873015
f(n)=             99999999999999999999999999999999999999999999999, len=275573192239858906525573192239858906525594, g(  423)=123345555566666777778+9*275573192239858906525573192239858906525573
f(n)=            199999999999999999999999999999999999999999999999, len=551146384479717813051146384479717813051165, g(  424)=1344455556666777888+9*551146384479717813051146384479717813051146
f(n)=            299999999999999999999999999999999999999999999999, len=826719576719576719576719576719576719576741, g(  425)=1223334444555666788888+9*826719576719576719576719576719576719576719
f(n)=            399999999999999999999999999999999999999999999999, len=1102292768959435626102292768959435626102315, g(  426)=12334555667777777888888+9*1102292768959435626102292768959435626102292
f(n)=            499999999999999999999999999999999999999999999999, len=1377865961199294532627865961199294532627886, g(  427)=134445567777788888888+9*1377865961199294532627865961199294532627865
f(n)=            599999999999999999999999999999999999999999999999, len=1653439153439153439153439153439153439153454, g(  428)=122333444457778+9*1653439153439153439153439153439153439153439
f(n)=            699999999999999999999999999999999999999999999999, len=1929012345679012345679012345679012345679027, g(  429)=123345666666888+9*1929012345679012345679012345679012345679012
f(n)=            799999999999999999999999999999999999999999999999, len=2204585537918871252204585537918871252204605, g(  430)=13444666667777778888+9*2204585537918871252204585537918871252204585
f(n)=            899999999999999999999999999999999999999999999999, len=2480158730158730158730158730158730158730186, g(  431)=1223334444555556667777888888+9*2480158730158730158730158730158730158730158
f(n)=            999999999999999999999999999999999999999999999999, len=2755731922398589065255731922398589065255753, g(  432)=1233455555667788888888+9*2755731922398589065255731922398589065255731
f(n)=           1999999999999999999999999999999999999999999999999, len=5511463844797178130511463844797178130511488, g(  433)=1344455556666677778888888+9*5511463844797178130511463844797178130511463
f(n)=           2999999999999999999999999999999999999999999999999, len=8267195767195767195767195767195767195767222, g(  434)=122333444455567777777888888+9*8267195767195767195767195767195767195767195
f(n)=           3999999999999999999999999999999999999999999999999, len=11022927689594356261022927689594356261022946, g(  435)=1233455566667888888+9*11022927689594356261022927689594356261022927
f(n)=           4999999999999999999999999999999999999999999999999, len=13778659611992945326278659611992945326278675, g(  436)=1344455777788888+9*13778659611992945326278659611992945326278659
f(n)=           5999999999999999999999999999999999999999999999999, len=16534391534391534391534391534391534391534415, g(  437)=122333444456667777778888+9*16534391534391534391534391534391534391534391
f(n)=           6999999999999999999999999999999999999999999999999, len=19290123456790123456790123456790123456790139, g(  438)=1233456666668888+9*19290123456790123456790123456790123456790123
f(n)=           7999999999999999999999999999999999999999999999999, len=22045855379188712522045855379188712522045868, g(  439)=1344466777888+9*22045855379188712522045855379188712522045855
f(n)=           8999999999999999999999999999999999999999999999999, len=24801587301587301587301587301587301587301613, g(  440)=12233344445555566667777788+9*24801587301587301587301587301587301587301587
f(n)=           9999999999999999999999999999999999999999999999999, len=27557319223985890652557319223985890652557331, g(  441)=123345555588+9*27557319223985890652557319223985890652557319
f(n)=          19999999999999999999999999999999999999999999999999, len=55114638447971781305114638447971781305114652, g(  442)=13444555568888+9*55114638447971781305114638447971781305114638
f(n)=          29999999999999999999999999999999999999999999999999, len=82671957671957671957671957671957671957671978, g(  443)=122333444455566888888+9*82671957671957671957671957671957671957671957
f(n)=          39999999999999999999999999999999999999999999999999, len=110229276895943562610229276895943562610229295, g(  444)=1233455566688888888+9*110229276895943562610229276895943562610229276
f(n)=          49999999999999999999999999999999999999999999999999, len=137786596119929453262786596119929453262786608, g(  445)=134445566668+9*137786596119929453262786596119929453262786596
f(n)=          59999999999999999999999999999999999999999999999999, len=165343915343915343915343915343915343915343934, g(  446)=1223334444566666888+9*165343915343915343915343915343915343915343915
f(n)=          69999999999999999999999999999999999999999999999999, len=192901234567901234567901234567901234567901251, g(  447)=12334566666688888+9*192901234567901234567901234567901234567901234
f(n)=          79999999999999999999999999999999999999999999999999, len=220458553791887125220458553791887125220458566, g(  448)=1344478888888+9*220458553791887125220458553791887125220458553
f(n)=          89999999999999999999999999999999999999999999999999, len=248015873015873015873015873015873015873015889, g(  449)=1223334444555557+9*248015873015873015873015873015873015873015873
f(n)=          99999999999999999999999999999999999999999999999999, len=275573192239858906525573192239858906525573206, g(  450)=12334555556788+9*275573192239858906525573192239858906525573192
f(n)=         199999999999999999999999999999999999999999999999999, len=551146384479717813051146384479717813051146402, g(  451)=134445555666778888+9*551146384479717813051146384479717813051146384
f(n)=         299999999999999999999999999999999999999999999999999, len=826719576719576719576719576719576719576719603, g(  452)=122333444455566666777888888+9*826719576719576719576719576719576719576719576
f(n)=         399999999999999999999999999999999999999999999999999, len=1102292768959435626102292768959435626102292789, g(  453)=123345557777788888888+9*1102292768959435626102292768959435626102292768
f(n)=         499999999999999999999999999999999999999999999999999, len=1377865961199294532627865961199294532627865977, g(  454)=1344455667777778+9*1377865961199294532627865961199294532627865961
f(n)=         599999999999999999999999999999999999999999999999999, len=1653439153439153439153439153439153439153439178, g(  455)=1223334444566667777777888+9*1653439153439153439153439153439153439153439153
f(n)=         699999999999999999999999999999999999999999999999999, len=1929012345679012345679012345679012345679012363, g(  456)=123345666666888888+9*1929012345679012345679012345679012345679012345
f(n)=         799999999999999999999999999999999999999999999999999, len=2204585537918871252204585537918871252204585553, g(  457)=1344467788888888+9*2204585537918871252204585537918871252204585537
f(n)=         899999999999999999999999999999999999999999999999999, len=2480158730158730158730158730158730158730158751, g(  458)=122333444455555667778+9*2480158730158730158730158730158730158730158730
f(n)=         999999999999999999999999999999999999999999999999999, len=2755731922398589065255731922398589065255731943, g(  459)=123345555566667777888+9*2755731922398589065255731922398589065255731922
f(n)=        1999999999999999999999999999999999999999999999999999, len=5511463844797178130511463844797178130511463863, g(  460)=1344455556678888888+9*5511463844797178130511463844797178130511463844
f(n)=        2999999999999999999999999999999999999999999999999999, len=8267195767195767195767195767195767195767195787, g(  461)=12233344445557777778+9*8267195767195767195767195767195767195767195767
f(n)=        3999999999999999999999999999999999999999999999999999, len=11022927689594356261022927689594356261022927709, g(  462)=12334555666667788888+9*11022927689594356261022927689594356261022927689
f(n)=        4999999999999999999999999999999999999999999999999999, len=13778659611992945326278659611992945326278659636, g(  463)=1344455666777777788888888+9*13778659611992945326278659611992945326278659611
f(n)=        5999999999999999999999999999999999999999999999999999, len=16534391534391534391534391534391534391534391553, g(  464)=1223334444567777888+9*16534391534391534391534391534391534391534391534
f(n)=        6999999999999999999999999999999999999999999999999999, len=19290123456790123456790123456790123456790123475, g(  465)=1233456666668888888+9*19290123456790123456790123456790123456790123456
f(n)=        7999999999999999999999999999999999999999999999999999, len=22045855379188712522045855379188712522045855394, g(  466)=134446666777778+9*22045855379188712522045855379188712522045855379
f(n)=        8999999999999999999999999999999999999999999999999999, len=24801587301587301587301587301587301587301587324, g(  467)=12233344445555567788888+9*24801587301587301587301587301587301587301587301
f(n)=        9999999999999999999999999999999999999999999999999999, len=27557319223985890652557319223985890652557319253, g(  468)=123345555566666677777788888888+9*27557319223985890652557319223985890652557319223
f(n)=       19999999999999999999999999999999999999999999999999999, len=55114638447971781305114638447971781305114638475, g(  469)=1344455556666667777788888888+9*55114638447971781305114638447971781305114638447
f(n)=       29999999999999999999999999999999999999999999999999999, len=82671957671957671957671957671957671957671957702, g(  470)=1223334444555666666777788888888+9*82671957671957671957671957671957671957671957671
f(n)=       39999999999999999999999999999999999999999999999999999, len=110229276895943562610229276895943562610229276920, g(  471)=1233455566666677788888888+9*110229276895943562610229276895943562610229276895
f(n)=       49999999999999999999999999999999999999999999999999999, len=137786596119929453262786596119929453262786596142, g(  472)=13444556666667788888888+9*137786596119929453262786596119929453262786596119
f(n)=       59999999999999999999999999999999999999999999999999999, len=165343915343915343915343915343915343915343915369, g(  473)=12233344445666666788888888+9*165343915343915343915343915343915343915343915343
f(n)=       69999999999999999999999999999999999999999999999999999, len=192901234567901234567901234567901234567901234587, g(  474)=12334566666688888888+9*192901234567901234567901234567901234567901234567
f(n)=       79999999999999999999999999999999999999999999999999999, len=220458553791887125220458553791887125220458553816, g(  475)=1344466666677777778888888+9*220458553791887125220458553791887125220458553791
f(n)=       89999999999999999999999999999999999999999999999999999, len=248015873015873015873015873015873015873015873048, g(  476)=122333444455555666667777778888888+9*248015873015873015873015873015873015873015873015
f(n)=       99999999999999999999999999999999999999999999999999999, len=275573192239858906525573192239858906525573192266, g(  477)=123345555566666777778888888+9*275573192239858906525573192239858906525573192239
f(n)=      199999999999999999999999999999999999999999999999999999, len=551146384479717813051146384479717813051146384501, g(  478)=1344455556666777888888+9*551146384479717813051146384479717813051146384479
f(n)=      299999999999999999999999999999999999999999999999999999, len=826719576719576719576719576719576719576719576741, g(  479)=1223334444555666788888+9*826719576719576719576719576719576719576719576719
f(n)=      399999999999999999999999999999999999999999999999999999, len=1102292768959435626102292768959435626102292768979, g(  480)=12334555667777777888+9*1102292768959435626102292768959435626102292768959
f(n)=      499999999999999999999999999999999999999999999999999999, len=1377865961199294532627865961199294532627865961214, g(  481)=134445567777788+9*1377865961199294532627865961199294532627865961199
f(n)=      599999999999999999999999999999999999999999999999999999, len=1653439153439153439153439153439153439153439153454, g(  482)=122333444457778+9*1653439153439153439153439153439153439153439153439
f(n)=      699999999999999999999999999999999999999999999999999999, len=1929012345679012345679012345679012345679012345691, g(  483)=123345666666+9*1929012345679012345679012345679012345679012345679
f(n)=      799999999999999999999999999999999999999999999999999999, len=2204585537918871252204585537918871252204585537941, g(  484)=13444666667777778888888+9*2204585537918871252204585537918871252204585537918
f(n)=      899999999999999999999999999999999999999999999999999999, len=2480158730158730158730158730158730158730158730186, g(  485)=1223334444555556667777888888+9*2480158730158730158730158730158730158730158730158
f(n)=      999999999999999999999999999999999999999999999999999999, len=2755731922398589065255731922398589065255731922417, g(  486)=1233455555667788888+9*2755731922398589065255731922398589065255731922398
f(n)=     1999999999999999999999999999999999999999999999999999999, len=5511463844797178130511463844797178130511463844816, g(  487)=1344455556666677778+9*5511463844797178130511463844797178130511463844797
f(n)=     2999999999999999999999999999999999999999999999999999999, len=8267195767195767195767195767195767195767195767222, g(  488)=122333444455567777777888888+9*8267195767195767195767195767195767195767195767195
f(n)=     3999999999999999999999999999999999999999999999999999999, len=11022927689594356261022927689594356261022927689610, g(  489)=1233455566667888+9*11022927689594356261022927689594356261022927689594
f(n)=     4999999999999999999999999999999999999999999999999999999, len=13778659611992945326278659611992945326278659612011, g(  490)=1344455777788888888+9*13778659611992945326278659611992945326278659611992
f(n)=     5999999999999999999999999999999999999999999999999999999, len=16534391534391534391534391534391534391534391534415, g(  491)=122333444456667777778888+9*16534391534391534391534391534391534391534391534391
f(n)=     6999999999999999999999999999999999999999999999999999999, len=19290123456790123456790123456790123456790123456803, g(  492)=1233456666668+9*19290123456790123456790123456790123456790123456790
f(n)=     7999999999999999999999999999999999999999999999999999999, len=22045855379188712522045855379188712522045855379204, g(  493)=1344466777888888+9*22045855379188712522045855379188712522045855379188
f(n)=     8999999999999999999999999999999999999999999999999999999, len=24801587301587301587301587301587301587301587301613, g(  494)=12233344445555566667777788+9*24801587301587301587301587301587301587301587301587
f(n)=     9999999999999999999999999999999999999999999999999999999, len=27557319223985890652557319223985890652557319224003, g(  495)=123345555588888888+9*27557319223985890652557319223985890652557319223985
f(n)=    19999999999999999999999999999999999999999999999999999999, len=55114638447971781305114638447971781305114638447988, g(  496)=13444555568888888+9*55114638447971781305114638447971781305114638447971
f(n)=    29999999999999999999999999999999999999999999999999999999, len=82671957671957671957671957671957671957671957671978, g(  497)=122333444455566888888+9*82671957671957671957671957671957671957671957671957
f(n)=    39999999999999999999999999999999999999999999999999999999, len=110229276895943562610229276895943562610229276895959, g(  498)=1233455566688888+9*110229276895943562610229276895943562610229276895943
f(n)=    49999999999999999999999999999999999999999999999999999999, len=137786596119929453262786596119929453262786596119944, g(  499)=134445566668888+9*137786596119929453262786596119929453262786596119929
f(n)=    59999999999999999999999999999999999999999999999999999999, len=165343915343915343915343915343915343915343915343934, g(  500)=1223334444566666888+9*165343915343915343915343915343915343915343915343915
sum_sg(500) has length 52 last digits are 698412698459839 computed in 87.92 seconds
"""