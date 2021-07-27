import math
import time
from collections import defaultdict
from functools import reduce
from itertools import combinations


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


PREFIX_INFO = defaultdict(list)
PREFIX_V = {}


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
F9 = FACTORIALS[9]

def find_fn(digits_sum):
    for i_str in gen_prospect_fn(digits_sum):
        i = int(i_str)
        n9 = i // FACTORIALS[9]
        distance = i - n9 * FACTORIALS[9]
        if distance <= 299999:
            return i_str, n9, distance


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


class Digits:
    def __init__(self, number):
        if isinstance(number, str):
            number = int(number)
        if isinstance(number, int):
            self.num = list(digits_gen(number * FACTORIALS[9]))
            self.n = number
        else:
            self.num = number.num
            self.n = number.n

    def __str__(self):
        """ Return number value as str """
        return ''.join([chr(d + ord('0')) for d in self.num[::-1]])

    def digits_sum(self):
        return sum(self.num)


    def digits_sum_w6(self):
        return sum(self.num[6:])


    @property
    def value(self):
        """ Return number value as int """
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def skip_to_next(self):
        if len(self.num) > 10 and self.num[5] < 7:
            return True
        else:
            return False

    def inc(self, *, start_digit=6):
        if self.num == [0]:
            self.num = FACTORIAL9.num[:]
            self.n = 1
        else:
            self.n += 1
            carry = 0
            for i, d in enumerate(FACTORIAL9.num):
                self.num[i] += d + carry
                carry = 0
                if self.num[i] > 9:
                    carry = 1
                    self.num[i] -= 10
            if carry == 1:
                for i in range(len(FACTORIAL9.num), len(self.num)):
                    self.num[i] += 1
                    if self.num[i] > 9:
                        self.num[i] -= 10
                        carry = 1
                    else:
                        carry = 0
                        break
                if carry == 1:
                    self.num.append(1)

    def next(self, needed, *, start_digit=6):
        def increase_digit(need, digit):
            inc = min(need, 9 - digit)
            return collect-inc, digit + inc

        def update_value():
            """ Set digits after carry on 1.
            Instead of  0 fill with updated digit
            Eg. 2999 + 1 is 3333 not 3000
            """
            self.num[5] = 7
            for i in range(5):
                self.num[i] = 0
            if self.value % FACTORIALS[9]:
                nn = self.value // FACTORIALS[9] + 1
            else:
                nn = self.value // FACTORIALS[9]
            new_value = nn * FACTORIALS[9]
            assert new_value >= self.value
            self.num = list(digits_gen(new_value))
            self.n = nn
            # print(f'Next from {prev_n:3} {prev} to {nn:3} {self.value}')

        prev = self.value
        prev_n = self.n
        ndx = start_digit
        collect = max(1, needed - self.digits_sum_w6())
        # print(f'value: {prev} sum: {self.digits_sum_w6()}, collect: {collect}')
        for i in range(start_digit, len(self.num)):
            collect, self.num[i] = increase_digit(collect, self.num[i])
            if collect == 0:
                break
        # print(f'value: {self.value} sum: {self.digits_sum_w6()}, collect: {collect}')
        if collect:
            self.num.append(1)
            for i in range(start_digit, len(self.num)-1):
                self.num[i] = 0
            collect = needed - 1
        for i in range(start_digit, len(self.num)):
            collect, self.num[i] = increase_digit(collect, self.num[i])
            if collect == 0:
                break
        update_value()
        return self


DEBUG = False
PREFIX_MAX = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6,
              6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8]
FACTORIALS = [math.factorial(i) for i in range(10)]

FACTORIAL9 = Digits(1)


def rrange(i):
    for n in reversed(range(i)):
        yield n



def single_digit_sum(n):
    while (n := digits_sum(n)) > 9:
        pass
    return n


