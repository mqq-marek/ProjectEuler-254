"""
Euler challenge from HackerRank https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem

Simple optimizations

"""
import math
import time
from collections import defaultdict
from functools import reduce
from itertools import combinations

DEBUG = False

PREFIX_MAX = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6,
              6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8]


FACTORIALS = [math.factorial(i) for i in range(10)]


def digits_gen(n):
    """
    Yields number n digits in reverse sequence. For n = 342 sequence is 2,  4,  3
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


def single_digit_sum(n):
    while (n := digits_sum(n)) > 9:
        pass
    return n


class Digits:
    def __init__(self, number):
        if isinstance(number, int):
            self.num = list(digits_gen(number))
        elif isinstance(number, str):
            self.num = [ord(ch) - ord('0') for ch in number[::-1]]
        else:
            self.num = number.num
        self.suffix_len = sum([1 for d in self.num if d == 9])
        self.prefix_len = len(self.num) - self.suffix_len
        self.prefix_pos = 0

    def __str__(self):
        """ Return number value as str """
        return ''.join([chr(d + ord('0')) for d in self.num[::-1]])

    @property
    def value(self):
        """ Return number value as int """
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def next(self, start_digit=0):
        def set_after_carry_on(k):
            """ Set digits after carry on 1.
            Instead of  0 fill with updated digit
            Eg. 2999 + 1 is 3333 not 3000
            """
            filler = self.num[k]
            copy_len = k - start_digit
            if filler == 9:
                index = len(PREFIX_MAX)
            else:
                index = PREFIX_MAX.index(filler) + 1

            for ndx in range(copy_len):
                if ndx + index < len(PREFIX_MAX):
                    self.num[k - 1 - ndx] = PREFIX_MAX[index + ndx]
                else:
                    self.num[k - 1 - ndx] = 9

        ndx = start_digit
        while True:
            if self.num[ndx] < 9:
                # Non 9 digit so increase it and set all on right to the same value
                self.num[ndx] += 1
                set_after_carry_on(ndx)
                # print(self.value)
                return self
            elif ndx < len(self.num) - 1:
                # if digit 9 then go to next digit
                self.num[ndx] = 0
                ndx += 1
            else:
                # if all digits are 9, then new digit starting with
                self.num.append(1)
                set_after_carry_on(ndx + 1)
                return self

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
    sf(342) = 5,  also sf(25) = 5 and 25 is the smallest number giving sf(i) = 5,  so g(5) = 25
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
    sf(342) = 5,  also sf(25) = 5 and 25 is the smallest number giving sf(i) = 5,  so g(5) = 25
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
                n9 = sum([1 for d in n.num if d == 9])
                diff = f(n) - f(int('0'+'9'*n9))
                print(
                    f"f(n) = {f(n):10}, f({n9:3}*9) = {f(int('0'+'9'*n9)):10}, diff={diff:8}, "
                    f"sf(n) = {i:2}. sg({i:2}) = {digits_sum(n):4}. "
                    f"Time: {stop_time - start_time:8.4f} seconds for n[{len(str(n)):2}] = {str(n):10} "
                )
                print(f"Singe digits for f(n) = {single_digit_sum(f(n))}, "
                      f"f({n9:3}*9) = {single_digit_sum(f(int('0'+'9'*n9)))} "
                      f"f(diff) = {single_digit_sum(diff)}")
        else:
            if DEBUG:
                print(
                    f"f(n) = {f(int(sf_cache[i])):10}, sf(n) = {i:2}. "
                    f"sg({i:2}) = {digits_sum(sf_cache[i]):4}. "
                    f"Time: Already computed For n[{len(str(sf_cache[i])):2}] = {sf_cache[i]:10} "
                )

    return sf_cache


def sg(i):
    """
    Define  sg(i) as the sum of the digits of g(i).
    So sg(5) = 2 + 5 = 7 as g(5) = 25.
    :param i:
    :return: sum digits of g(i)
    """
    return digits_sum(sf_cache[i])


def sum_sg(n):
    g_sequence(n)
    print(sf_cache)
    return sum([sg(i) for i in range(1, n + 1)])


def sum_sg_mod(n, m):
    g_sequence(n)
    s = 0
    for i in range(1, n+1):
        s = (s + sg(i)) % m
    return s

def main():
    q = int(input())
    for _ in range(q):
        n, m = map(int, input().split())
        r = sum_sg_mod(n, m)
        print(r)


if __name__ == "__main__":
    DEBUG = True
    pgm_start = time.perf_counter()
    nn = 70
    total = sum_sg(nn)
    pgm_stop = time.perf_counter()
    print(f"sum_sg({nn}) is {total} computed in {pgm_stop - pgm_start:.2f} seconds")
    """
