"""The upgrade tree. List order is a valid buying order (every requirement comes earlier)."""
from dataclasses import dataclass

from . import balance as B
from .quests import BY_ID as QUESTS, QUEST_FOR_UNLOCK


@dataclass
class Unlock:
    id: str
    title: str
    cost: dict
    requires: tuple = ()
    floor: str | None = None
    grid: tuple | None = None
    speed: int | None = None
    windows: int = 0
    summary: str = ""
    help: str | None = None

    @property
    def kind(self):
        if self.floor:
            return "floor"
        if self.grid:
            return "grid"
        if self.speed:
            return "speed"
        return "feature" if self.help and not self.help.startswith("floor_") else "other"


def F(id, title, cost, requires=(), summary=""):
    """A Python-feature unlock with its own help page."""
    return Unlock(id, title, cost, tuple(requires), summary=summary, help=id)


def FLOOR(id, floor, title, cost, requires, summary):
    return Unlock(id, title, cost, tuple(requires), floor=floor, summary=summary, help=id)


def SPEED(level, cost, requires):
    return Unlock(f"speed{level}", f"Drone Speed {level}", cost, tuple(requires), speed=level,
                  summary=f"The drone works x{B.SPEEDS[level]} as fast in real time.")


UNLOCKS = [
    F("loops", "Loops", {"RAM": 5}, summary="while loops (and wait()) so the drone can keep working forever."),
    SPEED(1, {"RAM": 15}, ["loops"]),
    F("variables", "Variables & Operators", {"RAM": 20}, ["loops"],
      "Store values, do maths and compare things. Also num_items()."),
    F("conditionals", "Conditionals", {"RAM": 40}, ["variables"],
      "if / elif / else, plus can_harvest() and get_part()."),
    FLOOR("floor_cpu", "CPU", "CPU Floor", {"RAM": 60}, ["conditionals"],
          "Open the CPU floor. place() chips and let them bake. Ride the lift with goto_floor()."),
    F("for_loops", "For Loops & range", {"RAM": 50, "CPU": 5}, ["floor_cpu"], "for loops, range(), break and continue."),
    F("positions", "Positions & Tuples", {"RAM": 60, "CPU": 10}, ["for_loops"],
      "get_pos() gives an (x, y) tuple. get_world_size() gives the grid size."),
    F("functions", "Functions", {"CPU": 25}, ["for_loops"], "def your own reusable routines."),
    SPEED(2, {"RAM": 100, "CPU": 20}, ["speed1", "floor_cpu"]),
    FLOOR("floor_ssd", "SSD", "SSD Floor", {"RAM": 150, "CPU": 50}, ["functions"],
          "SSDs cost RAM and CPUs to place, but pay out double."),
    F("lists", "Lists", {"SSD": 10}, ["floor_ssd"], "Lists, indexing, append/pop, len()."),
    F("strings", "Strings & f-strings", {"SSD": 10}, ["floor_ssd"], "String methods, slicing and f-strings."),
    SPEED(3, {"SSD": 40}, ["speed2", "floor_ssd"]),
    FLOOR("floor_board", "BOARD", "Motherboard Floor", {"SSD": 80}, ["lists"],
          "Motherboards merge into big boards... but some come out faulty. is_faulty()!"),
    F("sets", "Sets", {"BOARD": 20}, ["floor_board"], "Collections with no duplicates."),
    F("dicts", "Dictionaries", {"BOARD": 30}, ["floor_board"], "Look things up by key."),
    F("comprehensions", "Comprehensions & lambda", {"BOARD": 60}, ["lists"], "Build lists in one line."),
    F("hof", "Higher-order Functions", {"BOARD": 80}, ["comprehensions", "functions"], "map, filter, sorted with key=."),
    SPEED(4, {"BOARD": 60}, ["speed3", "floor_board"]),
    FLOOR("floor_gpu", "GPU", "GPU Floor", {"BOARD": 150}, ["dicts"],
          "GPU chips have scores. Sort the whole grid for a huge bonus: measure() and swap()."),
    Unlock("modules", "Modules", {"GPU": 40}, ("floor_gpu",), help="modules",
           summary="Your code windows can import each other, plus import math / random."),
    F("exceptions", "Exceptions", {"GPU": 60}, ["floor_gpu"], "try / except / finally and raise."),
    SPEED(5, {"GPU": 200}, ["speed4", "floor_gpu"]),
    FLOOR("floor_assembly", "ASSEMBLY", "Final Assembly", {"GPU": 200}, ["exceptions"],
          "Fill customer orders to build complete computers."),
    F("classes", "Classes", {"COMPUTER": 1}, ["floor_assembly"], "Design your own objects."),
]

GRID_BASE = {"RAM": 20, "CPU": 10, "SSD": 10, "BOARD": 8, "GPU": 20}
FLOOR_UNLOCK = {"RAM": "loops", "CPU": "floor_cpu", "SSD": "floor_ssd", "BOARD": "floor_board", "GPU": "floor_gpu"}

for _floor, _base in GRID_BASE.items():
    for _size in range(B.START_SIZE + 1, B.MAX_SIZE + 1):
        _prev = FLOOR_UNLOCK[_floor] if _size == B.START_SIZE + 1 else f"grid_{_floor.lower()}_{_size - 1}"
        UNLOCKS.append(Unlock(f"grid_{_floor.lower()}_{_size}", f"{_floor.title()} Grid {_size}x{_size}",
                              {_floor: _base * 2 ** (_size - B.START_SIZE - 1)}, (_prev,), grid=(_floor, _size),
                              summary=f"Make the {_floor} floor {_size}x{_size}."))

BY_ID = {u.id: u for u in UNLOCKS}


def buy(world, unlock_id):
    u = BY_ID.get(unlock_id)
    if u is None:
        return False, f"There's no upgrade called {unlock_id!r}."
    if u.id in world.unlocks:
        return False, f"You already own {u.title}."
    missing = [BY_ID[r].title for r in u.requires if r not in world.unlocks]
    if missing:
        return False, f"{u.title} needs {', '.join(missing)} first."
    quest = QUEST_FOR_UNLOCK.get(u.id)
    if quest and quest not in world.quests:
        return False, f"{u.title} needs a quest first: {QUESTS[quest].title}. (See 📖 Help.)"
    short = {p: n - world.inventory.get(p, 0) for p, n in u.cost.items() if world.inventory.get(p, 0) < n}
    if short:
        return False, "Not enough parts: need " + ", ".join(f"{n} more {p}" for p, n in short.items()) + "."
    for p, n in u.cost.items():
        world.inventory[p] -= n
    world.unlocks.add(u.id)
    if u.floor:
        world.open_floor(u.floor)
    if u.grid:
        world.resize(*u.grid)
    if u.speed:
        world.speed_level = max(world.speed_level, u.speed)
    return True, f"Unlocked {u.title}!"


def windows_allowed(world):
    return 1 + sum(BY_ID[u].windows for u in world.unlocks if u in BY_ID)


def tree_json():
    return [{"id": u.id, "title": u.title, "cost": u.cost, "requires": list(u.requires),
             "summary": u.summary, "help": u.help, "kind": u.kind, "windows": u.windows,
             "quest": _quest_json(u.id)} for u in UNLOCKS]


def _quest_json(unlock_id):
    quest = QUEST_FOR_UNLOCK.get(unlock_id)
    return {"id": quest, "title": QUESTS[quest].title, "page": quest} if quest else None
