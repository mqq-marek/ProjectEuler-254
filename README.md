# hackerrank-euler
## Day 0

As the first step we build solution based on problem stated on
[HackerRank](https://www.hackerrank.com/contests/projecteuler/challenges/euler254/problem) 
as Project Euler #254: Sums of Digit Factorials

That is naive approach base implemented functions definition as is.
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

Day 0 contains initial code extended with simple reporting and test cases.

By using this approach you can compute function sg until value 45 in around 
90 seconds on 
Intel(R) Core(TM) i5-4310U CPU @ 2.00GHz   2.60 GHz.

Python code is in file euler_00_naive.py. 
Tests are in test_euler_00_naive.py. 

Initial analysis will be done next day.

## Day 1

We start with some basic refactoring.

Let's start with define factorial values for digits:
```python
import math
FACTORIALS = [math.factorial(i) for i in range(10)]
```

Next let's improve number conversion into list of digits with generator.
This generator yields digits in reverse order but digits sum is not depend on the digits order.

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


Now let's look at function sg. Our final function sum_sg need 
to compute sg & g for values from 1 to n and compute sg sum as a result.
That's mean that it is good to cache g values in case of next call.
Other observation is that for every g(i) we start loop with n = 1. 
instead of find a way to resume g computation from previous n value.

So let's start the first with update sf function to store in cache 
under integer key i such the lowest integer n for which sf(n) == i.

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


The last change we made before detailed task analysis is the way how 
we will represent numbers on which we will work.

Let's define class Digits which will represent the numbers.
Class digits will represent number as a list of integers 0-9 
representing digits starting from least significant (reversed order).
We define methods __str__, digits_gen and next.
Method next will find the next number for testing f values. 

We make them slightly better than just take the next integer.
- When we compute f(n) = x we are interested only in the minimal n giving x 
  as later we look only for minimal n such that sf(n) = s(f(n)) = i. 
  So if we have numbers n0, n1, n2, ... having the same f_value 
  we need to find the smallest one and skip all others. 
  Eg 2 = f(2) = f(11) = f(1223) = f(2333). So only 2 necessary.
- If we have sequence od digits d[0],...,d[i], d[i+1], ....d[k] then
f(d[0]....d[k]) = f(d[0])...f(d[i]) + f(d[i+1]...d[k]) based on f definition
- If we have minimal n where s(f(n)) = i, then n does not contain 0. 
  We can substitute 10 by 2 because f(10)=f(2) and 2 < 10. We can
  substitute 20 by 12 because f(20)=f(12) and 12 < 20...
- Minimal n giving f(n)=x has digits in not decreasing order. 
  If some digits are decreasing like 32 then f(23)=f(32) and 23 < 32

Based on this next method when going to next number for computing f(n) 
works in a way that next number after 239999 is 244444 not 24000 
because all numbers between 24000 and 24443 can be reduced to smaller number which gives the same value,
so they were processed earlier if we process number in increasing order.

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

Now speed of the algorithm is around 500 times faster, 
but it allows as to increase computing sum_sg from 45 to only 55 
in around minute.
For g(45), n is 12378889
For g(55), n is 1333666799999999999
For g(60), n is 1233456679999999999999999999999

You can notice the n size increases very fast, so the methods 
which is based on finding incrementally such n that g(n) = i 
for i > 70 will not work.

In next part we will look more detailed how functions f(n)/sf(n) works 
and how to find other method for compute g(i) for bigger i.

Python code is in file euler_day_01.py. 
Tests are in test_euler_day_01.py. 

## Day 2
We will look more detailed on the way how different n gives the same f(n). 

Our goal is to find cheap methods of finding g(i).

At the moment for finding g(i) where i>60 we need scan 
numbers in increasing order which has more than 32 digits 
so this approach will not work for longer i.

As you noticed yesterday interesting numbers has digits ordered 
from smallest to highest.
We also notice yesterday some reduction property: 
if n has two 11 digits it can be 
replaced by 2 which is lower number 
as it's length is shorter by one digit.
So we know that numbers which are result of g(i) have maximum one digit 1.

If we apply the same rules to others digit we can easily find that:
- f(222) = f(3) as 2!+2!+2! = 3!
- f(3333) = f(4)
- ...
- f(888888888) = f(9) as 9 * 8! = 9!

As a result that number candidates for being n such that g(i)=i have
the following pattern:

^1{0,1}2{0,2}3{0,3}4{0,4}5{0,5}6{0,6}7{0,7}8{0,8}9*$

- number need to have minimum one digit 
- digits are in ascending order
- there is max 1 time 1, 2 times 2, ..., 8 times 8 and any number of 9 digits

That allows as build all prospect numbers as two part string 
the first one which is a prefix build from digits 1..8 and 
suffix which is any number of digits 9.
There are maximum 9! prefixes with max length 36 digits.

So now algorithm for method next in class Digits can look sometimes like:
Lets assume we have current number n having length k:
- with prefix length l (0<=l<=k))
- suffix (digits 9) length k-l (0<=k-l<=k)