def digits_sum(n):
    if isinstance(n, int):
        return sum([d for d in digits_gen(n)])
    elif isinstance(n, str):
        return sum([ord(d) - ord('0') for d in n])
    else:
        return sum([d for d in n.digits_gen()])


n9mod = {}

if __name__ == '__main__':
    number = 1
    for i in range(10000):
        mod = number % F9
        number = number * 10
        # print(f"mod={mod:6}, i={i:100}")
        if mod == 202240:
            print(f"mod={mod:6}, i={i:100}")
    exit()


    init_prefixes()
    for i in range(90, 101):

        fn, n9, d = find_fn(i)
        print(f'g({i}) = {PREFIX_V[d]}+9*{n9}')
    exit()
    # 3125 - mod 10**6 seed/loop
    print(FACTORIALS)
    n = 0
    nvd = Digits(0)
    max_sum = 0
    max_n = 0
    max_nv = 0
    avg = 0
    inc_n = 0
    while True:
        n = nvd.n
        nv = nvd.value
        nmod6 = nv % 1000000
        nmod5 = nv % 100000
        d6 = (nmod6 - nmod5) // 100000
        prefix_inc = min(9 - d6, 2) + 45 - digits_sum(nmod5)
        suffix_sum = digits_sum(nv)
        max_inc = suffix_sum + prefix_inc
        if max_inc > max_sum:
            max_nv = nv
            max_num = nvd.num[:]
            max_sum = max_inc
            if max_n:
                inc_n = (n - max_n) / max_n
            max_n = n
            nv_len = len(str(nv))
            if nv_len > 5:
                avg = digits_sum(nv - nmod5) / (nv_len - 5)
            print(f'For n={n:10} max sum is {max_inc:3} with prefix = {prefix_inc:2} '
                  f'on value {nv // 100000:20} avg digit is {avg:.2f} with inc n increase {inc_n:.4f}')
        if n9mod.get(nmod6, None) is None:
            n9mod[nmod6] = n
        nvd.inc()
        if digits_sum(nvd.value) < max_sum - 50:
            nvd.next(max(1, max_sum - 55))

        if n > 2000:
            pass
            # exit()




