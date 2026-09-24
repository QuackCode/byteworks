"""Quests: a help page's "Try this" task, checked automatically from what a program actually did.

Every Python-feature upgrade needs the quest from the help page before it (plus its parts).
Quests are checked live during a run (so a `while True:` farm that's stopped still counts),
except ones that need the program to end by itself, which are checked when it finishes.
"""
import re
from dataclasses import dataclass, field


@dataclass
class RunStats:
    """What one run of the player's program did."""
    harvested: dict = field(default_factory=dict)     # part -> parts gained this run
    floors_harvested: set = field(default_factory=set)
    bonks: int = 0
    big_board: bool = False       # harvested a merged 2x2 (or bigger) motherboard
    gpu_sorted: bool = False      # harvested a sorted GPU floor
    assembled: int = 0
    printed_ram: bool = False     # printed a line showing the current RAM count
    finished: bool = False        # the program ended by itself (not Stop, not an error)
    nodes: set = field(default_factory=set)            # Python syntax used, e.g. "While", "For", "JoinedStr"
    calls: set = field(default_factory=set)            # names of functions the code calls
    user_imports: int = 0                              # imports of the player's own code windows

    def got(self, part):
        return self.harvested.get(part, 0)

    def total(self):
        return sum(self.harvested.values())


@dataclass
class Quest:
    id: str           # also the help page it belongs to
    title: str
    check: object     # check(stats, world) -> bool
    needs_finish: bool = False


QUESTS = [
    Quest("start", "Harvest all 9 RAM sticks in one run",
          lambda s, w: s.got("RAM") >= 9),
    Quest("loops", "Use a loop to sweep the floor twice in one run: 18 RAM with zero bonks",
          lambda s, w: "While" in s.nodes and s.got("RAM") >= 18 and s.bonks == 0),
    Quest("variables", "Write a program that collects 100 more RAM and then stops by itself (use num_items)",
          lambda s, w: s.finished and "num_items" in s.calls and s.got("RAM") >= 100,
          needs_finish=True),
    Quest("floor_cpu", "Farm both floors in one program: harvest 5 RAM and 5 CPUs in a single run",
          lambda s, w: s.got("RAM") >= 5 and s.got("CPU") >= 5),
    Quest("for_loops", "Sweep with for loops: harvest 18 parts in one run with zero bonks",
          lambda s, w: "For" in s.nodes and s.total() >= 18 and s.bonks == 0),
    Quest("positions", "Harvest 9 parts, then use get_pos() to walk home so your program ends at (0, 0) with no bonks",
          lambda s, w: s.finished and "get_pos" in s.calls and s.total() >= 9 and s.bonks == 0
          and (w.x, w.y) == (0, 0), needs_finish=True),
    Quest("floor_ssd", "Harvest 10 SSDs in one run",
          lambda s, w: s.got("SSD") >= 10),
    Quest("lists", "Use a list of floors to harvest on 3 different floors in one run",
          lambda s, w: "List" in s.nodes and len(s.floors_harvested) >= 3),
    Quest("strings", "print() an f-string that shows how much RAM you have",
          lambda s, w: "JoinedStr" in s.nodes and s.printed_ram),
    Quest("floor_board", "Harvest a merged motherboard: a 2×2 square of good boards (or bigger)",
          lambda s, w: s.big_board),
    Quest("sets", "Use a set in your code and harvest on 4 different floors in one run",
          lambda s, w: bool({"Set", "SetComp"} & s.nodes or "set" in s.calls) and len(s.floors_harvested) >= 4),
    Quest("comprehensions", "Choose floors with a list comprehension, then harvest on 2 of them in one run",
          lambda s, w: "ListComp" in s.nodes and len(s.floors_harvested) >= 2),
    Quest("floor_gpu", "Sort a whole GPU floor and harvest it for the big bonus",
          lambda s, w: s.gpu_sorted),
    Quest("modules", "Split your code: import a second code window from main.py and harvest 9 parts",
          lambda s, w: s.user_imports >= 1 and s.total() >= 9),
    Quest("floor_assembly", "Build a computer at Final Assembly",
          lambda s, w: s.assembled >= 1),
]

BY_ID = {q.id: q for q in QUESTS}

# upgrade -> the quest it needs (the help page you read just before it)
QUEST_FOR_UNLOCK = {
    "loops": "start", "variables": "loops", "conditionals": "variables", "for_loops": "floor_cpu",
    "positions": "for_loops", "functions": "positions", "lists": "floor_ssd", "strings": "lists",
    "sets": "floor_board", "dicts": "sets", "comprehensions": "strings", "hof": "comprehensions",
    "modules": "floor_gpu", "exceptions": "modules", "classes": "floor_assembly",
}


def shows_number(text, number):
    """True if `number` appears on its own in `text` (so 42 matches "RAM: 42" but not "421")."""
    return number > 0 and re.search(rf"(?<!\d){number}(?!\d)", text) is not None


def update(world, stats, final=False):
    """Mark newly completed quests on the world and return them."""
    done = []
    for quest in QUESTS:
        if quest.id in world.quests or (quest.needs_finish and not final):
            continue
        if quest.check(stats, world):
            world.quests.add(quest.id)
            done.append(quest)
    return done