Next n based on the pattern described above can be build 
in the following way:
- get next prefix with the sam length l if next prefix exist, otherwise
- add digit 9 to suffix and decrease prefix length by 1 
  and place the first prefix with this length 
  if prefix length was not zero, otherwise
- increase number length k by 1 and build new number as the first prefix with length k if k <= 36, otherwise
- if k > 36 add k-36 digits n at the end


```python
PREFIXES = defaultdict(list)
for i1 in range(2):
    for i2 in range(3):
        for i3 in range(4):
            for i4 in range(5):
                for i5 in range(6):
                    for i6 in range(7):
                        for i7 in range(8):
                            for i8 in range(9):
                                i = i1 + i2 + i3 + i4 + i5 + i6 + i7 + i8
                                PREFIXES[i].append(''.join(['1'*i1, '2'*i2, '3'*i3, '4'*i4, 
                                                            '5'*i5, '6'*i6, '7'*i7, '8'*i8]))

class Digits:
    def __init__(self, number):
        self.num = list(digits_gen(number))
        self.suffix_len = sum([1 for d in self.num if d == 9])
        self.prefix_len = len(self.num) - self.suffix_len
        self.prefix_pos = 0
        self.prefix_size = len(PREFIXES[self.prefix_len])  
        
    def next(self):
        self.prefix_pos += 1
        if self.prefix_pos < self.prefix_size:
            prefix = PREFIXES[self.prefix_len][self.prefix_pos][::-1]
            for i in range(self.prefix_len):
                self.num[i + self.suffix_len] = prefix[i]
            return self
        elif self.prefix_len:
            self.num[self.suffix_len] = 9
            self.suffix_len += 1
            self.prefix_len -= 1
            self.prefix_pos = 0
            self.prefix_size = len(PREFIXES[self.prefix_len])
            prefix = PREFIXES[self.prefix_len][self.prefix_pos][::-1]
            for i in range(self.prefix_len):
                self.num[i + self.suffix_len] = prefix[i]
            return self
        else:
            # increase size
            self.num.append(0)
            k = len(self.num)
            self.prefix_len = min(k, 36)
            self.suffix_len = k - self.prefix_len
            self.prefix_pos = 0
            self.prefix_size = len(PREFIXES[self.prefix_len])
            for i in range(self.suffix_len):
                self.num[i] = 9
            prefix = PREFIXES[self.prefix_len][self.prefix_pos][::-1]
            for i in range(self.prefix_len):
                self.num[i + self.suffix_len] = prefix[i]
            return self

```

Now we can compute sg(70) in around 6 minutes.
It gives us speed increase 60 times comparing previous algorithm 
and 30,000 comparing initial on.

Algorithm speed start to be proportional to length of n while 
at the beginning it was expotentional comparing length of n

For sf(70) n has 320 digits - see below:

For n = 13444788889999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 sf(n) = 70. sg(70) = 2035. Time: 427.1509 seconds



Python code is in file euler_day_02.py. 

Tests are in test_euler_day_02.py. 









