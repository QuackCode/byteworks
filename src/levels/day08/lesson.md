## Dictionaries: look things up by name

A list finds items by **position** (`belt[0]`). A **dictionary** (`dict`) finds values by a **key**, like a real dictionary looks up a word to get its meaning. Each entry is a `key: value` pair inside `{}`:

```python
stick = {"serial": "RAM-0042", "capacity": 32, "tested": True}
print(stick["serial"])       # RAM-0042
print(stick["capacity"])     # 32
print(len(stick))            # 3 pairs
```

Keys are usually strings. Values can be **anything**, even lists or other dicts.

## Adding and changing

```python
stock = {"DDR4": 10}
stock["DDR5"] = 25          # new key → added
stock["DDR4"] = 12          # existing key → replaced
stock["DDR4"] += 3          # update using the old value
print(stock)
```

## Looking up safely

`stock["DDR9"]` crashes with a `KeyError` if the key doesn't exist. Use `.get()` for a safe lookup with a default:

```python
stock = {"DDR4": 10}
print(stock.get("DDR9", 0))      # 0: no crash
print("DDR4" in stock)           # True: checks the KEYS
```

## Removing

```python
stock = {"DDR3": 4, "DDR4": 10}
old = stock.pop("DDR3")      # removes it AND gives back the value
print(old, stock)
del stock["DDR4"]            # just removes it
print(stock)
```

## Keys, values and items

```python
stock = {"DDR4": 10, "DDR5": 25}
print(list(stock.keys()))      # ['DDR4', 'DDR5']
print(list(stock.values()))    # [10, 25]
print(list(stock.items()))     # [('DDR4', 10), ('DDR5', 25)]: pairs as tuples!
print(sum(stock.values()))     # 35
```

Other handy methods: `.update({...})` merges in another dict, `.copy()` makes a copy, and `.clear()` empties it.

## Your task

You're given `inventory` (a dict of model → stock), `delivery` (how many new DDR5 sticks arrived) and `order` (a dict like `{"model": "DDR4", "qty": 5}`).

1. Add `delivery` to the `"DDR5"` stock
2. Add a new model `"LPDDR5"` with a stock of `20`
3. Remove `"DDR3"` from the inventory and store its old stock in `retired`
4. Take the order's quantity away from the order's model (use `order["model"]` as the key!)
5. `total_sticks`: the total of all the stock
6. `models`: a **list** of the model names