For n = 1          sf(n) =  1. sg( 1) =  1. Time:   0.0000 seconds
For n = 2          sf(n) =  2. sg( 2) =  2. Time:   0.0000 seconds
For n = 5          sf(n) =  3. sg( 3) =  5. Time:   0.0000 seconds
For n = 15         sf(n) =  4. sg( 4) =  6. Time:   0.0000 seconds
For n = 25         sf(n) =  5. sg( 5) =  7. Time:   0.0000 seconds
For n = 3          sf(n) =  6. sg( 6) =  3. Time: Computed in earlier step
For n = 13         sf(n) =  7. sg( 7) =  4. Time: Computed in earlier step
For n = 23         sf(n) =  8. sg( 8) =  5. Time: Computed in earlier step
For n = 6          sf(n) =  9. sg( 9) =  6. Time: Computed in earlier step
For n = 16         sf(n) = 10. sg(10) =  7. Time: Computed in earlier step
For n = 26         sf(n) = 11. sg(11) =  8. Time:   0.0000 seconds
For n = 44         sf(n) = 12. sg(12) =  8. Time:   0.0000 seconds
For n = 144        sf(n) = 13. sg(13) =  9. Time:   0.0002 seconds
For n = 256        sf(n) = 14. sg(14) = 13. Time:   0.0002 seconds
For n = 36         sf(n) = 15. sg(15) =  9. Time: Computed in earlier step
For n = 136        sf(n) = 16. sg(16) = 10. Time: Computed in earlier step
For n = 236        sf(n) = 17. sg(17) = 11. Time: Computed in earlier step
For n = 67         sf(n) = 18. sg(18) = 13. Time: Computed in earlier step
For n = 167        sf(n) = 19. sg(19) = 14. Time: Computed in earlier step
For n = 267        sf(n) = 20. sg(20) = 15. Time:   0.0000 seconds
For n = 446        sf(n) = 21. sg(21) = 14. Time:   0.0001 seconds
For n = 1446       sf(n) = 22. sg(22) = 15. Time:   0.0007 seconds
For n = 2567       sf(n) = 23. sg(23) = 20. Time:   0.0005 seconds
For n = 49         sf(n) = 24. sg(24) = 13. Time: Computed in earlier step
For n = 149        sf(n) = 25. sg(25) = 14. Time: Computed in earlier step
For n = 249        sf(n) = 26. sg(26) = 15. Time: Computed in earlier step
For n = 9          sf(n) = 27. sg(27) =  9. Time: Computed in earlier step
For n = 19         sf(n) = 28. sg(28) = 10. Time: Computed in earlier step
For n = 29         sf(n) = 29. sg(29) = 11. Time: Computed in earlier step
For n = 129        sf(n) = 30. sg(30) = 12. Time: Computed in earlier step
For n = 229        sf(n) = 31. sg(31) = 13. Time: Computed in earlier step
For n = 1229       sf(n) = 32. sg(32) = 14. Time:   0.0008 seconds
For n = 39         sf(n) = 33. sg(33) = 12. Time: Computed in earlier step
For n = 139        sf(n) = 34. sg(34) = 13. Time: Computed in earlier step
For n = 239        sf(n) = 35. sg(35) = 14. Time: Computed in earlier step
For n = 1239       sf(n) = 36. sg(36) = 15. Time:   0.0000 seconds
For n = 13339      sf(n) = 37. sg(37) = 19. Time:   0.0046 seconds
For n = 23599      sf(n) = 38. sg(38) = 28. Time:   0.0019 seconds
For n = 4479       sf(n) = 39. sg(39) = 24. Time: Computed in earlier step
For n = 14479      sf(n) = 40. sg(40) = 25. Time: Computed in earlier step
For n = 2355679    sf(n) = 41. sg(41) = 37. Time:   0.0381 seconds
For n = 344479     sf(n) = 42. sg(42) = 31. Time: Computed in earlier step
For n = 1344479    sf(n) = 43. sg(43) = 32. Time: Computed in earlier step
For n = 2378889    sf(n) = 44. sg(44) = 45. Time:   0.0002 seconds
For n = 12378889   sf(n) = 45. sg(45) = 46. Time:   0.0388 seconds
For n = 133378889  sf(n) = 46. sg(46) = 50. Time:   0.0843 seconds
For n = 2356888899 sf(n) = 47. sg(47) = 66. Time:   0.1955 seconds
For n = 12356888899 sf(n) = 48. sg(48) = 67. Time:   0.2126 seconds
For n = 133356888899 sf(n) = 49. sg(49) = 71. Time:   0.3742 seconds
For n = 12245677888899 sf(n) = 50. sg(50) = 84. Time:   1.1286 seconds
For n = 34446666888899 sf(n) = 51. sg(51) = 89. Time:   0.0964 seconds
For n = 134446666888899 sf(n) = 52. sg(52) = 90. Time:   0.8550 seconds
For n = 12245578899999999 sf(n) = 53. sg(53) = 114. Time:   3.9157 seconds
For n = 123345578899999999 sf(n) = 54. sg(54) = 118. Time:   2.0354 seconds
For n = 1344457778899999999 sf(n) = 55. sg(55) = 130. Time:   2.3419 seconds
For n = 12245556666799999999999 sf(n) = 56. sg(56) = 154. Time:  14.2385 seconds
For n = 123345556666799999999999 sf(n) = 57. sg(57) = 158. Time:   3.7793 seconds
For n = 1333579999999999999999999 sf(n) = 58. sg(58) = 193. Time:   5.0514 seconds
For n = 122456679999999999999999999999 sf(n) = 59. sg(59) = 231. Time:  24.6855 seconds
For n = 1233456679999999999999999999999 sf(n) = 60. sg(60) = 235. Time:   4.9824 seconds
For n = 13444667779999999999999999999999 sf(n) = 61. sg(61) = 247. Time:   5.0247 seconds
For n = 12245555588888999999999999999999999999999 sf(n) = 62. sg(62) = 317. Time:  51.2790 seconds
For n = 123345555588888999999999999999999999999999 sf(n) = 63. sg(63) = 321. Time:   5.6676 seconds
For n = 134445555689999999999999999999999999999999999999999999999999999999 sf(n) = 64. sg(64) = 545. Time: 184.5603 seconds
For n = 1223334444555668888889999999999999999999999999999999999999999999999999999999999999999999999999999999999 sf(n) = 65. sg(65) = 843. Time: 380.9418 seconds
For n = 123345556668899999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 sf(n) = 66. sg(66) = 1052. Time: 270.1022 seconds
For n = 13444556666888888899999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 sf(n) = 67. sg(67) = 1339. Time: 488.5466 seconds
For n = 1223334444566666888999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 sf(n) = 68. sg(68) = 1574. Time: 527.3139 seconds
For n = 12334566666688888888999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 sf(n) = 69. sg(69) = 1846. Time: 585.8830 seconds
For n = 13444788889999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 sf(n) = 70. sg(70) = 2035. Time: 427.1509 seconds
    """
