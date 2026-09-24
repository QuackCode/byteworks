"""The ByteWorks factory: floors of tiles, one drone, an inventory and a game clock.

Floors have walls: moving off an edge is blocked (the Api stuns the drone for it).

Time only moves when the drone acts (the Api adds ticks), so everything is deterministic.
Grids are indexed grid[x][y]; y = 0 is the South edge and North is +y.
"""
import random

from . import balance as B

FLOORS = ["RAM", "CPU", "SSD", "BOARD", "GPU", "ASSEMBLY"]
PARTS = ["RAM", "CPU", "SSD", "BOARD", "GPU", "COMPUTER"]
DIRS = {"North": (0, 1), "East": (1, 0), "South": (0, -1), "West": (-1, 0)}


class FaultyBoardError(Exception):
    """Raised when the drone harvests a faulty motherboard."""


class Tile:
    __slots__ = ("part", "ready_at", "faulty", "score", "planted_at")

    def __init__(self, part=None, ready_at=0, faulty=False, score=None, planted_at=0):
        self.part = part
        self.ready_at = ready_at
        self.faulty = faulty
        self.score = score
        self.planted_at = planted_at

    def to_json(self):
        return [self.part, self.ready_at, self.faulty, self.score, self.planted_at]

    @classmethod
    def from_json(cls, data):
        return cls(*data)


