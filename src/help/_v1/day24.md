## Statistics: making sense of lots of numbers

With 5 benchmark scores you can eyeball them. With 5,000 you need **statistics**:

- **Mean**: the average (add them up, divide by how many)
- **Median**: the middle value when sorted (not fooled by a few extreme scores)
- **Mode**: the most common value
- **Range**: biggest minus smallest
- **Standard deviation** (std): how **spread out** the values are. Small means consistent, big means all over the place

Python's built-in `statistics` module handles small lists:

```python
import statistics
scores = [7200, 8100, 6900, 9400, 8100]
print(statistics.mean(scores), statistics.median(scores), statistics.mode(scores))
print(round(statistics.stdev(scores), 1))
```

## NumPy: fast maths on whole arrays

**NumPy** is the package behind almost all data science in Python. Its core is the **array**: like a list, but built for maths.

```python
import numpy as np
arr = np.array([7200, 8100, 6900, 9400])
print(arr.mean(), np.median(arr), arr.std(), arr.min(), arr.max())
print(arr.shape, arr.dtype)
```

## Maths on every item at once

With a list you'd need a loop. With an array, maths applies to **every** item:

```python
import numpy as np
arr = np.array([1, 2, 3, 4])
print(arr * 10)
print(arr + arr)
print(arr ** 2)
```

## Comparisons and filtering (boolean masks)

Comparing an array gives an array of `True`/`False`. You can use it to **filter**:

```python
import numpy as np
scores = np.array([7200, 4100, 9400, 3900, 8800])
low = scores < 5000
print(low)                 # [False  True False  True False]
print(low.sum())           # 2: True counts as 1
print(scores[scores > 8000])
```

## Shapes: 2D arrays

`reshape` turns a flat array into rows and columns. `axis=1` means "along each row":

```python
import numpy as np
arr = np.arange(12)            # 0..11
grid = arr.reshape(3, 4)       # 3 rows, 4 columns
print(grid)
print(grid.mean(axis=1))       # mean of each row
print(grid.sum(axis=0))        # sum of each column
```

Other handy tools: `np.zeros(5)`, `np.ones((2, 3))`, `np.linspace(0, 1, 5)`, `np.random.default_rng(1).normal(100, 15, 5)`.

## Your task

You're given `scores`, a plain Python list of GPU benchmark scores.

1. `arr`: `scores` as a NumPy array
2. `mean`, `median` and `spread` (the standard deviation) of the scores
3. `failures`: **how many** scores are below 5000 (as an `int`)
4. `elite`: an array of only the scores of 9000 or more
5. `rating`: every score rescaled from 0 to 1: `(arr - min) / (max - min)`
6. `grid`: the first 12 scores reshaped into 3 rows × 4 columns
7. `row_means`: the mean of each row of `grid`
