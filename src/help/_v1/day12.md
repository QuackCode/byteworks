## Modules: code in other files

A **module** is simply a `.py` file full of code (functions, variables) that other code can **import** and use. Here's the whole `cpu_tools` module the factory made from your Day 9 rules:

```python
# cpu_tools.py
GAMING_GHZ = 4.0

def grade(cpu):
    if cpu["temp_c"] > 90:
        return "REJECT"
    if cpu["clock_ghz"] >= GAMING_GHZ:
        return "GAMING"
    if cpu["clock_ghz"] >= 2.5:
        return "OFFICE"
    return "REJECT"
```

On your own computer you'd save that as `cpu_tools.py` and, in another file in the same folder, write `import cpu_tools`. Here it lives inside the `factory` package, so the import is `factory.cpu_tools`.

## Ways to import

```python
import math                     # the whole module: use math.something
print(math.sqrt(81), math.pi)

from math import ceil, floor    # just some names: use them directly
print(ceil(4.1), floor(4.9))

import statistics as stats      # a shorter nickname (alias)
print(stats.mean([2, 4, 9]))

from factory.cpu_tools import grade
print(grade({"clock_ghz": 4.4, "temp_c": 60}))
```

## The standard library: batteries included 🔋

Python ships with hundreds of modules. Some favourites:

| Module | Useful for | Examples |
|---|---|---|
| `math` | maths | `math.ceil`, `math.floor`, `math.sqrt`, `math.pi` |
| `random` | randomness | `random.randint(1, 6)`, `random.choice(list)`, `random.shuffle(list)` |
| `statistics` | averages | `mean`, `median`, `mode`, `stdev` |
| `string` | letter lists | `string.ascii_letters`, `string.digits` |
| `os` | files & folders | `os.getcwd()`, `os.listdir()` |
| `sys` | Python itself | `sys.version` |
| `datetime` | dates & times | (Day 16!) |

```python
import random
print(random.randint(1, 6))
print(random.choice(["DDR4", "DDR5"]))
nums = [1, 2, 3, 4]
random.shuffle(nums)
print(nums)
```

## Your task

You're given `batch`, a list of CPU dicts.

1. Import `math`, `random`, `statistics` **as** `stats`, and `grade` from `factory.cpu_tools`
2. `boxes`: how many boxes of 12 you need to hold the whole batch. Round **up**: 13 chips need 2 boxes (`math.ceil`)
3. `audit`: one **random** chip from the batch for a surprise inspection
4. `avg_clock`: the mean `clock_ghz` of the batch (build a list of clocks first, then use `stats.mean`)
5. `grades`: a list of `grade(cpu)` for every chip in the batch, in order
