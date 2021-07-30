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
        return sum([int(ch) for ch in n])
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
        return ''.join([str(d) for d in self.num[::-1]])

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


def g_sequence(max_i):
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

    print(f'Verify up to {len(sg_table)} sg values!')
    for i, sg_sum in enumerate(sg_table, 1):
        if sg_cache.get(i) and sg_cache.get(i) != sg_sum:
            print(f'Assertion error sg({i}) is {sg_cache.get(i, 0)} while expected {sg_sum}')


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


def print_const_tables():
    print(f'g_cache size {len(g_cache)}')
    g_table = [(g.prefix, g.suffix_len) for g in dic_as_list(g_cache)]
    print(f'g_table = {g_table}')
    print(f'sg_table = {dic_as_list(sg_cache)}')


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
    # print_const_tables()


if __name__ == "__main__":
    DEBUG = True
    # hacker_main()
    # profile_main(100)
    development_main(250)
    # assert_gen()
    exit()

"""
sum_sg(100) is 19846950 computed in 59.06 seconds
sum_sg(150) is 8184523820510 computed in 61.08 seconds
sum_sg(200) is 2728174603174619234 computed in 62.22 seconds
sum_sg(250) is 1016865079365079365100280 computed in 54.30 seconds

cost:       999993, len=1                    , f(n) =                                        1, g(1) = 1+9*0
cost:       999978, len=1                    , f(n) =                                        2, g(2) = 2+9*0
cost:       999937, len=1                    , f(n) =                                      120, g(3) = 5+9*0
cost:       999846, len=2                    , f(n) =                                      121, g(4) = 15+9*0
cost:       999664, len=2                    , f(n) =                                      122, g(5) = 25+9*0
cost:       399350, len=1                    , f(n) =                                        6, g(6) = 3+9*0
cost:       998746, len=2                    , f(n) =                                        7, g(7) = 13+9*0
cost:       797789, len=2                    , f(n) =                                        8, g(8) = 23+9*0
cost:       396618, len=1                    , f(n) =                                      720, g(9) = 6+9*0
cost:       724020, len=2                    , f(n) =                                      721, g(10) = 16+9*0
cost:       720720, len=2                    , f(n) =                                      722, g(11) = 26+9*0
cost:       716069, len=2                    , f(n) =                                       48, g(12) = 44+9*0
cost:      1064671, len=3                    , f(n) =                                       49, g(13) = 144+9*0
cost:      1054149, len=3                    , f(n) =                                      842, g(14) = 256+9*0
cost:       686354, len=2                    , f(n) =                                      726, g(15) = 36+9*0
cost:      1023277, len=3                    , f(n) =                                      727, g(16) = 136+9*0
cost:      1001965, len=3                    , f(n) =                                      728, g(17) = 236+9*0
cost:       635277, len=2                    , f(n) =                                     5760, g(18) = 67+9*0
cost:       944651, len=3                    , f(n) =                                     5761, g(19) = 167+9*0
cost:       909210, len=3                    , f(n) =                                     5762, g(20) = 267+9*0
cost:       868881, len=3                    , f(n) =                                   362910, g(21) = 34+9*1
cost:      1085786, len=4                    , f(n) =                                   362911, g(22) = 134+9*1
cost:      1017371, len=4                    , f(n) =                                   362912, g(23) = 234+9*1
cost:       441706, len=2                    , f(n) =                                   362904, g(24) = 4+9*1
cost:       665237, len=3                    , f(n) =                                   362905, g(25) = 14+9*1
cost:       607147, len=3                    , f(n) =                                   362906, g(26) = 24+9*1
cost:       116408, len=1                    , f(n) =                                   362880, g(27) = 9*1
cost:       276800, len=2                    , f(n) =                                   362881, g(28) = 1+9*1
cost:       237689, len=2                    , f(n) =                                   362882, g(29) = 2+9*1
cost:       374124, len=3                    , f(n) =                                   362883, g(30) = 12+9*1
cost:       320743, len=3                    , f(n) =                                   362884, g(31) = 22+9*1
cost:       335883, len=4                    , f(n) =                                   362885, g(32) = 122+9*1
cost:       109250, len=2                    , f(n) =                                   362886, g(33) = 3+9*1
cost:       184626, len=3                    , f(n) =                                   362887, g(34) = 13+9*1
cost:       148620, len=3                    , f(n) =                                   362888, g(35) = 23+9*1
cost:       139380, len=4                    , f(n) =                                   362889, g(36) = 123+9*1
cost:       157346, len=5                    , f(n) =                                   362899, g(37) = 1333+9*1
cost:       119112, len=5                    , f(n) =                                   725888, g(38) = 235+9*2
cost:        58812, len=4                    , f(n) =                                   367968, g(39) = 447+9*1
cost:        63681, len=5                    , f(n) =                                   367969, g(40) = 1447+9*1
cost:        71714, len=7                    , f(n) =                                   368888, g(41) = 235567+9*1
cost:        45232, len=6                    , f(n) =                                   367998, g(42) = 34447+9*1
cost:        33655, len=7                    , f(n) =                                   367999, g(43) = 134447+9*1
cost:        22025, len=7                    , f(n) =                                   488888, g(44) = 237888+9*1
cost:        20992, len=8                    , f(n) =                                   488889, g(45) = 1237888+9*1
cost:        16082, len=9                    , f(n) =                                   488899, g(46) = 13337888+9*1
cost:        10646, len=10                   , f(n) =                                   887888, g(47) = 23568888+9*2
cost:         9934, len=11                   , f(n) =                                   887889, g(48) = 123568888+9*2
cost:         6133, len=12                   , f(n) =                                   887899, g(49) = 1333568888+9*2
cost:         6315, len=14                   , f(n) =                                   897989, g(50) = 122456778888+9*2
cost:         3396, len=14                   , f(n) =                                   889998, g(51) = 344466668888+9*2
cost:         1715, len=15                   , f(n) =                                   889999, g(52) = 1344466668888+9*2
cost:         1715, len=17                   , f(n) =                                  2988989, g(53) = 122455788+9*8
cost:          799, len=18                   , f(n) =                                  2988999, g(54) = 1233455788+9*8
cost:          470, len=19                   , f(n) =                                  3998899, g(55) = 13336667+9*11
cost:          792, len=23                   , f(n) =                                  3999989, g(56) = 122455566667+9*11
cost:          358, len=24                   , f(n) =                                  3999999, g(57) = 1233455566667+9*11
cost:          330, len=25                   , f(n) =                                  6899899, g(58) = 133357+9*19
cost:          330, len=30                   , f(n) =                                  7989989, g(59) = 12245667+9*22
cost:          120, len=31                   , f(n) =                                  7989999, g(60) = 123345667+9*22
cost:           36, len=32                   , f(n) =                                  7999999, g(61) = 1344466777+9*22
cost:            8, len=41                   , f(n) =                                  9999989, g(62) = 12245555588888+9*27
cost:            1, len=42                   , f(n) =                                  9999999, g(63) = 123345555588888+9*27
cost:            1, len=66                   , f(n) =                                 19999999, g(64) = 13444555568+9*55
cost:            1, len=103                  , f(n) =                                 29999999, g(65) = 122333444455566888888+9*82
cost:            1, len=123                  , f(n) =                                 39999999, g(66) = 1233455566688+9*110
cost:            1, len=155                  , f(n) =                                 49999999, g(67) = 134445566668888888+9*137
cost:            1, len=184                  , f(n) =                                 59999999, g(68) = 1223334444566666888+9*165
cost:            1, len=212                  , f(n) =                                 69999999, g(69) = 12334566666688888888+9*192
cost:            1, len=230                  , f(n) =                                 79999999, g(70) = 1344478888+9*220
cost:            1, len=264                  , f(n) =                                 89999999, g(71) = 1223334444555557+9*248
cost:            1, len=292                  , f(n) =                                 99999999, g(72) = 12334555556788888+9*275
cost:            1, len=566                  , f(n) =                                199999999, g(73) = 134445555666778+9*551
cost:            1, len=853                  , f(n) =                                299999999, g(74) = 122333444455566666777888888+9*826
cost:            1, len=1117                 , f(n) =                                399999999, g(75) = 123345557777788+9*1102
cost:            1, len=1399                 , f(n) =                                499999999, g(76) = 1344455667777778888888+9*1377
cost:            1, len=1678                 , f(n) =                                599999999, g(77) = 1223334444566667777777888+9*1653
cost:            1, len=1941                 , f(n) =                                699999999, g(78) = 123345666666+9*1929
cost:            1, len=2217                 , f(n) =                                799999999, g(79) = 1344467788888+9*2204
cost:            1, len=2501                 , f(n) =                                899999999, g(80) = 122333444455555667778+9*2480
cost:            1, len=2779                 , f(n) =                                999999999, g(81) = 123345555566667777888888+9*2755
cost:            1, len=5527                 , f(n) =                               1999999999, g(82) = 1344455556678888+9*5511
cost:            1, len=8287                 , f(n) =                               2999999999, g(83) = 12233344445557777778+9*8267
cost:            1, len=11045                , f(n) =                               3999999999, g(84) = 12334555666667788888888+9*11022
cost:            1, len=13800                , f(n) =                               4999999999, g(85) = 1344455666777777788888+9*13778
cost:            1, len=16553                , f(n) =                               5999999999, g(86) = 1223334444567777888+9*16534
cost:            1, len=19303                , f(n) =                               6999999999, g(87) = 1233456666668+9*19290
cost:            1, len=22066                , f(n) =                               7999999999, g(88) = 134446666777778888888+9*22045
cost:            1, len=24824                , f(n) =                               8999999999, g(89) = 12233344445555567788888+9*24801
cost:            1, len=27581                , f(n) =                               9999999999, g(90) = 123345555566666677777788+9*27557
cost:            1, len=55139                , f(n) =                              19999999999, g(91) = 1344455556666667777788888+9*55114
cost:            1, len=82702                , f(n) =                              29999999999, g(92) = 1223334444555666666777788888888+9*82671
cost:            1, len=110248               , f(n) =                              39999999999, g(93) = 1233455566666677788+9*110229
cost:            1, len=137806               , f(n) =                              49999999999, g(94) = 13444556666667788888+9*137786
cost:            1, len=165369               , f(n) =                              59999999999, g(95) = 12233344445666666788888888+9*165343
cost:            1, len=192915               , f(n) =                              69999999999, g(96) = 12334566666688+9*192901
cost:            1, len=220480               , f(n) =                              79999999999, g(97) = 1344466666677777778888+9*220458
cost:            1, len=248048               , f(n) =                              89999999999, g(98) = 122333444455555666667777778888888+9*248015
cost:            1, len=275594               , f(n) =                              99999999999, g(99) = 123345555566666777778+9*275573
cost:            1, len=551165               , f(n) =                             199999999999, g(100) = 1344455556666777888+9*551146
cost:            1, len=826741               , f(n) =                             299999999999, g(101) = 1223334444555666788888+9*826719
cost:            1, len=1102315              , f(n) =                             399999999999, g(102) = 12334555667777777888888+9*1102292
cost:            1, len=1377886              , f(n) =                             499999999999, g(103) = 134445567777788888888+9*1377865
cost:            1, len=1653454              , f(n) =                             599999999999, g(104) = 122333444457778+9*1653439
cost:            1, len=1929027              , f(n) =                             699999999999, g(105) = 123345666666888+9*1929012
cost:            1, len=2204605              , f(n) =                             799999999999, g(106) = 13444666667777778888+9*2204585
cost:            1, len=2480186              , f(n) =                             899999999999, g(107) = 1223334444555556667777888888+9*2480158
cost:            1, len=2755753              , f(n) =                             999999999999, g(108) = 1233455555667788888888+9*2755731
cost:            1, len=5511488              , f(n) =                            1999999999999, g(109) = 1344455556666677778888888+9*5511463
cost:            1, len=8267222              , f(n) =                            2999999999999, g(110) = 122333444455567777777888888+9*8267195
cost:            1, len=11022946             , f(n) =                            3999999999999, g(111) = 1233455566667888888+9*11022927
cost:            1, len=13778675             , f(n) =                            4999999999999, g(112) = 1344455777788888+9*13778659
cost:            1, len=16534415             , f(n) =                            5999999999999, g(113) = 122333444456667777778888+9*16534391
cost:            1, len=19290139             , f(n) =                            6999999999999, g(114) = 1233456666668888+9*19290123
cost:            1, len=22045868             , f(n) =                            7999999999999, g(115) = 1344466777888+9*22045855
cost:            1, len=24801613             , f(n) =                            8999999999999, g(116) = 12233344445555566667777788+9*24801587
cost:            1, len=27557331             , f(n) =                            9999999999999, g(117) = 123345555588+9*27557319
cost:            1, len=55114652             , f(n) =                           19999999999999, g(118) = 13444555568888+9*55114638
cost:            1, len=82671978             , f(n) =                           29999999999999, g(119) = 122333444455566888888+9*82671957
cost:            1, len=110229295            , f(n) =                           39999999999999, g(120) = 1233455566688888888+9*110229276
cost:            1, len=137786608            , f(n) =                           49999999999999, g(121) = 134445566668+9*137786596
cost:            1, len=165343934            , f(n) =                           59999999999999, g(122) = 1223334444566666888+9*165343915
cost:            1, len=192901251            , f(n) =                           69999999999999, g(123) = 12334566666688888+9*192901234
cost:            1, len=220458566            , f(n) =                           79999999999999, g(124) = 1344478888888+9*220458553
cost:            1, len=248015889            , f(n) =                           89999999999999, g(125) = 1223334444555557+9*248015873
cost:            1, len=275573206            , f(n) =                           99999999999999, g(126) = 12334555556788+9*275573192
cost:            1, len=551146402            , f(n) =                          199999999999999, g(127) = 134445555666778888+9*551146384
cost:            1, len=826719603            , f(n) =                          299999999999999, g(128) = 122333444455566666777888888+9*826719576
cost:            1, len=1102292789           , f(n) =                          399999999999999, g(129) = 123345557777788888888+9*1102292768
cost:            1, len=1377865977           , f(n) =                          499999999999999, g(130) = 1344455667777778+9*1377865961
cost:            1, len=1653439178           , f(n) =                          599999999999999, g(131) = 1223334444566667777777888+9*1653439153
cost:            1, len=1929012363           , f(n) =                          699999999999999, g(132) = 123345666666888888+9*1929012345
cost:            1, len=2204585553           , f(n) =                          799999999999999, g(133) = 1344467788888888+9*2204585537
cost:            1, len=2480158751           , f(n) =                          899999999999999, g(134) = 122333444455555667778+9*2480158730
cost:            1, len=2755731943           , f(n) =                          999999999999999, g(135) = 123345555566667777888+9*2755731922
cost:            1, len=5511463863           , f(n) =                         1999999999999999, g(136) = 1344455556678888888+9*5511463844
cost:            1, len=8267195787           , f(n) =                         2999999999999999, g(137) = 12233344445557777778+9*8267195767
cost:            1, len=11022927709          , f(n) =                         3999999999999999, g(138) = 12334555666667788888+9*11022927689
cost:            1, len=13778659636          , f(n) =                         4999999999999999, g(139) = 1344455666777777788888888+9*13778659611
cost:            1, len=16534391553          , f(n) =                         5999999999999999, g(140) = 1223334444567777888+9*16534391534
cost:            1, len=19290123475          , f(n) =                         6999999999999999, g(141) = 1233456666668888888+9*19290123456
cost:            1, len=22045855394          , f(n) =                         7999999999999999, g(142) = 134446666777778+9*22045855379
cost:            1, len=24801587324          , f(n) =                         8999999999999999, g(143) = 12233344445555567788888+9*24801587301
cost:            1, len=27557319253          , f(n) =                         9999999999999999, g(144) = 123345555566666677777788888888+9*27557319223
cost:            1, len=55114638475          , f(n) =                        19999999999999999, g(145) = 1344455556666667777788888888+9*55114638447
cost:            1, len=82671957702          , f(n) =                        29999999999999999, g(146) = 1223334444555666666777788888888+9*82671957671
cost:            1, len=110229276920         , f(n) =                        39999999999999999, g(147) = 1233455566666677788888888+9*110229276895
cost:            1, len=137786596142         , f(n) =                        49999999999999999, g(148) = 13444556666667788888888+9*137786596119
cost:            1, len=165343915369         , f(n) =                        59999999999999999, g(149) = 12233344445666666788888888+9*165343915343
cost:            1, len=192901234587         , f(n) =                        69999999999999999, g(150) = 12334566666688888888+9*192901234567
cost:            1, len=220458553816         , f(n) =                        79999999999999999, g(151) = 1344466666677777778888888+9*220458553791
cost:            1, len=248015873048         , f(n) =                        89999999999999999, g(152) = 122333444455555666667777778888888+9*248015873015
cost:            1, len=275573192266         , f(n) =                        99999999999999999, g(153) = 123345555566666777778888888+9*275573192239
cost:            1, len=551146384501         , f(n) =                       199999999999999999, g(154) = 1344455556666777888888+9*551146384479
cost:            1, len=826719576741         , f(n) =                       299999999999999999, g(155) = 1223334444555666788888+9*826719576719
cost:            1, len=1102292768979        , f(n) =                       399999999999999999, g(156) = 12334555667777777888+9*1102292768959
cost:            1, len=1377865961214        , f(n) =                       499999999999999999, g(157) = 134445567777788+9*1377865961199
cost:            1, len=1653439153454        , f(n) =                       599999999999999999, g(158) = 122333444457778+9*1653439153439
cost:            1, len=1929012345691        , f(n) =                       699999999999999999, g(159) = 123345666666+9*1929012345679
cost:            1, len=2204585537941        , f(n) =                       799999999999999999, g(160) = 13444666667777778888888+9*2204585537918
cost:            1, len=2480158730186        , f(n) =                       899999999999999999, g(161) = 1223334444555556667777888888+9*2480158730158
cost:            1, len=2755731922417        , f(n) =                       999999999999999999, g(162) = 1233455555667788888+9*2755731922398
cost:            1, len=5511463844816        , f(n) =                      1999999999999999999, g(163) = 1344455556666677778+9*5511463844797
cost:            1, len=8267195767222        , f(n) =                      2999999999999999999, g(164) = 122333444455567777777888888+9*8267195767195
cost:            1, len=11022927689610       , f(n) =                      3999999999999999999, g(165) = 1233455566667888+9*11022927689594
cost:            1, len=13778659612011       , f(n) =                      4999999999999999999, g(166) = 1344455777788888888+9*13778659611992
cost:            1, len=16534391534415       , f(n) =                      5999999999999999999, g(167) = 122333444456667777778888+9*16534391534391
cost:            1, len=19290123456803       , f(n) =                      6999999999999999999, g(168) = 1233456666668+9*19290123456790
cost:            1, len=22045855379204       , f(n) =                      7999999999999999999, g(169) = 1344466777888888+9*22045855379188
cost:            1, len=24801587301613       , f(n) =                      8999999999999999999, g(170) = 12233344445555566667777788+9*24801587301587
cost:            1, len=27557319224003       , f(n) =                      9999999999999999999, g(171) = 123345555588888888+9*27557319223985
cost:            1, len=55114638447988       , f(n) =                     19999999999999999999, g(172) = 13444555568888888+9*55114638447971
cost:            1, len=82671957671978       , f(n) =                     29999999999999999999, g(173) = 122333444455566888888+9*82671957671957
cost:            1, len=110229276895959      , f(n) =                     39999999999999999999, g(174) = 1233455566688888+9*110229276895943
cost:            1, len=137786596119944      , f(n) =                     49999999999999999999, g(175) = 134445566668888+9*137786596119929
cost:            1, len=165343915343934      , f(n) =                     59999999999999999999, g(176) = 1223334444566666888+9*165343915343915
cost:            1, len=192901234567915      , f(n) =                     69999999999999999999, g(177) = 12334566666688+9*192901234567901
cost:            1, len=220458553791894      , f(n) =                     79999999999999999999, g(178) = 1344478+9*220458553791887
cost:            1, len=248015873015889      , f(n) =                     89999999999999999999, g(179) = 1223334444555557+9*248015873015873
cost:            1, len=275573192239878      , f(n) =                     99999999999999999999, g(180) = 12334555556788888888+9*275573192239858
cost:            1, len=551146384479738      , f(n) =                    199999999999999999999, g(181) = 134445555666778888888+9*551146384479717
cost:            1, len=826719576719603      , f(n) =                    299999999999999999999, g(182) = 122333444455566666777888888+9*826719576719576
cost:            1, len=1102292768959453     , f(n) =                    399999999999999999999, g(183) = 123345557777788888+9*1102292768959435
cost:            1, len=1377865961199313     , f(n) =                    499999999999999999999, g(184) = 1344455667777778888+9*1377865961199294
cost:            1, len=1653439153439178     , f(n) =                    599999999999999999999, g(185) = 1223334444566667777777888+9*1653439153439153
cost:            1, len=1929012345679027     , f(n) =                    699999999999999999999, g(186) = 123345666666888+9*1929012345679012
cost:            1, len=2204585537918881     , f(n) =                    799999999999999999999, g(187) = 1344467788+9*2204585537918871
cost:            1, len=2480158730158751     , f(n) =                    899999999999999999999, g(188) = 122333444455555667778+9*2480158730158730
cost:            1, len=2755731922398607     , f(n) =                    999999999999999999999, g(189) = 123345555566667777+9*2755731922398589
cost:            1, len=5511463844797191     , f(n) =                   1999999999999999999999, g(190) = 1344455556678+9*5511463844797178
cost:            1, len=8267195767195787     , f(n) =                   2999999999999999999999, g(191) = 12233344445557777778+9*8267195767195767
cost:            1, len=11022927689594373    , f(n) =                   3999999999999999999999, g(192) = 12334555666667788+9*11022927689594356
cost:            1, len=13778659611992964    , f(n) =                   4999999999999999999999, g(193) = 1344455666777777788+9*13778659611992945
cost:            1, len=16534391534391553    , f(n) =                   5999999999999999999999, g(194) = 1223334444567777888+9*16534391534391534
cost:            1, len=19290123456790139    , f(n) =                   6999999999999999999999, g(195) = 1233456666668888+9*19290123456790123
cost:            1, len=22045855379188730    , f(n) =                   7999999999999999999999, g(196) = 134446666777778888+9*22045855379188712
cost:            1, len=24801587301587324    , f(n) =                   8999999999999999999999, g(197) = 12233344445555567788888+9*24801587301587301
cost:            1, len=27557319223985917    , f(n) =                   9999999999999999999999, g(198) = 123345555566666677777788888+9*27557319223985890
cost:            1, len=55114638447971803    , f(n) =                  19999999999999999999999, g(199) = 1344455556666667777788+9*55114638447971781
cost:            1, len=82671957671957702    , f(n) =                  29999999999999999999999, g(200) = 1223334444555666666777788888888+9*82671957671957671
cost:            1, len=110229276895943584   , f(n) =                  39999999999999999999999, g(201) = 1233455566666677788888+9*110229276895943562
cost:            1, len=137786596119929470   , f(n) =                  49999999999999999999999, g(202) = 13444556666667788+9*137786596119929453
cost:            1, len=165343915343915369   , f(n) =                  59999999999999999999999, g(203) = 12233344445666666788888888+9*165343915343915343
cost:            1, len=192901234567901251   , f(n) =                  69999999999999999999999, g(204) = 12334566666688888+9*192901234567901234
cost:            1, len=220458553791887144   , f(n) =                  79999999999999999999999, g(205) = 1344466666677777778+9*220458553791887125
cost:            1, len=248015873015873048   , f(n) =                  89999999999999999999999, g(206) = 122333444455555666667777778888888+9*248015873015873015
cost:            1, len=275573192239858930   , f(n) =                  99999999999999999999999, g(207) = 123345555566666777778888+9*275573192239858906
cost:            1, len=551146384479717829   , f(n) =                 199999999999999999999999, g(208) = 1344455556666777+9*551146384479717813
cost:            1, len=826719576719576741   , f(n) =                 299999999999999999999999, g(209) = 1223334444555666788888+9*826719576719576719
cost:            1, len=1102292768959435643  , f(n) =                 399999999999999999999999, g(210) = 12334555667777777+9*1102292768959435626
cost:            1, len=1377865961199294550  , f(n) =                 499999999999999999999999, g(211) = 134445567777788888+9*1377865961199294532
cost:            1, len=1653439153439153454  , f(n) =                 599999999999999999999999, g(212) = 122333444457778+9*1653439153439153439
cost:            1, len=1929012345679012363  , f(n) =                 699999999999999999999999, g(213) = 123345666666888888+9*1929012345679012345
cost:            1, len=2204585537918871269  , f(n) =                 799999999999999999999999, g(214) = 13444666667777778+9*2204585537918871252
cost:            1, len=2480158730158730186  , f(n) =                 899999999999999999999999, g(215) = 1223334444555556667777888888+9*2480158730158730158
cost:            1, len=2755731922398589081  , f(n) =                 999999999999999999999999, g(216) = 1233455555667788+9*2755731922398589065
cost:            1, len=5511463844797178152  , f(n) =                1999999999999999999999999, g(217) = 1344455556666677778888+9*5511463844797178130
cost:            1, len=8267195767195767222  , f(n) =                2999999999999999999999999, g(218) = 122333444455567777777888888+9*8267195767195767195
cost:            1, len=...2927689594356274  , f(n) =                3999999999999999999999999, g(219) = 1233455566667+9*11022927689594356261
cost:            1, len=...8659611992945339  , f(n) =                4999999999999999999999999, g(220) = 1344455777788+9*13778659611992945326
cost:            1, len=...4391534391534415  , f(n) =                5999999999999999999999999, g(221) = 122333444456667777778888+9*16534391534391534391
cost:            1, len=...0123456790123475  , f(n) =                6999999999999999999999999, g(222) = 1233456666668888888+9*19290123456790123456
cost:            1, len=...5855379188712532  , f(n) =                7999999999999999999999999, g(223) = 1344466777+9*22045855379188712522
cost:            1, len=...1587301587301613  , f(n) =                8999999999999999999999999, g(224) = 12233344445555566667777788+9*24801587301587301587
cost:            1, len=...7319223985890667  , f(n) =                9999999999999999999999999, g(225) = 123345555588888+9*27557319223985890652
cost:            1, len=...4638447971781316  , f(n) =               19999999999999999999999999, g(226) = 13444555568+9*55114638447971781305
cost:            1, len=...1957671957671978  , f(n) =               29999999999999999999999999, g(227) = 122333444455566888888+9*82671957671957671957
cost:            1, len=...9276895943562623  , f(n) =               39999999999999999999999999, g(228) = 1233455566688+9*110229276895943562610
cost:            1, len=...6596119929453280  , f(n) =               49999999999999999999999999, g(229) = 134445566668888888+9*137786596119929453262
cost:            1, len=...3915343915343934  , f(n) =               59999999999999999999999999, g(230) = 1223334444566666888+9*165343915343915343915
cost:            1, len=...1234567901234587  , f(n) =               69999999999999999999999999, g(231) = 12334566666688888888+9*192901234567901234567
cost:            1, len=...8553791887125230  , f(n) =               79999999999999999999999999, g(232) = 1344478888+9*220458553791887125220
cost:            1, len=...5873015873015889  , f(n) =               89999999999999999999999999, g(233) = 1223334444555557+9*248015873015873015873
cost:            1, len=...3192239858906542  , f(n) =               99999999999999999999999999, g(234) = 12334555556788888+9*275573192239858906525
cost:            1, len=...6384479717813066  , f(n) =              199999999999999999999999999, g(235) = 134445555666778+9*551146384479717813051
cost:            1, len=...9576719576719603  , f(n) =              299999999999999999999999999, g(236) = 122333444455566666777888888+9*826719576719576719576
cost:            1, len=...2768959435626117  , f(n) =              399999999999999999999999999, g(237) = 123345557777788+9*1102292768959435626102
cost:            1, len=...5961199294532649  , f(n) =              499999999999999999999999999, g(238) = 1344455667777778888888+9*1377865961199294532627
cost:            1, len=...9153439153439178  , f(n) =              599999999999999999999999999, g(239) = 1223334444566667777777888+9*1653439153439153439153
cost:            1, len=...2345679012345691  , f(n) =              699999999999999999999999999, g(240) = 123345666666+9*1929012345679012345679
cost:            1, len=...5537918871252217  , f(n) =              799999999999999999999999999, g(241) = 1344467788888+9*2204585537918871252204
cost:            1, len=...8730158730158751  , f(n) =              899999999999999999999999999, g(242) = 122333444455555667778+9*2480158730158730158730
cost:            1, len=...1922398589065279  , f(n) =              999999999999999999999999999, g(243) = 123345555566667777888888+9*2755731922398589065255
cost:            1, len=...3844797178130527  , f(n) =             1999999999999999999999999999, g(244) = 1344455556678888+9*5511463844797178130511
cost:            1, len=...5767195767195787  , f(n) =             2999999999999999999999999999, g(245) = 12233344445557777778+9*8267195767195767195767
cost:            1, len=...7689594356261045  , f(n) =             3999999999999999999999999999, g(246) = 12334555666667788888888+9*11022927689594356261022
cost:            1, len=...9611992945326300  , f(n) =             4999999999999999999999999999, g(247) = 1344455666777777788888+9*13778659611992945326278
cost:            1, len=...1534391534391553  , f(n) =             5999999999999999999999999999, g(248) = 1223334444567777888+9*16534391534391534391534
cost:            1, len=...3456790123456803  , f(n) =             6999999999999999999999999999, g(249) = 1233456666668+9*19290123456790123456790
cost:            1, len=...5379188712522066  , f(n) =             7999999999999999999999999999, g(250) = 134446666777778888888+9*22045855379188712522045
"""
