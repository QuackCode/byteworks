## Classes: blueprints for objects

Everything in Python is an **object**: strings, lists and dicts are all objects with their own **data** and their own **methods** (like `.append()`). A **class** lets you design your own kind of object.

Think of a class as a **blueprint**, and each object (or **instance**) as a thing built from it.

```python
class Robot:
    pass

r1 = Robot()      # build an object from the blueprint
r2 = Robot()
print(type(r1))
```

## `__init__`: setting up a new object

`__init__` runs automatically when an object is created. `self` means **"this particular object"**:

```python
class Robot:
    def __init__(self, name, arms=2):
        self.name = name        # attributes: data stored ON the object
        self.arms = arms

bolt = Robot("Bolt")
spark = Robot("Spark", arms=4)
print(bolt.name, bolt.arms)
print(spark.name, spark.arms)
```

## Methods: what objects can do

A **method** is a function inside a class. Its first parameter is always `self`:

```python
class Robot:
    def __init__(self, name):
        self.name = name
        self.jobs = []

    def do(self, job):
        self.jobs.append(job)
        return f"{self.name} did {job}"

bolt = Robot("Bolt")
print(bolt.do("welding"))
print(bolt.jobs)
```

## `__str__`: how an object prints

```python
class Robot:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"🤖 Robot {self.name}"

print(Robot("Bolt"))
```

Methods with double underscores (`__init__`, `__str__`) are called **dunder** ("double under") methods. Python calls them for you at special moments.

## Inheritance: a blueprint built on another blueprint

A **child** class gets everything from its **parent**, and can add or change things. `super()` calls the parent's version:

```python
class Robot:
    def __init__(self, name):
        self.name = name
    def greet(self):
        return f"Hi, I'm {self.name}"

class WeldingRobot(Robot):           # inherits from Robot
    def __init__(self, name, torch_temp):
        super().__init__(name)       # run Robot's __init__ first
        self.torch_temp = torch_temp

w = WeldingRobot("Sparky", 3000)
print(w.greet())                     # inherited!
print(w.torch_temp)
print(isinstance(w, Robot))          # True: a WeldingRobot IS a Robot
```

## Your task

1. A class `Motherboard` with `__init__(self, serial, socket, ram_slots=4)` that stores all three, plus `self.ram` as an empty list
2. A method `install_ram(self, stick)` that adds `stick` to `self.ram`, **but raises** a `ValueError` if all the slots are already full
3. A `__str__` method that returns `Motherboard <serial> (<socket>)`, e.g. `Motherboard MB-0042 (AM5)`
4. A class `GamingBoard` that **inherits** from `Motherboard`. Its `__init__(self, serial, socket)` uses `super()` to set up **8** RAM slots, and it also sets `self.rgb = True`
