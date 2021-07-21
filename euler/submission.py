import math
import time
from collections import defaultdict
from functools import reduce
from itertools import combinations

DEBUG = False

PREFIXES = defaultdict(list)


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
                                    fs_ = sf(prefix)
                                    PREFIXES[fs_].append(prefix)
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
        self.suffix = self.num[:]
        self.sum = self.suffix_digits_sum()
        self.prefix = [0]

    def __str__(self):
        """ Return number value as str """
        return ''.join([chr(d + ord('0')) for d in self.num[::-1]])

    @property
    def value(self):
        """ Return number value as int """
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def digits_sum(self):
        """
        Sum of suffix only digits in  n.
        Does not include 5 least significant digits and max 7 on the 6th least significant digits.
        :return:
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

    def next(self):
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

        def revert_suffix():
            self.num = self.suffix[:]
            assert self.sum == self.suffix_digits_sum()

        def update_value(inc_sum):
            # inc_sum = max(0, self.sum - self.suffix_digits_sum())
            # try to increase digit po position 5 up to 7
            inc_sum, self.num[5] = increase_digit(inc_sum, self.num[5], max_digit=7)
            for i in range(6, len(self.num)):
                inc_sum, self.num[i] = increase_digit(inc_sum, self.num[i])
                if inc_sum == 0:
                    return 0
            return inc_sum

        def next_value_with_sum(sum_needed):
            still_needed = sum_needed - self.suffix_digits_sum()
            while still_needed > 0:
                still_needed = update_value(sum_needed - suffix_sum)
                if still_needed:
                    self.num.append(1)
                    for i in range(0, len(self.num) - 1):
                        self.num[i] = 0
                    still_needed = sum_needed - 1

        def make_suffix_value():
            current_value = self.value
            reminder = current_value % FACTORIALS[9]
            if reminder:
                self.num = list(digits_gen(current_value + FACTORIALS[9] - reminder))
            return self.suffix_digits_sum()

        # Get next suffix value [one 9 digit more so sum is increase by 9!]
        next_value = self.value + FACTORIALS[9]
        self.num = list(digits_gen(next_value))
        suffix_sum = self.suffix_digits_sum()

        while suffix_sum < self.sum:
            next_value_with_sum(self.sum)
            suffix_sum = make_suffix_value()

        self.sum = suffix_sum
        self.suffix = self.num[:]
        assert self.value % FACTORIALS[9] == 0
        self.n = self.value // FACTORIALS[9]
        self.prefix = [0]

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


sf_cache = {}


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
    sf(342) = 5, also sf(25) = 5 and 25 is the smallest number giving sf(i) = 5, so g(5) = 25
    As n start be huge numbers - million and more digits we store in cache sg(n) which is digits sum of n
    Results are in a global cached dictionary
    :param max_i: range for compute g(i) from 1 to max_i
    :return: None
    """

    def g_find(f_number, *, max_cnt=None):
        """
        Founds n such that sf(n) == i
        :param f_number: suffix starting f(n) with n being suffix with f_number. n - 9 digits
        :param max_cnt: optional limit early stop if n not found based on amount of '9' digits
        :return: tuple <prefix value>, prefix len, suffix, len
                    if not found returns None, None, max_cnt
        """
        cost = 0
        while max_cnt is None or f_number.n < max_cnt:
            # exit in case of limit for amount of '9' digits in suffix
            cost += 1
            f_sum = f_number.digits_sum()
            if f_sum == i:
                # found sf(n) = i, where n contains only digits 9
                if DEBUG:
                    print(f'cost: {cost:12}, len={f_number.n:6}, g({i}) = 9*{f_number.n}')
                return 0

            needed_prefix_sum = i - f_sum
            prefix_part_sum = sum(f_number.num[0:6])
            max_prefix_sum = 47 - prefix_part_sum
            if max_prefix_sum < needed_prefix_sum or f_sum > i:
                # print(f'Too small prefix for i={i}  with 9*{n_cnt} and missing digits sum={needed_prefix_sum}')
                f_number.next()
                continue

            prefixes = PREFIXES.get(needed_prefix_sum, [])
            for prefix in prefixes:
                cost += 1
                if digits_sum(f_number.value + f(prefix)) == i:
                    if DEBUG:
                        print(
                            f'cost: {cost:12}, len={len(str(prefix)) + f_number.n:6}, '
                            f'g({i}) = {str(prefix)}+9*{f_number.n}')
                    return prefix
            if prefixes:
                pass
                if DEBUG:
                    print(f'Not found matched prefix for i={i} with 9*{f_number.n} '
                          f'and missing digits sum={needed_prefix_sum}')
            else:
                pass
                if DEBUG:
                    print(f'Missing prefix for i={i}  with 9*{f_number.n} and missing digits sum={needed_prefix_sum}')
            f_number.next()
        # Not found sf(n) = i when d9_counter < max_cnt
        return None

    suffix = FDigits(0)
    for i in range(1, max_i + 1):
        more_results = False
        prefix = g_find(suffix)
        current_len = len(str(prefix)) + suffix.n
        current_suffix = FDigits(suffix)
        suffix.next()
        while suffix.n <= current_len:
            tmp_prefix = g_find(suffix, max_cnt=current_len)
            if tmp_prefix is not None:
                more_results = True
                tmp_len = len(str(tmp_prefix)) + suffix.n
                if tmp_len < current_len:
                    prefix = tmp_prefix
                    current_suffix = FDigits(suffix)
            suffix.next()

        # sf_cache[i] = str(prefix) + '9' * current_suffix.n
        sf_cache[i] = digits_sum(prefix) + 9 * current_suffix.n
        if more_results and DEBUG:
            print(f'Best result for i={i} is {str(prefix)}+9*{current_suffix.n}')
        suffix = current_suffix
    return sf_cache


def sg(i):
    """
    Define  sg(i) as the sum of the digits of g(i).
    So sg(5) = 2 + 5 = 7 as g(5) = 25.
    :param i:
    :return: sum digits of g(i)
    """
    if sf_cache.get(i) is None:
        g_sequence(i)
    return int(sf_cache[i])


def sum_sg_mod(n, m):
    g_sequence(n)
    s = 0
    for i in range(1, n + 1):
        s = (s + sg(i)) % m
    return s


def main():
    q = int(input())
    for _ in range(q):
        n, m = map(int, input().split())
        r = sum_sg_mod(n, m)
        print(r)


def sum_sg(n):
    g_sequence(n)
    # print(sf_cache)
    return sum([sg(i) for i in range(1, n + 1)])


if __name__ == "__main__":
    DEBUG = False
    init_prefixes()
    main()
    exit()
    '''
    pgm_start = time.perf_counter()
    init_prefixes()
    pgm_stop = time.perf_counter()
    print(f"Init prefixes - {pgm_stop - pgm_start:.2f} seconds")
    '''
    pgm_start = time.perf_counter()
    nn = 2000
    total = sum_sg(nn)
    pgm_stop = time.perf_counter()
    print(f"sum_sg({nn}) is {total} computed in {pgm_stop - pgm_start:.2f} seconds")