class World:
    def __init__(self, seed=1):
        self.seed = seed
        self.rng = random.Random(seed)
        self.clock = 0
        self.inventory = {p: 0 for p in PARTS}
        self.unlocks = set()
        self.speed_level = 0
        self.floors = {}
        self.floor = "RAM"
        self.x = 0
        self.y = 0
        self.order = None
        self.orders_done = 0
        self.bumped = False   # True right after the drone walked into a wall (drawn as 💫)
        self.open_floor("RAM")

    # ---------------------------------------------------------------- floors
    def open_floor(self, name):
        if name in self.floors:
            return
        size = 1 if name == "ASSEMBLY" else B.START_SIZE
        self.floors[name] = {"size": size, "grid": [[self._fresh_tile(name) for _ in range(size)] for _ in range(size)]}
        if name == "ASSEMBLY" and self.order is None:
            self.new_order()

    def _fresh_tile(self, floor):
        return Tile("RAM", 0) if floor == "RAM" else Tile()

    def resize(self, name, size):
        old = self.floors[name]
        grid = [[old["grid"][x][y] if x < old["size"] and y < old["size"] else self._fresh_tile(name)
                 for y in range(size)] for x in range(size)]
        self.floors[name] = {"size": size, "grid": grid}
        if self.floor == name:
            self.x %= size
            self.y %= size

    def size(self, name=None):
        return self.floors[name or self.floor]["size"]

    def grid(self, name=None):
        return self.floors[name or self.floor]["grid"]

    def here(self):
        return self.grid()[self.x][self.y]

    def is_ready(self, tile):
        return tile.part is not None and self.clock >= tile.ready_at

    def grow_time(self, part):
        low, high = B.GROW_TICKS[part]
        return self.rng.randint(low, high)

    # ---------------------------------------------------------------- actions
    def move(self, direction):
        if direction not in DIRS:
            raise ValueError("move() needs a direction: North, East, South or West")
        dx, dy = DIRS[direction]
        nx, ny = self.x + dx, self.y + dy
        n = self.size()
        if not (0 <= nx < n and 0 <= ny < n):
            return False          # a wall: the drone stays where it is
        self.x, self.y = nx, ny
        return True

    def harvest(self):
        """Collect the part under the drone. Returns how many parts were gained."""
        tile = self.here()
        if tile.part is None:
            return 0
        if tile.part == "RAM":
            if not self.is_ready(tile):
                return 0
            gained = B.YIELD["RAM"]
            tile.planted_at = self.clock
            tile.ready_at = self.clock + self.grow_time("RAM")
            self.inventory["RAM"] += gained
            return gained
        return self._harvest_placed(tile)

    # ---------------------------------------------------------------- sensing
    def get_part(self):
        return self.here().part

    def can_harvest(self):
        return self.is_ready(self.here())

    def is_faulty(self):
        tile = self.here()
        return tile.part == "BOARD" and self.is_ready(tile) and tile.faulty

    def measure(self):
        tile = self.here()
        return tile.score if tile.part == "GPU" else None

    # ---------------------------------------------------------------- building
    def place(self, part):
        if part not in B.PLACE_COST or part != self.floor:
            return False
        tile = self.here()
        replacing_fault = tile.part == "BOARD" and self.is_ready(tile) and tile.faulty
        if tile.part is not None and not replacing_fault:
            return False
        cost = B.PLACE_COST[part]
        if any(self.inventory[p] < n for p, n in cost.items()):
            return False
        for p, n in cost.items():
            self.inventory[p] -= n
        faulty = part == "BOARD" and self.rng.random() < B.FAULT_CHANCE
        score = self.rng.randint(0, 9) if part == "GPU" else None
        self.grid()[self.x][self.y] = Tile(part, self.clock + self.grow_time(part), faulty, score, self.clock)
        return True

    def _harvest_placed(self, tile):
        if not self.is_ready(tile):
            self.grid()[self.x][self.y] = Tile()      # harvested too early: destroyed
            return 0
        part = tile.part
        if part == "BOARD":
            if tile.faulty:
                raise FaultyBoardError(f"The motherboard at {(self.x, self.y)} is faulty!")
            gained = self._harvest_board_square()
        elif part == "GPU" and self.gpu_grid_sorted():
            n = self.size()
            gained = n * n * n * n
            self.floors[self.floor]["grid"] = [[Tile() for _ in range(n)] for _ in range(n)]
        else:
            gained = B.YIELD[part]
            self.grid()[self.x][self.y] = Tile()
        self.inventory[part] += gained
        return gained

    def _good_board(self, x, y):
        tile = self.grid()[x][y]
        return tile.part == "BOARD" and self.is_ready(tile) and not tile.faulty

    def _harvest_board_square(self):
        n = self.size()
        for k in range(n, 1, -1):
            for sx in range(max(0, self.x - k + 1), min(self.x, n - k) + 1):
                for sy in range(max(0, self.y - k + 1), min(self.y, n - k) + 1):
                    cells = [(sx + i, sy + j) for i in range(k) for j in range(k)]
                    if all(self._good_board(cx, cy) for cx, cy in cells):
                        for cx, cy in cells:
                            self.grid()[cx][cy] = Tile()
                        return k ** 3
        self.grid()[self.x][self.y] = Tile()
        return B.YIELD["BOARD"]

    def swap(self, direction):
        if direction not in DIRS:
            raise ValueError("swap() needs a direction: North, East, South or West")
        dx, dy = DIRS[direction]
        nx, ny = self.x + dx, self.y + dy
        n = self.size()
        if not (0 <= nx < n and 0 <= ny < n):
            return False
        g = self.grid()
        g[self.x][self.y], g[nx][ny] = g[nx][ny], g[self.x][self.y]
        return True

    def gpu_grid_sorted(self):
        g, n = self.grid(), self.size()
        if not all(g[x][y].part == "GPU" and self.is_ready(g[x][y]) for x in range(n) for y in range(n)):
            return False
        rows = all(g[x][y].score <= g[x + 1][y].score for y in range(n) for x in range(n - 1))
        cols = all(g[x][y].score <= g[x][y + 1].score for x in range(n) for y in range(n - 1))
        return rows and cols

    # ---------------------------------------------------------------- lift + orders
    def goto_floor(self, name):
        if name not in self.floors:
            return False
        self.floor = name
        self.x %= self.size()
        self.y %= self.size()
        return True

    def new_order(self):
        kinds = min(5, 2 + self.orders_done // 3)
        parts = self.rng.sample(list(B.ORDER_BASE), kinds)
        scale = 1 + self.orders_done // 4
        self.order = {p: B.ORDER_BASE[p] * self.rng.randint(1, 2) * scale for p in parts}

    def assemble(self):
        if self.floor != "ASSEMBLY" or not self.order:
            return False
        if any(self.inventory[p] < n for p, n in self.order.items()):
            return False
        for p, n in self.order.items():
            self.inventory[p] -= n
        self.inventory["COMPUTER"] += 1
        self.orders_done += 1
        self.new_order()
        return True

    # ---------------------------------------------------------------- saving
    def to_state(self):
        version, internal, gauss = self.rng.getstate()
        return {
            "seed": self.seed,
            "clock": self.clock,
            "inventory": dict(self.inventory),
            "unlocks": sorted(self.unlocks),
            "speed_level": self.speed_level,
            "floors": {name: {"size": f["size"], "grid": [[t.to_json() for t in col] for col in f["grid"]]}
                       for name, f in self.floors.items()},
            "floor": self.floor,
            "x": self.x,
            "y": self.y,
            "order": dict(self.order) if self.order else None,
            "orders_done": self.orders_done,
            "bumped": self.bumped,
            "rng": [version, list(internal), gauss],
        }

    @classmethod
    def load(cls, state):
        """(world, ok). A save that can't be read gives a fresh world and ok=False instead of crashing."""
        from .unlocks import BY_ID
        try:
            world = cls.from_state(state)
        except (KeyError, TypeError, ValueError, IndexError, AttributeError):
            return cls(seed=1), False
        world.unlocks = {u for u in world.unlocks if u in BY_ID}   # upgrades removed in newer versions
        return world, True

    @classmethod
    def from_state(cls, state):
        w = cls.__new__(cls)
        w.seed = state.get("seed", 1)
        w.rng = random.Random(w.seed)
        if state.get("rng"):
            version, internal, gauss = state["rng"]
            w.rng.setstate((version, tuple(internal), gauss))
        w.clock = int(state.get("clock", 0))
        w.inventory = {p: int(state["inventory"].get(p, 0)) for p in PARTS}
        w.unlocks = set(state.get("unlocks", []))
        w.speed_level = min(int(state.get("speed_level", 0)), len(B.SPEEDS) - 1)
        w.floors = {name: {"size": f["size"], "grid": [[Tile.from_json(t) for t in col] for col in f["grid"]]}
                    for name, f in state["floors"].items() if name in FLOORS}
        w.floor = state.get("floor", "RAM")
        if "RAM" not in w.floors or w.floor not in w.floors:
            raise ValueError("save has no usable floors")
        for f in w.floors.values():
            if len(f["grid"]) != f["size"] or any(len(col) != f["size"] for col in f["grid"]):
                raise ValueError("save has a broken grid")
        w.x = int(state.get("x", 0)) % w.size()
        w.y = int(state.get("y", 0)) % w.size()
        w.order = dict(state["order"]) if state.get("order") else None
        w.orders_done = int(state.get("orders_done", 0))
        w.bumped = bool(state.get("bumped", False))
        if "ASSEMBLY" in w.floors and w.order is None:
            w.new_order()
        return w
