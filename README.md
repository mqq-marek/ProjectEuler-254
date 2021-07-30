# hackerrank-euler:  Sums of Digit Factorials - problem #254

## Day 0


At the first step we build solution based on problem definition from
[HackerRank](https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem) 
as Project Euler #254: Sums of Digit Factorials

That naive approach is based on functions definition.
```python
import math

def digits_sum(n):
    return sum([int(ch) for ch in str(n)])  

def f(n):
    return sum([math.factorial(int(ch)) for ch in str(n)])

def sf(n):
    return digits_sum(f(n))

def g(i):
    n = 1
    while sf(n) != i:
        n += 1
    return n

def sg(i):
    return digits_sum(g(i))

def sum_sg(n):
    return sum([sg(i) for i in range(1, n + 1)])
```

Day 0 contains only initial code extended with simple reporting and test cases.

By using this approach you can compute function sg until value 45 in around 
90 seconds on 
Intel(R) Core(TM) i5-4310U CPU @ 2.00GHz   2.60 GHz.

Python code is in file euler_00_naive.py. 
Tests are in test_euler_00_naive.py.


## Day 1

We start with some basic refactoring at the begining.

Let's define factorials values for digits 1-9:
```python
import math
FACTORIALS = [math.factorial(i) for i in range(10)]
```

Next we improve number conversion into list of digits using generator.
This generator yields digits in reverse order 
but digits sum is not depend on the digits order

```python
def digits_gen(n):
    while True:
        yield n % 10
        n //= 10
        if not n:
            break

def digits_sum(n):
    return sum([d for d in digits_gen(n)])   

def f(n):
    return sum([FACTORIALS[d] for d in digits_gen(n)])
    
def sf(n): 
    return digits_sum(f(n)) 
```


Now let's look at function sg and sum_sg. 
Our final function sum_sg need 
to compute sg & g for values from 1 to n 
and compute sg sum as a result.

That's mean that having g values cached in case of next call will help

Other observation is that for every g(i) we start loop with n = 1. 
instead of find a way to resume g computation from previous n value.

So let's start the first with update sf function to store in cache 
under integer key i such the lowest integer n for which sf(n) == i.
In other way key, value pair means that g(key) = value.

```python
sf_cache = {}

def sf(n):
    sf_ = digits_sum(f(n))
    sf_cache.setdefault(sf_, str(n))
    return sf_
```

And instead of g(i) lets define g_sequence(i) 
which will scan n form 1 until its find g(1), g(2), ..., g(n)

```python
def g_sequence(max_i):
    n = 1
    for i in range(1, max_i + 1):
        if not sf_cache.get(i):
            start_time = time.perf_counter()
            while sf(n) != i:
                n += 1
            stop_time = time.perf_counter()
            if DEBUG:
                print(
                    f"For n = {n:10} sf(n) = {i:2}. sg({i:2}) = {sum([d for d in digits_gen(n)]):2}. "
                    f"Time: {stop_time-start_time:8.4f} seconds"
                )
        else:
            if DEBUG:
                print(
                    f"For n = {sf_cache[i]:10} sf(n) = {i:2}. "
                    f"sg({i:2}) = {sum([d for d in digits_gen(sf_cache[i])]):2}. "
                    f"Time: Computed in earlier step"
                )
    return sf_cache
```

There are many operations here on number digits instead of number value.
This leads us to change the way how numbers can be represented.

Let's define class Digits which will represent the numbers.
Internally we will represent number as a list of digits (integers 0-9). 
List will keep digits in reverse order starting from least significant.

We define methods __str__ and value for converting number to string 
and int.
Method next will find the next number for testing f values. 

Now is a time for first analysis. We will try to find better way to 
guess proper n such that n = g(i) than simply increase n.
- If we have numbers n0, n1, n2, ... having the same f_value 
  we need to find the smallest one and skip all others. 
  E.g., 2 = f(2) = f(11) = f(1223) = f(2333). So, we need only 2.
- If two numbers have the same f value 
  the number with fewer digits is better
- Minimal n giving f(n)=i has digits in not decreasing order. 
  If some digits are decreasing order like 32 then f(23)=f(32) and 23 < 32  
