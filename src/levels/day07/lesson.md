## Sets: no duplicates allowed

A **set** is a collection where **every item is unique** and there's **no order**. It uses curly brackets `{}`:

```python
models = {"DDR4", "DDR5", "DDR4", "DDR4"}
print(models)        # {'DDR4', 'DDR5'}: the duplicates vanished!
print(len(models))   # 2
```

⚠️ An empty set is `set()`. Writing `{}` gives you an empty **dictionary** (tomorrow's topic).

The fastest way to remove duplicates from a list is to turn it into a set:

```python
scans = ["A1", "B2", "A1", "C3", "B2"]
unique = set(scans)
print(unique, len(unique))
```

Sets have no positions, so `unique[0]` won't work. You can check membership with `in`, and it's very fast:

```python
print("A1" in {"A1", "B2"})    # True
```

## Changing a set

```python
stock = {"DDR4"}
stock.add("DDR5")              # add one item
stock.update(["LPDDR5", "DDR3"])  # add several
stock.remove("DDR3")           # remove (error if missing)
stock.discard("DDR9")          # remove (no error if missing)
print(stock)
```

## Set maths 🔀

This is where sets shine. Think of two overlapping circles:

| Operation | Operator | Method | Gives you |
|---|---|---|---|
| Union | `a \| b` | `a.union(b)` | everything in either |
| Intersection | `a & b` | `a.intersection(b)` | only what's in **both** |
| Difference | `a - b` | `a.difference(b)` | in `a` but **not** `b` |
| Symmetric difference | `a ^ b` | `a.symmetric_difference(b)` | in one or the other, not both |

```python
a = {"DDR4", "DDR5", "LPDDR5"}
b = {"DDR5", "DDR3"}
print(a | b)
print(a & b)
print(a - b)
print(a.issubset(b), {"DDR5"}.issubset(a))
```

## Your task

You're given `scanned` (a list of serials with some double-scans), plus `supplier_a` and `supplier_b` (sets of RAM models).

1. `unique`: a set of the different serials
2. `duplicates`: how many scans were duplicates (hint: compare lengths)
3. `in_both`: models **both** suppliers sell
4. `all_models`: every model **either** supplier sells
5. `only_a`: models only supplier A sells
6. `a_sells_ddr5`: `True` if `"DDR5"` is in `supplier_a`
