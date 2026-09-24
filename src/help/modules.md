# Modules

Your programs are getting long. **Modules** let your **code windows** (which are really separate files) use each other's code.

## Code windows

You've been able to make extra windows all along: click **+ New window** above the editor and give it a name, like `helpers`. That makes `helpers.py` (the ✎ button renames the window that's open). Until now each window ran on its own. With Modules, one window can **import** another.

A module is just a file full of code (usually functions) that other files can **import**:

```py
# helpers.py
def tend(part):
    for col in range(3):
        for row in range(3):
            if can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            if row < 2:
                if col % 2 == 0:
                    move(North)
                else:
                    move(South)
        if col < 2:
            move(East)
    move(West)
    move(West)
    move(South)
    move(South)
```

```py
# main.py
import helpers

while True:
    goto_floor(Floor.CPU)
    helpers.tend(Part.CPU)
```

Run `main.py`, and it can use everything defined in `helpers.py`. You can also import just one name: `from helpers import tend`.

## Python's own modules

You can also import two modules from Python's **standard library**:

```python
import math
print(math.sqrt(81), math.pi, math.ceil(4.1), math.floor(4.9))

import random
print(random.randint(1, 6), random.choice(["RAM", "CPU"]))
```

Only `math`, `random` and your own code windows can be imported in ByteWorks.

## 🎯 Quest

**Split your code: import a second code window from main.py and harvest 9 parts.** Doing it lets you buy **Exceptions** (you'll still need its parts).

Make a `helpers` window with a function in it, then `import helpers` in main.py and call the function.