- If we have sequence of digits d[0],...,d[i], d[i+1], ....d[k] then
f(d[0]....d[k]) = f(d[0])+...+f(d[i]) + f(d[i+1]...d[k]) based on f definition
- If we have minimal n where s(f(n)) = i, then n does not contain 0. 
  We can always substitute 10 by 2 because f(10)=f(2) and 2 < 10. We can
  substitute 20 by 12 because f(20)=f(12) and 12 < 20 and so on ...


Based on this analysis we build the improved next method. 
Instead of increasing n by 1 and testing sf(n) against i, 
we will take next n which fulfill conditions which we find above.
The numbers selected by the next method will have 
its digits in increasing order. E.g. 
after 239999 next is 244444 not 24000.

```python
class Digits:
    def __init__(self, number):
        self.num = list(digits_gen(number))

    def __str__(self):
        return ''.join([chr(d+ord('0')) for d in self.num[::-1]])

    @property
    def value(self):
        return reduce(lambda x, y: x * 10 + y, self.num[::-1])

    def next(self, start_digit=0):
        def set_after_carry_on(k):
            """ Set digits after carry on 1.
            Instead of  0 fill with updated digit
            Eg. 2999 + 1 is 3333 not 3000
            """
            filler = self.num[k]
            for ii in range(k-1, start_digit - 1, -1):
                self.num[ii] = filler

        ndx = start_digit
        while True:
            if self.num[ndx] < 9:
                # Non 9 digit so increase it and set all on right to the same value
                self.num[ndx] += 1
                set_after_carry_on(ndx)
                return self
            elif ndx < len(self.num) - 1:
                # if digit 9 then go to next digit
                self.num[ndx] = 0
                ndx += 1
            else:
                # if all digits are 9, then new digit starting with
                self.num.append(1)
                set_after_carry_on(ndx+1)
                return self

```

Now speed of the algorithm is around 600 times faster, 
but it allows as to increase computing sum_sg from 45 to 55 
in time of one minute.

For g(45), n is 12378889

For g(55), n is 1333666799999999999

For g(60), n is 1233456679999999999999999999999



You can notice now that, the n size increases very fast.
That is a reason why finding incrementally such n that sf(n) = i
for i > 70 will not work.

Python code is in file euler_day_01.py. 
Tests are in test_euler_day_01.py. 

## Day 2


We will look more detailed on the way how different n gives the same f(n).

Yesterday we noticed that, the prospect number n has digits ordered 
from smallest to highest. 

We fonded also some reduction property - n does not have digit 0 
and n has only one digit 1 (11 digits can be 
replaced by 2 which makes smaller number because number is horter by one digit).


If we apply the same redustion rules to others digit we can easily 
find that:
- f(222) = f(3) as 2!+2!+2! = 3!
- f(3333) = f(4)
- ...
- f(888888888) = f(9) as 9 * 8! = 9!

As a result that number n candidates such that g(i)=n have
the following pattern:

^1{0,1}2{0,2}3{0,3}4{0,4}5{0,5}6{0,6}7{0,7}8{0,8}9*$

- digits are in ascending order
- there is max 1 time 1, 2 times 2, ..., 8 times 8 and any number of 9 digits

Based on thi we can look at n as number composed of two parts: 
prefix and suffix. 
- Prefix contains digits from 1 to 8 and has length in range 0 to 36
  digits. The longest prefix 12233344445555566666677777778888888 has
  f value equals 9!-1
- Suffix 0 or more digits 9. Unlimited length.


We modify method next in a way that after every increment 
we will have number which forms valid prefix and suffix 
composed of 0 or more digits 9.


Update function below enforces rule that digit d will occur 
maximum d times except 9.

```python
class Digits:
    def __init__(self, number):
        if isinstance(number, int):
            self.num = list(digits_gen(number))
        elif isinstance(number, str):
            self.num = [ord(ch) - ord('0') for ch in number[::-1]]
        else:
            self.num = number.num

    def __str__(self):
        """ Return number value as str """
        return ''.join([chr(d+ord('0')) for d in self.num[::-1]])

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

```
New algorithm is only 4 times faster than day before.
We need huge increase.

