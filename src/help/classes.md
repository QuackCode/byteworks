# Classes

Everything in Python is an **object**: strings, lists and dicts all have their own **data** and **methods**. A **class** lets you design your own kind of object. Think of the class as a **blueprint**, and each object as something built from it.

Classes are **optional** in ByteWorks: you can finish the game without them. But they're a great way to organise bigger programs.

## `__init__` and `self`

```python
class Robot:
    def __init__(self, name, arms=2):
        self.name = name        # data stored ON the object
        self.arms = arms

bolt = Robot("Bolt")
spark = Robot("Spark", arms=4)
print(bolt.name, bolt.arms, spark.arms)
```

`__init__` runs when an object is created. `self` means "this particular object".

## Methods and `__str__`

```python
class Robot:
    def __init__(self, name):
        self.name = name
        self.jobs = []

    def do(self, job):
        self.jobs.append(job)
        return f"{self.name} did {job}"

    def __str__(self):
        return f"Robot {self.name} ({len(self.jobs)} jobs)"

bolt = Robot("Bolt")
print(bolt.do("welding"))
print(bolt)
```

## Inheritance

A **child** class gets everything from its **parent**, and `super()` calls the parent's version:

```python
class Robot:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hi, I'm {self.name}"

class WeldingRobot(Robot):
    def __init__(self, name, torch_temp):
        super().__init__(name)
        self.torch_temp = torch_temp

w = WeldingRobot("Sparky", 3000)
print(w.greet(), w.torch_temp, isinstance(w, Robot))
```

## Challenge: an `OrderPlanner`

```py
class OrderPlanner:
    def __init__(self):
        self.order = get_order()

    def missing(self):
        short = {}
        for part in self.order:
            gap = self.order[part] - num_items(part)
            if gap > 0:
                short[part] = gap
        return short

planner = OrderPlanner()
print(planner.missing())
```

## Try this

Give `OrderPlanner` a `next_floor()` method that returns the floor with the biggest shortage, and use it to steer your drone.
