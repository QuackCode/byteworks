"""The ByteWorks factory: floors of tiles, one drone, an inventory and a game clock.

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
        n = self.size()
        self.x = (self.x + dx) % n
        self.y = (self.y + dy) % n
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

    def _harvest_placed(self, tile):
        # Filled in by Task 3 (CPU/SSD/BOARD/GPU rules)
        raise NotImplementedError

    def new_order(self):
        # Filled in by Task 3
        self.order = None

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
            "rng": [version, list(internal), gauss],
        }

    @classmethod
    def from_state(cls, state):
        w = cls.__new__(cls)
        w.seed = state["seed"]
        w.rng = random.Random()
        version, internal, gauss = state["rng"]
        w.rng.setstate((version, tuple(internal), gauss))
        w.clock = state["clock"]
        w.inventory = {p: state["inventory"].get(p, 0) for p in PARTS}
        w.unlocks = set(state["unlocks"])
        w.speed_level = state["speed_level"]
        w.floors = {name: {"size": f["size"], "grid": [[Tile.from_json(t) for t in col] for col in f["grid"]]}
                    for name, f in state["floors"].items()}
        w.floor = state["floor"]
        w.x = state["x"]
        w.y = state["y"]
        w.order = dict(state["order"]) if state["order"] else None
        w.orders_done = state["orders_done"]
        return w