Let's try harder next day.

Python code is in file euler_day_02.py. 

Tests are in test_euler_day_02.py. 

## Day 3

In previous days we worked on faster method for finding n such that g(i) is n. 

Now we are ready to notice why id does not help us find solution.


g(i) is defined as smallest number n such sf(n) 
(sum of digits f(n)) is equal n.

For given i f value having digits sum equals  i is number 
composed of digits 9 and up to one digit at the beginning which sum up to i.
For example for i = 50 f(n) is 499999, for i = 100, 
f(n) is 199999999999.

Simply we have number with digit i % 9 at the beginning 
and i // 9 digits n.
So f(n) has ceil(i//9) digits. 

Having f(n) we can find n. 
We know that having n f(n) is build as a sum of number n digits factorial.
Part with prefix is responsible for value from 0 to 9!-1 
and every digit 9 is responsible for value 9! in f(n). 
Simply for f(n) n has f(n)/9! digits 9 and prefix in length between 0 and 36 
such that digits factorial sum gives us f(n) % 9!. 


For given i f(n) has i//9 digits. The 10\*\*6 < 9! < 10\*\*7. When we divide 
f(n) / 9! we will have result which has maximum 7 digits less. 
So that means that for given i n has 10\*\*(i//9 - 7) digits 
and number having such number of digits has value 
10 \*\* (10 \*\* (i//9-7)).

For example for i = 100, n has value around 10\*\*10000 and has 10,000 digits plus prefix.
For i = 300, n will have 8267195767195767195767195767 
digits 9 plus prefix: 12233344445557777778 
which is 10\*\*28 9 digits comparing to 10\*\*26 digits from our approximation.

That is clear that method which is based on searching n incrementally
will not work for i > 80.

We need to find cheaper method for finding g(i). 

So instead of generate successive n, lets 
try for given i generate successive f_values 
with sum of digits equals i.

Next we need to built reverse f function which from f_value gives us n.
We know that n  contains 
some digits from:
- PREFIX: 122333444455555666666777777788888888 and
- SUFFIX: any number of digits 9.
- If n is concatenations of digits in PREFIX and SUFFIX then 
f(n) = f(PREFIX) + f(SUFFIX).
- For given f_value we can find n in 
the following way: 
  - SUFFIX length is f_value // 9! digits n. 
  - PREFIX is a number which sum  of digits factorial equals 
 f_value x % 9!
  - PREFIX can be can find with pre-build dictionary which 
    for given f(PREFIX) gives us PREFIX. You can verify that 
    we have 9!-1 prefixes and for any number k from range 1..9!-1 
    exist exactly one prefix 
    (in form: ^1{0,1}2{0,2}3{0,3}4{0,4}5{0,5}6{0,6}7{0,7}8{0,8}9*$)
    such that f(prefix) = k.


Now our new approach for finding g(i) for given i looks like:
- Let's get the lowest number f_value having sum of digits = i
- Using reverse f function find n such that f(n) = f_value, and sf(n) = i

Unfortunately we need scan more than one f_value with sum i 
as we need find smallest n such that sf(n)=i - starting from the smallest 
f_value does not guarantee us smallest n.

For example for i =21:
- the smallest number 
which have sum 21 is 399 = f(12334555)=399. 
- next number with sum 21 is 489 = f(1235555).
- ...
- next number having sum 21 is 768 = f(446), 
- ...  
-  362910 = f(349). 

The last one gives us n which is g(21) = 349. 
All numbers with sum of digits equal 21 gives us greater n than 349.

We need to limit in some way this scan. 

The easiest way is to take the length of the first prefix here 
is 8=length(12334555), which gives us limit for f value as 8*9!.

Based on the way how number n looks like  
we know that for f_value > k*9! we will have k digits with non-empty prefix or 
more than k digits 9.

Let's start and define all prefixes in dictionary which allows us 
map f(prefix) to prefix. 

```python
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
```

For fining f values with given sum  we define FDigits class with 
the following approach:
- class constructor need to have parameter - number of digits
- class works as iterator so class object will generate  
  sequence of numbers with given sum of digits in increasing order 
- sequence for 1: 1, 10, 100, 1000, ...
- sequence for 20: 299, 389, 398, 479, 488, ...
- property num keeps internal number representation as sequence of digits
- property value gives integer number representation
- internally method next_number gives next number with given sum of digits

```python
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

```

For computing number n from f(n) we need to define reverse_f function.
We know that n is composed of prefix and suffix which 
contains only digits 9, 
so we define N_Number tuple as prefix and suffix_len and 
function smaller_n, which takes 
two N_Number's and returns smaller one.

```python
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

```


Our new g_sequence function for given i creates iterator returning numbers 
with digits sum, keeps the best_n until stop conditions occurs.

```python
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

```

Result of running our new algorithm is:
```python
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
```

As you can see initial steps until i = 62 are very costly and slow.
Starting from i=63 finding n such that g(i) = n takes only one step.

Reason behind this is that later on distance between two numbers 
having the same amount of digits sum start to be bigger and bigger.
For i=64 distance between to consecutive numbers with the same amount of digits is 
When distance between numbers starts to be bigger than 10\*\*7.
When one f-value is greater than 10\*\*37 from another 
one then difference between n is around 30 digits, 
so we get stop condition after one step.




sum_sg(20000) is computed in 144.58 seconds


To verify is this is correct please register on [Project Euler](https://projecteuler.net) web page.
Go to problem 254 and enter value for sum of sg for 150.
But on HackerRank problem is more difficult you - you must build solution 
which is fast enough to pass the tests.

On next day we will try join the best part of Day 2 and Day 3 solutions.


### Numbers representation
Two most frequent number representation are base on radix 10 and 2.
When you have number 1,000,000,000 times bigger than 
its representation in decimal format is plus 9 digits longer, binary representation
is plus 30 digits longer.
Representation defined in our problem composed of prefix suffix will be
2750 times longer than before multiply.

Multiple two n digits numbers in decimal/binary representation 
gives the result with  maximum 2\*n digits.
For prefix/suffix representation the result will have 
n\*n digits in the result.

Prefix suffix representation is like representation with radix equals 1.
Every digit 9 is responsible for value 9!. So representation length is 
 proportional to number value while in positional representation 
number length is proportional math.log(number, radix).

## Day 4


The first time we receive algorithm which is slow 
but can compute g(i) for i = 20,000 in lest than 3 minutes.

The last solution is very slow for small i. 
We can also notice that f value pattern is random 
especially at the beginning 
while above i=63 is very regular.


The reason behind is the prefix/suffix interaction. For small i, 
the length of prefix part summed up with length of suffix part
introduce huge noise as lengths of parts are comparable 
while prefix value comparing to its length is very irregular.


Later on impact of 
prefix part is negligible as 
distance between two n's having the same digit sum or greater digits sum 
start to be bigger and bigger. Max prefix length is 36, so as a result 
from i=63 g(i) function behavior is very regular.

For speed up our algorithm we initialize the first 200 values of g(i) 
at the beginning and start to compute g(i) from bigger values.

When we will look at prefixes 
we can notice that only 117 out of 9! prefixes are used 
for composing n such that g(i) = n i>63.

We can build n such that g(i) = n in one step, so 
we remove FDigits class and stay with function which gives 
us f_value and reverse function for getting n.

Function g_sequence is very simple now - no need for scan and find best_n. 
We always get it in one step.


```python
def reverse_f(f_value):
    suffix_len, f_prefix = divmod(f_value, FACTORIALS[9])
    prefix = PREFIX[f_prefix]
    PREFIX_USED[f_prefix] = prefix
    return N_Number(prefix, suffix_len)


def build_f_value_with(digits_sum):
    """ Build suffix which gives g(i) = i """
    n9, d = divmod(digits_sum, 9)
    if d == 0:
        return '9' * n9
    else:
        return chr(d+ord('0')) + '9' * n9


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
        if sg_cache.get(i):
            continue
        f_value = build_f_value_with(i)
        best_n = reverse_f(int(f_value))
        if DEBUG:
            l_str = str(len(str(best_n.prefix)) + best_n.suffix_len)
            if len(l_str) > 19:
                l_str = '...'+l_str[-16:]
            prefix = best_n.prefix + '+'
            print(
                f'len={l_str:21}, f(n) = {f_value:40}, '
                f'g({i}) = {prefix}9*{best_n.suffix_len}')
        sg_cache[i] = digits_sum(best_n.prefix) + 9 * best_n.suffix_len
        g_cache[i] = best_n
    return
```

sum_sg(50000) has length 5552 last digits are 126984132135059 computed in 4.09 seconds
sum_sg(100000) has length 11108 last digits are 269841280147918 computed in 27.90 seconds

We can see now that computing sum up to 50,000 is 4 sec, up to 100,000 is 27 sec.
That means that we have still faster than linear increase in computing time.

Let's verify this using profiler.

```python
def profile_main(size=200):
    with cProfile.Profile() as pr:
        init_prefixes()
        sum_sg(size)

    s = io.StringIO()
    sort_by = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.print_stats()
    print(s.getvalue())
```


Execution time increases because of processed values 
have huge amount of digits and cost of 
such operation growing faster than linear.


## Day 5


Today we try to decrease time of computing sg(i).

Computing sg(i) looks in the following way:
- build the first f_value which has i digits 
  (i: 10-> 19, i: 71->89999999)
- find n as: :
  - suffix which contains (f_value // 9!)  digits '9'
  - prefix which sum of factorial digits is: f_value % 9!
- build sg as sum of digits n: 9 * (f_value // 9!) + digits_sum(prefix)

Number of digits of f_value increased fast. 
For i = 500 F_value has 56 digits, n value has 10\*\*49 digits,
so cost of operations on such numbers start to be very high.

Let's look at the F_values base on increasing order of i:
76: 499999999
77: 599999999, increase: 100000000
78: 699999999, increase: 100000000
79: 799999999, increase: 100000000
80: 899999999, increase: 100000000
81: 999999999, increase: 100000000
82:1999999999, increase:1000000000
83:2999999999, increase:1000000000

So we can compute sg(i+1) as sum of:
- digits_sum(prefix for i+1) - 
  we can eliminate computing f_value % 9! and 
  make 162 elements prefix table as prefixes goes in cycle of i % 162
- 9*numbers of digits 9 in sg(i)
- additional amount of 9 digits based on increase value (increase // 9!) - 
  we have divide operation here, but we can do it once every 9 
  steps as 9 increases 
  are the same next we have next 9 increases 10 times higher
- carry which is 0 or 1. 
  Integer divide by the same offset value gives sometimes 1
  increase as you need to account also remainder from previous step divide..
  Simply when divide remainder in current step is smaller 
  than remainder in previous step we have additional 1 in divide result.. 
  Again it is base 162 elements cycle, 
  when dividing f_value by 9!, so we keep this value in the same table.

``` python
def sum_sg_mod(n, m):
    def verify_elem(val, i):
        """ Verify sg(i) elements build here against values in sg_table. """
        if i <= len(sg_table):
            if val != sg_table[i-1]:
                print(f"bad value for sg({i}. Expected {sg_table[i-1]}, received {val}")

    def get_sg(i, m):
        """ Compute sg(i) based on previous sg(i-1).
            nonlocal variables used for keeping previous sg(i-1) info:
                n9_step - numbers of 9 digits which increment g(i) value. n9step is the same for 9 successive i values
                starting with value where i % 9 == 1 (f_value 19999..)
                n9_sum - digits sum of suffix part = 9 * n9_step + 9 * carry. carry is precomputed and taken from table
                sg_n9_sum - digits sum of suffix from previous g value
        """
        nonlocal n9_step, n9_sum, sg_n9_sum

        """
        sgi_mod_table is 162 element table which keeps cycle information when operate on F_values.
        elements contains tuple with following information
            [0] - i value % 162 + 162
            [1] - f_value % 9! [f_value % 9! has cycle 162]
            [2] - PREFIX for given f_value % 9!
            [3] - sum digits of PREFIX
            [4] - carry = 1 if current f_value % 9! is smaller than previous one. In such situation:
                f_value // 9! - f_value_prev // 9! = (f_value - f_value_prev) // 9! + 1(carry)
            [5] - step increase - additional increase of number of 9 in suffix when go to f_value longer by 1 digit.
                Again lake for carry its cumulative increase of quotient based on (previous_reminder * 10) % 9!. 
                Proper value is 10 elements back comparing current element (i - 10) % 162
        """
        i_ = i % len(sgi_mod_table)
        sf_prefix = sgi_mod_table[i_][3]
        carry = sgi_mod_table[i_][4]

        ''' When f_value starts with 1 it means that we have 1 digit longer f_value. '''
        if i % 9 == 1:
            step_increase = sgi_mod_table[(i-10) % len(sgi_mod_table)][5]
            # print(f'n9_step inc = {inc}, rem: {n9_rem}')
            n9_step = (10 * n9_step + step_increase)
            n9_sum = n9_step * 9

        sg_n9_sum += n9_sum + 9 * carry
        sg_ = sg_n9_sum + sf_prefix

        verify_elem(sg_, i)
        return sg_

    ''' 
    Split sg_table at position cache_limit.
        The first part used for setting up initial values of sg(i). Minimum 70 is required.
        The second part is used for verifying result of new get_sg against data in sg_table.
    '''
    cache_limit = min(204, len(sg_table))
    s = 0
    s = sum(sg_table[:min(cache_limit, n)]) % m

    ''' Initialize n9_step, n9_sum, sg_n9_sum for i = cache_limit. '''
    f_value = f_value_with_digit_sum(cache_limit)
    nn = reverse_f(int(f_value))
    f_value_step = int(f_value[1:]) + 1
    n9_step = f_value_step // F9
    n9_sum = n9_step * 9
    sg_n9_sum = nn.suffix_len * 9

    ''' Start compute from i = cache_limit + 1. '''
    for i in range(cache_limit + 1, n + 1):
        s = (s + get_sg(i, m)) % m
    return s
```

Now algorithm is fast but later on when numbers starts 
to have huge amount of digits is slow.

- sum_sg(500) has length 12 last digits are 412698459839 computed in 0.00 seconds
- sum_sg(5000) has length 12 last digits are 269841780640 computed in 0.02 seconds
- sum_sg(50000) has length 12 last digits are 984132135059 computed in 0.81 seconds
- sum_sg(500000) has length 12 last digits are 412749963545 computed in 43.34 seconds

Expected result need to have value mod m, 
then  we introduce modulo arithmetic which prevent 
us to use to have huge numbers in our computations.

```python
def sum_sg_mod(n, m):
    def verify_elem(val, i):
        """ Verify sg(i) elements build here against values in sg_table. """
        if i <= len(sg_table):
            if val % m != sg_table[i-1] % m:
                print(f"bad value for sg({i}. Expected {sg_table[i-1]}, received {val}")

    def get_sg(i, m):
        """ Compute sg(i) based on previous sg(i-1).
            nonlocal variables used for keeping previous sg(i-1) info:
                n9_step - numbers of 9 digits which increment g(i) value. n9step is the same for 9 successive i values
                starting with value where i % 9 == 1 (f_value 19999..)
                n9_sum - digits sum of suffix part = 9 * n9_step + 9 * carry. carry is precomputed and taken from table
                sg_n9_sum - digits sum of suffix from previous g value
        """
        nonlocal n9_step, n9_sum, sg_n9_sum

        """
        sgi_mod_table is 162 element table which keeps cycle information when operate on F_values.
        elements contains tuple with following information
            [0] - i value % 162 + 162
            [1] - f_value % 9! [f_value % 9! has cycle 162]
            [2] - PREFIX for given f_value % 9!
            [3] - sum digits of PREFIX
            [4] - carry = 1 if current f_value % 9! is smaller than previous one. In such situation:
                f_value // 9! - f_value_prev // 9! = (f_value - f_value_prev) // 9! + 1(carry)
            [5] - step increase - additional increase of number of 9 in suffix when go to f_value longer by 1 digit.
                Again lake for carry its cumulative increase of quotient based on (previous_reminder * 10) % 9!. 
                Proper value is 10 elements back comparing current element (i - 10) % 162
        """
        i_ = i % len(sgi_mod_table)
        sf_prefix = sgi_mod_table[i_][3]
        carry = sgi_mod_table[i_][4]

        ''' When f_value starts with 1 it means that we have 1 digit longer f_value. '''
        if i % 9 == 1:
            step_increase = sgi_mod_table[(i-10) % len(sgi_mod_table)][5]
            # print(f'n9_step inc = {inc}, rem: {n9_rem}')
            n9_step = (10 * n9_step + step_increase) % m
            n9_sum = n9_step * 9 % m

        sg_n9_sum = (sg_n9_sum + n9_sum + 9 * carry ) % m
        sg_ = (sg_n9_sum + sf_prefix) % m

        verify_elem(sg_, i)
        return sg_

    ''' 
    Split sg_table at position cache_limit.
        The first part used for setting up initial values of sg(i). Minimum 70 is required.
        The second part is used for verifying result of new get_sg against data in sg_table.
    '''
    cache_limit = min(204, len(sg_table))
    s = 0
    s = sum(sg_table[:min(cache_limit, n)]) % m

    ''' Initialize n9_step, n9_sum, sg_n9_sum for i = cache_limit. '''
    f_value = f_value_with_digit_sum(cache_limit)
    nn = reverse_f(int(f_value))
    f_value_step = int(f_value[1:]) + 1
    n9_step = f_value_step // F9 % m
    n9_sum = n9_step * 9 % m
    sg_n9_sum = nn.suffix_len * 9 % m

    ''' Start compute from i = cache_limit + 1. '''
    for i in range(cache_limit + 1, n + 1):
        s = (s + get_sg(i, m)) % m
    return s
```

After introduce mod m arithmetic:
- sum_sg(500000) has length 12 last digits are 412749963545 computed in 1.30 seconds
- sum_sg(5000000) has length 12 last digits are 270356820724 computed in 6.22 seconds
- sum_sg(50000000) has length 12 last digits are 989282535332 computed in 68.57 seconds

Now time is linear - proportional to i.
It's great increase in speed comparing initial 10 \*\* 10 \*\* i.


## Day 6


Base on description we will have the data size in range:

1 <= i <= 10\*\*18


Empty loop in Python which has 10\*\*9 repetition takes around 50 
seconds, so 10\*\*18 repetition loop takes more than 10,000 days.

Until now, we work on finding the fastest way for guessing g(i).
That does not work, so we need to work on finding directly of sum_sg 
without need to compute earlier every g(i) in the given range 
and sum them.

To solve this we need to use mathematical approach.

Based idea is to find the sum of the sum_sg_range(i, j) in one step.

sg(i) is sum digits of lowest n such that g(i) = n. 
N is composed of prefix (build from digits form 
1 to 8 - max length 36 digits) and suffix - huge amount of digits 9.
For prefix, we already noticed that the appears in some order with 
cycle having 162 elements. 

More difficult is to find how amount of digits 9 increases in some range.

The easiest way which very frequently works is to find formula 
for next sum based on previous one,

The approach which works here after detailed analysis of the data:
- Take some starting point and frame  
- for i in range(start, start + frame) sum all digits 9 for g(i) in 
  this range
- next repeat the same for few next steps 
  range(start+frame, start+2*frame) and so on
- try to find something which allows you 
  to describe sum of next frame as combination of previous frame sum.
  That is possible that you need to work with different frame sizes and 
  different start points.
- You need to find some rules which will define sum_sg(i+1) as 
  some combinations of earlier step. Something similar to 
  recurrent definition of factorial or Fibonacci.
- Next step is pure mathematical thing - you need to transform 
  equation to non-recurrent form which define some kind of 
  geometric sequence 
- In next step you need to find equation which describe 
  sum of such sequences - which is equivalent to sum_sg(i, j).
- When you find this, then you will be able to compute   
 sum_sg(i, j) with one expression without any loop.
  
  

sum_sg(10000000000000000000000000000)  12 last digits are 238095233749 computed in 0.00 seconds


Finals submission as marek38 - rank 12

Success rate for this problem is 0.23% until now.






























