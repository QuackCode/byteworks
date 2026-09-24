# Comprehensions & lambda

## List comprehensions: loops in one line

```python
numbers = [1, 2, 3, 4, 5]
doubled = [n * 2 for n in numbers]
print(doubled)
```

Read it as: **"`n * 2`, for each `n` in `numbers`"**.

## Filtering with `if`

```python
numbers = [1, 2, 3, 4, 5, 6]
print([n for n in numbers if n % 2 == 0])
print([i * i for i in range(10) if i > 5])
```

The pattern is `[what_to_keep  for item in collection  if condition]`.

## Flattening a list of lists

```python
shelves = [["A1", "A2"], ["B1", "B2", "B3"]]
print([slot for row in shelves for slot in row])
```

## Dict and set comprehensions

```python
squares = {n: n * n for n in range(1, 5)}
print(squares)
print({word[0] for word in ["ram", "rom", "cpu"]})
```

## Lambda: tiny one-line functions

`lambda inputs: result` is a small, nameless function:

```python
double = lambda x: x * 2
add = lambda a, b: a + b
print(double(21), add(3, 4))
```

## Picking floors with a comprehension

```py
floors = [Floor.RAM, Floor.CPU, Floor.SSD, Floor.BOARD]
low = [f for f in floors if num_items(f) < 20]
print("Running low on:", low)
```

## 🎯 Quest

**Choose floors with a list comprehension, then harvest on 2 of them in one run.** Doing it lets you buy **Higher-order Functions** (you'll still need its parts).

Something like `floors = [f for f in all_floors if num_items(f) < 500]`, then visit those floors.