'''
[1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
For n=         0 max sum is  47 with prefix = 47 on value                    0 avg digit is 0.00 with inc n increase 0.0000
For n=         1 max sum is  50 with prefix = 23 on value                    3 avg digit is 3.00 with inc n increase 0.0000
For n=         2 max sum is  54 with prefix = 27 on value                    7 avg digit is 7.00 with inc n increase 1.0000
For n=         5 max sum is  55 with prefix = 37 on value                   18 avg digit is 4.50 with inc n increase 1.5000
For n=         8 max sum is  56 with prefix = 38 on value                   29 avg digit is 5.50 with inc n increase 0.6000
For n=        11 max sum is  57 with prefix = 21 on value                   39 avg digit is 6.00 with inc n increase 0.3750
For n=        13 max sum is  58 with prefix = 31 on value                   47 avg digit is 5.50 with inc n increase 0.1818
For n=        16 max sum is  59 with prefix = 32 on value                   58 avg digit is 6.50 with inc n increase 0.2308
For n=        19 max sum is  60 with prefix = 24 on value                   68 avg digit is 7.00 with inc n increase 0.1875
For n=        22 max sum is  61 with prefix = 25 on value                   79 avg digit is 8.00 with inc n increase 0.1579
For n=        24 max sum is  62 with prefix = 35 on value                   87 avg digit is 7.50 with inc n increase 0.0909
For n=        27 max sum is  63 with prefix = 18 on value                   97 avg digit is 8.00 with inc n increase 0.1250
For n=        55 max sum is  64 with prefix = 28 on value                  199 avg digit is 6.33 with inc n increase 1.0370
For n=        82 max sum is  65 with prefix = 29 on value                  297 avg digit is 6.00 with inc n increase 0.4909
For n=       110 max sum is  66 with prefix = 30 on value                  399 avg digit is 7.00 with inc n increase 0.3415
For n=       137 max sum is  67 with prefix = 31 on value                  497 avg digit is 6.67 with inc n increase 0.2455
For n=       165 max sum is  68 with prefix = 32 on value                  598 avg digit is 7.33 with inc n increase 0.2044
For n=       217 max sum is  69 with prefix = 24 on value                  787 avg digit is 7.33 with inc n increase 0.3152
For n=       220 max sum is  70 with prefix = 34 on value                  798 avg digit is 8.00 with inc n increase 0.0138
For n=       248 max sum is  71 with prefix = 26 on value                  899 avg digit is 8.67 with inc n increase 0.1273
For n=       275 max sum is  72 with prefix = 36 on value                  997 avg digit is 8.33 with inc n increase 0.1089
For n=       551 max sum is  73 with prefix = 19 on value                 1999 avg digit is 7.00 with inc n increase 1.0036
For n=       826 max sum is  74 with prefix = 20 on value                 2997 avg digit is 6.75 with inc n increase 0.4991
For n=      1102 max sum is  75 with prefix = 21 on value                 3998 avg digit is 7.25 with inc n increase 0.3341
For n=      1650 max sum is  76 with prefix = 40 on value                 5987 avg digit is 7.25 with inc n increase 0.4973
For n=      1653 max sum is  77 with prefix = 32 on value                 5998 avg digit is 7.75 with inc n increase 0.0018
For n=      1929 max sum is  78 with prefix = 24 on value                 6999 avg digit is 8.25 with inc n increase 0.1670
For n=      2204 max sum is  79 with prefix = 25 on value                 7997 avg digit is 8.00 with inc n increase 0.1426
For n=      2480 max sum is  80 with prefix = 35 on value                 8999 avg digit is 8.75 with inc n increase 0.1252
For n=      2755 max sum is  81 with prefix = 36 on value                 9997 avg digit is 8.50 with inc n increase 0.1109
For n=      5511 max sum is  82 with prefix = 28 on value                19998 avg digit is 7.20 with inc n increase 1.0004
For n=      8267 max sum is  83 with prefix = 20 on value                29999 avg digit is 7.60 with inc n increase 0.5001
For n=     13503 max sum is  84 with prefix = 21 on value                48999 avg digit is 7.80 with inc n increase 0.6334
For n=     13778 max sum is  85 with prefix = 31 on value                49997 avg digit is 7.60 with inc n increase 0.0204
For n=     16534 max sum is  86 with prefix = 23 on value                59998 avg digit is 8.00 with inc n increase 0.2000
For n=     19290 max sum is  87 with prefix = 33 on value                69999 avg digit is 8.40 with inc n increase 0.1667
For n=     24526 max sum is  88 with prefix = 16 on value                88999 avg digit is 8.60 with inc n increase 0.2714
For n=     24801 max sum is  89 with prefix = 17 on value                89997 avg digit is 8.40 with inc n increase 0.0112
For n=     27557 max sum is  90 with prefix = 27 on value                99998 avg digit is 8.80 with inc n increase 0.1111
For n=     55114 max sum is  91 with prefix = 28 on value               199997 avg digit is 7.33 with inc n increase 1.0000
For n=    107473 max sum is  92 with prefix = 38 on value               389998 avg digit is 7.67 with inc n increase 0.9500
For n=    110229 max sum is  93 with prefix = 21 on value               399998 avg digit is 7.83 with inc n increase 0.0256
For n=    137786 max sum is  94 with prefix = 22 on value               499997 avg digit is 7.83 with inc n increase 0.2500
For n=    190145 max sum is  95 with prefix = 32 on value               689998 avg digit is 8.17 with inc n increase 0.3800
For n=    192901 max sum is  96 with prefix = 24 on value               699999 avg digit is 8.50 with inc n increase 0.0145
For n=    220458 max sum is  97 with prefix = 25 on value               799997 avg digit is 8.33 with inc n increase 0.1429
For n=    272817 max sum is  98 with prefix = 26 on value               989998 avg digit is 8.67 with inc n increase 0.2375
For n=    275573 max sum is  99 with prefix = 36 on value               999999 avg digit is 9.00 with inc n increase 0.0101
For n=    551146 max sum is 100 with prefix = 28 on value              1999998 avg digit is 7.71 with inc n increase 1.0000
For n=    826719 max sum is 101 with prefix = 29 on value              2999997 avg digit is 7.71 with inc n increase 0.5000
For n=   1102292 max sum is 102 with prefix = 30 on value              3999997 avg digit is 7.86 with inc n increase 0.3333
For n=   1650683 max sum is 103 with prefix = 31 on value              5989998 avg digit is 8.14 with inc n increase 0.4975
For n=   1653439 max sum is 104 with prefix = 32 on value              5999999 avg digit is 8.43 with inc n increase 0.0017
For n=   1929012 max sum is 105 with prefix = 24 on value              6999998 avg digit is 8.43 with inc n increase 0.1667
For n=   2204585 max sum is 106 with prefix = 34 on value              7999998 avg digit is 8.57 with inc n increase 0.1429
For n=   2480158 max sum is 107 with prefix = 35 on value              8999997 avg digit is 8.57 with inc n increase 0.1250
For n=   5235890 max sum is 108 with prefix = 36 on value             18999997 avg digit is 7.62 with inc n increase 1.1111
For n=   7991622 max sum is 109 with prefix = 28 on value             28999997 avg digit is 7.75 with inc n increase 0.5263
For n=   8267195 max sum is 110 with prefix = 38 on value             29999997 avg digit is 7.88 with inc n increase 0.0345
For n=  11022927 max sum is 111 with prefix = 21 on value             39999997 avg digit is 8.00 with inc n increase 0.3333
For n=  13778659 max sum is 112 with prefix = 22 on value             49999997 avg digit is 8.12 with inc n increase 0.2500
For n=  16534391 max sum is 113 with prefix = 32 on value             59999998 avg digit is 8.38 with inc n increase 0.2000
For n=  19290123 max sum is 114 with prefix = 33 on value             69999998 avg digit is 8.50 with inc n increase 0.1667
For n=  22045855 max sum is 115 with prefix = 34 on value             79999998 avg digit is 8.62 with inc n increase 0.1429
For n=  24801587 max sum is 116 with prefix = 26 on value             89999998 avg digit is 8.75 with inc n increase 0.1250
For n=  27557319 max sum is 117 with prefix = 27 on value             99999999 avg digit is 9.00 with inc n increase 0.1111
For n=  55114638 max sum is 118 with prefix = 28 on value            199999998 avg digit is 8.00 with inc n increase 1.0000
For n=  82671957 max sum is 119 with prefix = 29 on value            299999997 avg digit is 8.00 with inc n increase 0.5000
For n= 135030864 max sum is 120 with prefix = 30 on value            489999999 avg digit is 8.33 with inc n increase 0.6333
For n= 137786596 max sum is 121 with prefix = 22 on value            499999999 avg digit is 8.44 with inc n increase 0.0204
For n= 165343915 max sum is 122 with prefix = 32 on value            599999998 avg digit is 8.44 with inc n increase 0.2000
For n= 192901234 max sum is 123 with prefix = 24 on value            699999997 avg digit is 8.44 with inc n increase 0.1667
For n= 220458553 max sum is 124 with prefix = 34 on value            799999997 avg digit is 8.56 with inc n increase 0.1429
For n= 248015873 max sum is 125 with prefix = 26 on value            899999999 avg digit is 8.89 with inc n increase 0.1250
For n= 275573192 max sum is 126 with prefix = 27 on value            999999999 avg digit is 9.00 with inc n increase 0.1111
For n= 551146384 max sum is 127 with prefix = 28 on value           1999999998 avg digit is 8.10 with inc n increase 1.0000
'''