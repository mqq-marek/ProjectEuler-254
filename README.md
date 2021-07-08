# hackerrank-euler
## Day 0

As the first step we build solution based on definition provided.
Let's make initial tests based on source document, 
build initial solution and add simple "print" reporting functionalities.

That is naive approach base on provided functions definition.

Initial analysis will be done next day.

You can notice that we can compute function sg until value 45 
which takes in total 90 seconds on 
Intel(R) Core(TM) i5-4310U CPU @ 2.00GHz   2.60 GHz.

Initial code is in file euler_00_naive.py

## Day 1

Let starts with pre-define factorial values for digits:
```python
FACTORIALS = [math.factorial(i) for i in range(10)]

def f(n):
   return sum([FACTORIALS[int(ch)] for ch in str(n)])
```

Instead of converting integer to text for text digits 
and converting text digits to int indexes let's make 
generator which yields int digits from n.
This generator yields digits in reverse order but 
return result is factorials sum,
so it is not depend on digits order.

```buildoutcfg
FACTORIALS = [math.factorial(i) for i in range(10)]


def digits_gen(n):
    while True:
        yield n % 10
        n //= 10
        if not n:
            break

def f(n):
    return sum([FACTORIALS[d] for d in digits_gen(n)])
    
    
def sf(n): 
    return sum([d for d in digits_gen(f(n))])  
```

Now let's look at function sg. Our final function sum_sg need 
to compute sg & g for values from 1 to n and compute sg sum as a result.
That's mean that it is good to cache g values for next sum_sg call.
Other observation is that for every g(i) computation we start with n = 1 
instead of find a way to resume g computation for next value 
from previous n value.

So let's start the first with update sf function to store in cache 
under integer key i such lowest integer n for which sf(n) == i.

```python
sf_cache = {}


def sf(n):
    sf_ = sum([d for d in digits_gen(f(n))])
    sf_cache.setdefault(sf_, n)
    return sf_
```

And instead of g(i) lets define g_sequence(i) 
which will scan n form 1 until its find g(1), g(2), ..., g(n)

```
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
we will represent numbers on which we will work later.

Let's define class Digits which will represent the numbers.
Class digits will represent number as a list of integers 0-9 
representing digits starting from least significant (reversed order).
We define methods __str__, digits_gen and next.
Method next finds the next number for testing f values based on 
the following observation:
- When we compute f(n) = x we look only for the minimal n giving x 
  as later we look only for minimal n such that sf(n) = s(f(n)) = i
- if we have sequence od digits d[0],...,d[i], d[i+1], ....d[k] then
f(d[0]....d[k]) = f(d[0])...f(d[i]) + f(d[i+1]...d[k]) based on f definition
- If we have minimal n where s(f(n)) = i, then n does not contain 0. 
  We can substitute 10 by 2 because f(10)=f(2) and 2 < 10. We can
  substitute 20 by 12 because f(20)=f(12) and 12 < 20...
- Minimal n giving f(n)=x has digits in not decreasing order. 
  If some digits are decreasing like 32 then f(23)=f(32) and 23 < 32

```buildoutcfg

```

Now speed of the algorithm is around 500 times faster, 
but it allows as to increase computing sum_sg from 45 to only 55 
in around minute.
For g(45), n is 12378889
For g(55), n is 1333666799999999999
For g(56), n is 12245556666799999999999
So you can notice the n size increases very fast, so the methods 
which is based on finding incrementally such n that g(n) = i 
for i > 70 will not work.

In next part we will look more detailed how functions f(n)/sf(n) works 
and how to find other method for compute g(i) for bigger i.


