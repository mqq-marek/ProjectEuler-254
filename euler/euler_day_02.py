"""
Euler challenge from HackerRank https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem

Speed improvement - Day 2

"""
import math
import time
from collections import defaultdict
from functools import reduce
from itertools import combinations

DEBUG = False
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
        return sum([int(ch) for ch in n])
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
            self.num = [int(ch) for ch in number[::-1]]
        else:
            self.num = number.num

    def __str__(self):
        """ Return number value as str """
        return ''.join([str(d) for d in self.num[::-1]])

    @property
    def value(self):
        """ Return number value as int """
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def next(self, start_digit=0):
        def update(d, pos):
            """
            Keep max d digits d from position pos
            :param d: digit to verify occurs no more than d times except 9
            :param pos: starting position
            :return: return next digit, position for next verify
            """
            # to is max position for d times digit d. if d is 9 no limit for digit 9 so position is up to 0
            to = pos - d if d < 9 else -1
            for i in range(pos, to, -1):
                if i < 0:   # return no more updates if process the whole number
                    return None, None
                if self.num[i] < d:  # less digit not allowed, so substitute current digit on next position
                    self.num[i] = d
                if self.num[i] > d:  # higher digit OK, so process for this digit starting from current pos
                    return self.num[i], i
            # now we are after d times digit d
            if to < 0:  # exit if end of number
                return None, None
            if self.num[pos - d] <= d + 1:   # next digit must be minimum one higher than previous
                self.num[pos - d] = d + 1
            return self.num[pos-d], pos-d  # process next number

        def update_prefix():
            """
            Update number to fulfill PREFIX definition 122333444455555...
            """
            start = len(self.num) - 1
            digit, start = update(self.num[start], start)
            while digit:
                digit, start = update(digit, start)
            # print(self.num)

        ndx = start_digit
        while True:
            if self.num[ndx] < 9:
                # Non 9 digit so increase it and set all on right to the same value
                self.num[ndx] += 1
                update_prefix()
                return self
            elif ndx < len(self.num) - 1:
                # if digit 9 then go to next digit
                self.num[ndx] = 0
                ndx += 1
            else:
                # if all digits are 9, then new digit starting with
                self.num[ndx] = 0
                self.num.append(1)
                update_prefix()
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
                diff = f(n) - f(int('0' + '9' * n9))
                print(
                    f"f(n) = {f(n):10}, "
                    f"sf(n) = {i:2}. sg({i:2}) = {digits_sum(n):4}. "
                    f"Time: {stop_time - start_time:8.4f} seconds for len(n) = {len(str(n)):2}, n = {str(n):10} "
                )
        else:
            if DEBUG:
                print(
                    f"f(n) = {f(int(sf_cache[i])):10}, "
                    f"sf(n) = {i:2}. sg({i:2}) = {digits_sum(sf_cache[i]):4}. "
                    f"Time: Already computed For len(n) = {len(str(sf_cache[i])):2}, n = {sf_cache[i]:10} "
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
    # print(sf_cache)
    return sum([sg(i) for i in range(1, n + 1)])


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


if __name__ == "__main__":
    DEBUG = True
    pgm_start = time.perf_counter()
    nn = 70
    total = sum_sg(nn)
    pgm_stop = time.perf_counter()
    print(f"sum_sg({nn}) is {total} computed in {pgm_stop - pgm_start:.2f} seconds")

    """
f(n) =          1, sf(n) =  1. sg( 1) =    1. Time:   0.0000 seconds for len(n) =  1, n = 1          
f(n) =          2, sf(n) =  2. sg( 2) =    2. Time:   0.0000 seconds for len(n) =  1, n = 2          
f(n) =        120, sf(n) =  3. sg( 3) =    5. Time:   0.0000 seconds for len(n) =  1, n = 5          
f(n) =        121, sf(n) =  4. sg( 4) =    6. Time:   0.0001 seconds for len(n) =  2, n = 15         
f(n) =        122, sf(n) =  5. sg( 5) =    7. Time:   0.0001 seconds for len(n) =  2, n = 25         
f(n) =          6, sf(n) =  6. sg( 6) =    3. Time: Already computed For len(n) =  1, n = 3          
f(n) =          7, sf(n) =  7. sg( 7) =    4. Time: Already computed For len(n) =  2, n = 13         
f(n) =          8, sf(n) =  8. sg( 8) =    5. Time: Already computed For len(n) =  2, n = 23         
f(n) =        720, sf(n) =  9. sg( 9) =    6. Time: Already computed For len(n) =  1, n = 6          
f(n) =        721, sf(n) = 10. sg(10) =    7. Time: Already computed For len(n) =  2, n = 16         
f(n) =        722, sf(n) = 11. sg(11) =    8. Time:   0.0000 seconds for len(n) =  2, n = 26         
f(n) =         48, sf(n) = 12. sg(12) =    8. Time:   0.0001 seconds for len(n) =  2, n = 44         
f(n) =         49, sf(n) = 13. sg(13) =    9. Time:   0.0004 seconds for len(n) =  3, n = 144        
f(n) =        842, sf(n) = 14. sg(14) =   13. Time:   0.0005 seconds for len(n) =  3, n = 256        
f(n) =        726, sf(n) = 15. sg(15) =    9. Time: Already computed For len(n) =  2, n = 36         
f(n) =        727, sf(n) = 16. sg(16) =   10. Time: Already computed For len(n) =  3, n = 136        
f(n) =        728, sf(n) = 17. sg(17) =   11. Time: Already computed For len(n) =  3, n = 236        
f(n) =       5760, sf(n) = 18. sg(18) =   13. Time: Already computed For len(n) =  2, n = 67         
f(n) =       5761, sf(n) = 19. sg(19) =   14. Time: Already computed For len(n) =  3, n = 167        
f(n) =       5762, sf(n) = 20. sg(20) =   15. Time:   0.0001 seconds for len(n) =  3, n = 267        
f(n) =     362910, sf(n) = 21. sg(21) =   16. Time:   0.0004 seconds for len(n) =  3, n = 349        
f(n) =     362911, sf(n) = 22. sg(22) =   17. Time:   0.0015 seconds for len(n) =  4, n = 1349       
f(n) =     362912, sf(n) = 23. sg(23) =   18. Time:   0.0011 seconds for len(n) =  4, n = 2349       
f(n) =     362904, sf(n) = 24. sg(24) =   13. Time: Already computed For len(n) =  2, n = 49         
f(n) =     362905, sf(n) = 25. sg(25) =   14. Time: Already computed For len(n) =  3, n = 149        
f(n) =     362906, sf(n) = 26. sg(26) =   15. Time: Already computed For len(n) =  3, n = 249        
f(n) =     362880, sf(n) = 27. sg(27) =    9. Time: Already computed For len(n) =  1, n = 9          
f(n) =     362881, sf(n) = 28. sg(28) =   10. Time: Already computed For len(n) =  2, n = 19         
f(n) =     362882, sf(n) = 29. sg(29) =   11. Time: Already computed For len(n) =  2, n = 29         
f(n) =     362883, sf(n) = 30. sg(30) =   12. Time: Already computed For len(n) =  3, n = 129        
f(n) =     362884, sf(n) = 31. sg(31) =   13. Time: Already computed For len(n) =  3, n = 229        
f(n) =     362885, sf(n) = 32. sg(32) =   14. Time: Already computed For len(n) =  4, n = 1229       
f(n) =     362886, sf(n) = 33. sg(33) =   12. Time: Already computed For len(n) =  2, n = 39         
f(n) =     362887, sf(n) = 34. sg(34) =   13. Time: Already computed For len(n) =  3, n = 139        
f(n) =     362888, sf(n) = 35. sg(35) =   14. Time: Already computed For len(n) =  3, n = 239        
f(n) =     362889, sf(n) = 36. sg(36) =   15. Time: Already computed For len(n) =  4, n = 1239       
f(n) =     362899, sf(n) = 37. sg(37) =   19. Time:   0.0041 seconds for len(n) =  5, n = 13339      
f(n) =     725888, sf(n) = 38. sg(38) =   28. Time:   0.0029 seconds for len(n) =  5, n = 23599      
f(n) =     367968, sf(n) = 39. sg(39) =   24. Time: Already computed For len(n) =  4, n = 4479       
f(n) =     367969, sf(n) = 40. sg(40) =   25. Time: Already computed For len(n) =  5, n = 14479      
f(n) =     368888, sf(n) = 41. sg(41) =   37. Time:   0.0502 seconds for len(n) =  7, n = 2355679    
f(n) =     367998, sf(n) = 42. sg(42) =   31. Time: Already computed For len(n) =  6, n = 344479     
f(n) =     367999, sf(n) = 43. sg(43) =   32. Time: Already computed For len(n) =  7, n = 1344479    
f(n) =     488888, sf(n) = 44. sg(44) =   45. Time:   0.0008 seconds for len(n) =  7, n = 2378889    
f(n) =     488889, sf(n) = 45. sg(45) =   46. Time:   0.0309 seconds for len(n) =  8, n = 12378889   
f(n) =     488899, sf(n) = 46. sg(46) =   50. Time:   0.1250 seconds for len(n) =  9, n = 133378889  
f(n) =     887888, sf(n) = 47. sg(47) =   66. Time:   0.3747 seconds for len(n) = 10, n = 2356888899 
f(n) =     887889, sf(n) = 48. sg(48) =   67. Time:   0.2017 seconds for len(n) = 11, n = 12356888899 
f(n) =     887899, sf(n) = 49. sg(49) =   71. Time:   0.5244 seconds for len(n) = 12, n = 133356888899 
f(n) =     897989, sf(n) = 50. sg(50) =   84. Time:   1.5206 seconds for len(n) = 14, n = 12245677888899 
f(n) =     889998, sf(n) = 51. sg(51) =   89. Time:   1.0332 seconds for len(n) = 14, n = 34446666888899 
f(n) =     889999, sf(n) = 52. sg(52) =   90. Time:   0.8054 seconds for len(n) = 15, n = 134446666888899 
f(n) =    2988989, sf(n) = 53. sg(53) =  114. Time:   3.6738 seconds for len(n) = 17, n = 12245578899999999 
f(n) =    2988999, sf(n) = 54. sg(54) =  118. Time:   3.0574 seconds for len(n) = 18, n = 123345578899999999 
f(n) =    3998899, sf(n) = 55. sg(55) =  134. Time:   4.0642 seconds for len(n) = 19, n = 1333666799999999999 
f(n) =    3999989, sf(n) = 56. sg(56) =  154. Time:  19.5457 seconds for len(n) = 23, n = 12245556666799999999999 
f(n) =    3999999, sf(n) = 57. sg(57) =  158. Time:   6.9994 seconds for len(n) = 24, n = 123345556666799999999999 
f(n) =    6899899, sf(n) = 58. sg(58) =  193. Time:   9.3241 seconds for len(n) = 25, n = 1333579999999999999999999 
f(n) =    7989989, sf(n) = 59. sg(59) =  231. Time:  39.2209 seconds for len(n) = 30, n = 122456679999999999999999999999 
f(n) =    7989999, sf(n) = 60. sg(60) =  235. Time:   9.9241 seconds for len(n) = 31, n = 1233456679999999999999999999999 
f(n) =    7999999, sf(n) = 61. sg(61) =  247. Time:  11.1719 seconds for len(n) = 32, n = 13444667779999999999999999999999 
f(n) =    9999989, sf(n) = 62. sg(62) =  317. Time:  95.8372 seconds for len(n) = 41, n = 12245555588888999999999999999999999999999 
f(n) =    9999999, sf(n) = 63. sg(63) =  321. Time:  13.0214 seconds for len(n) = 42, n = 123345555588888999999999999999999999999999 
f(n) =   19999999, sf(n) = 64. sg(64) =  545. Time: 379.6779 seconds for len(n) = 66, n = 134445555689999999999999999999999999999999999999999999999999999999 
f(n) =   29999999, sf(n) = 65. sg(65) =  843. Time: 847.6465 seconds for len(n) = 103, n = 1223334444555668888889999999999999999999999999999999999999999999999999999999999999999999999999999999999 
f(n) =   39999999, sf(n) = 66. sg(66) = 1052. Time: 615.5185 seconds for len(n) = 123, n = 123345556668899999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 
f(n) =   49999999, sf(n) = 67. sg(67) = 1339. Time: 1191.3816 seconds for len(n) = 155, n = 13444556666888888899999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 
f(n) =   59999999, sf(n) = 68. sg(68) = 1574. Time: 1651.1364 seconds for len(n) = 184, n = 1223334444566666888999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 
f(n) =   69999999, sf(n) = 69. sg(69) = 1846. Time: 2051.2096 seconds for len(n) = 212, n = 12334566666688888888999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 
f(n) =   79999999, sf(n) = 70. sg(70) = 2035. Time: 1096.5472 seconds for len(n) = 230, n = 13444788889999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 
sum_sg(70) is 12632 computed in 8053.64 seconds  
    """
