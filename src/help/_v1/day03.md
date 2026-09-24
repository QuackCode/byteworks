## Operators

An **operator** is a symbol that does something to values. You met the arithmetic ones on Day 1. Today you'll use all four families.

### 1. Arithmetic operators

```python
parts = 17
print(parts + 3)    # 20
print(parts - 3)    # 14
print(parts * 2)    # 34
print(parts / 4)    # 4.25  (always gives a float)
print(parts // 4)   # 4     (whole times 4 fits into 17)
print(parts % 4)    # 1     (what's left over)
print(parts ** 2)   # 289   (17 squared)
```

`//` and `%` are a great pair: 17 parts packed in boxes of 4 makes **4 full boxes** (`//`) with **1 left over** (`%`).

### 2. Assignment operators

These are shortcuts for updating a variable:

```python
stock = 10
stock += 5   # same as stock = stock + 5
stock -= 2   # same as stock = stock - 2
stock *= 3   # same as stock = stock * 3
print(stock) # 39
```

### 3. Comparison operators

These compare two values and give back a **bool** (`True` or `False`):

| Operator | Means |
|---|---|
| `==` | equal to (two equals signs!) |
| `!=` | not equal to |
| `>` / `<` | greater / less than |
| `>=` / `<=` | greater-or-equal / less-or-equal |

```python
temperature = 85
print(temperature > 90)     # False
print(temperature == 85)    # True
print(temperature != 85)    # False
```

⚠️ `=` **stores** a value, `==` **compares** two values. Mixing them up is the #1 beginner mistake!

You can store the result in a variable: `too_hot = temperature > 90`

### 4. Logical operators

These combine `True`/`False` values:

- `and`: True only if **both** sides are True
- `or`: True if **at least one** side is True
- `not`: flips True ↔ False

```python
has_power = True
has_parts = False
print(has_power and has_parts)   # False
print(has_power or has_parts)    # True
print(not has_parts)             # True
```

## Your task

You're given `parts_per_hour`, `hours`, `cost_per_part`, `budget` and `is_powered`. Work out:

1. `total_parts`: parts per hour × hours
2. `total_cost`: total parts × cost per part
3. `boxes`: how many **full** boxes of 12 you can pack
4. `leftover`: how many parts are left over after packing
5. `over_budget`: `True` if the total cost is **more than** the budget
6. `can_run`: `True` only if the factory is powered **and not** over budget
