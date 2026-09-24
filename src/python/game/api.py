"""The functions a player's program can call. Each action changes the world, adds game ticks,
tells the screen to redraw, then waits in real time so the player can watch it happen."""
import sys

from . import balance as B
from . import quests
from .world import DIRS, FLOORS, PARTS, FaultyBoardError


MAX_PRINT = 500     # characters per printed line
WAIT_STEP = 100     # ticks per step of wait()


class StopRun(BaseException):
    """Ends a run early (tick budget used up). BaseException, so `except Exception` can't catch it."""


class Part:
    RAM, CPU, SSD, BOARD, GPU, COMPUTER = PARTS


class Floor:
    RAM, CPU, SSD, BOARD, GPU, ASSEMBLY = FLOORS


class Api:
    def __init__(self, world, pace=None, on_change=None, on_print=None, max_ticks=None, stats=None,
                 user_files=("main.py",)):
        self.world = world
        self.user_files = set(user_files)
        self.stats = stats or quests.RunStats()
        self.pace = pace
        self.on_change = on_change
        self.on_print = on_print or (lambda text: None)
        self.limit = None if max_ticks is None else world.clock + max_ticks

    def _spend(self, action, ticks=None, bumped=False):
        ticks = B.ACTION_TICKS[action] if ticks is None else ticks
        self.world.clock += ticks
        if action != "sense":
            self.world.bumped = bumped
        if action != "sense":
            self.world.cursor = self._calling_line()
            self.check_quests()
        ms = ticks * B.MS_PER_TICK / B.SPEEDS[self.world.speed_level]
        if self.on_change and action != "sense":   # sensing changes nothing on screen
            self.on_change(ms)
        if self.pace:                               # ...but still takes real time
            self.pace(ms)
        if self.limit is not None and self.world.clock >= self.limit:
            raise StopRun()

    def _sense(self, value):
        self._spend("sense")
        return value

    @staticmethod
    def _check(value, allowed, what):
        if value not in allowed:
            raise ValueError(f"{what} must be one of: {', '.join(allowed)}")

    def _calling_line(self):
        """[file, line] of the player's code that called this action (for highlighting it)."""
        frame = sys._getframe(2)
        while frame is not None:
            if frame.f_code.co_filename in self.user_files:
                return [frame.f_code.co_filename, frame.f_lineno]
            frame = frame.f_back
        return None

    def check_quests(self, final=False):
        for quest in quests.update(self.world, self.stats, final):
            self.on_print(f"🏆 Quest complete: {quest.title}!")

    # ---- actions
    def harvest(self):
        part, floor = self.world.here().part, self.world.floor
        try:
            gained = self.world.harvest()
            if gained > 0:
                s = self.stats
                s.harvested[part] = s.harvested.get(part, 0) + gained
                s.floors_harvested.add(floor)
                s.big_board |= part == "BOARD" and gained > 1
                s.gpu_sorted |= part == "GPU" and gained > 1
            return gained > 0
        finally:
            self._spend("harvest")

    def move(self, direction):
        if self.world.move(direction):
            self._spend("move")
            return True
        # Walked into a wall: stunned for 1 real second, whatever the Drone Speed
        self.stats.bonks += 1
        self.on_print(f"Bonk! The drone hit the {direction} wall and is stunned for 1 second.")
        stun_ticks = round(B.STUN_MS * B.SPEEDS[self.world.speed_level] / B.MS_PER_TICK)
        self._spend("move", stun_ticks, bumped=True)
        return False

    def print(self, *values, sep=" ", end="\n"):
        text = (sep.join(str(v) for v in values) + end).rstrip("\n")
        if len(text) > MAX_PRINT:
            text = text[:MAX_PRINT] + " …(cut short)"
        self.stats.printed_ram |= quests.shows_number(text, self.world.inventory["RAM"])
        self.on_print(text)
        self._spend("print")

    def wait(self, ticks):
        if not isinstance(ticks, int) or ticks < 0:
            raise ValueError("wait() needs a whole number of ticks, like wait(100)")
        while ticks > 0:             # in small steps, so Stop and tick budgets work mid-wait
            step = min(ticks, WAIT_STEP)
            self._spend("move", step)   # any non-sense action name works: it animates and paces
            ticks -= step

    def place(self, part):
        self._check(part, PARTS[:-1], "place()'s part")
        ok = self.world.place(part)
        self._spend("place")
        return ok

    def swap(self, direction):
        ok = self.world.swap(direction)
        self._spend("swap")
        return ok

    def goto_floor(self, floor):
        self._check(floor, FLOORS, "goto_floor()'s floor")
        ok = self.world.goto_floor(floor)
        self._spend("goto_floor")
        return ok

    def assemble(self):
        ok = self.world.assemble()
        self.stats.assembled += ok
        self._spend("assemble")
        return ok

    # ---- sensing
    def num_items(self, part):
        self._check(part, PARTS, "num_items()'s part")
        return self._sense(self.world.inventory[part])

    def can_harvest(self):
        return self._sense(self.world.can_harvest())

    def get_part(self):
        return self._sense(self.world.get_part())

    def is_faulty(self):
        return self._sense(self.world.is_faulty())

    def measure(self):
        return self._sense(self.world.measure())

    def get_pos(self):
        return self._sense((self.world.x, self.world.y))

    def get_world_size(self):
        return self._sense(self.world.size())

    def get_floor(self):
        return self._sense(self.world.floor)

    def get_order(self):
        return self._sense(dict(self.world.order) if self.world.order else None)

    def namespace(self):
        ns = {name: getattr(self, name) for name in (
            "harvest", "move", "print", "wait", "place", "swap", "goto_floor", "assemble", "num_items",
            "can_harvest", "get_part", "is_faulty", "measure", "get_pos", "get_world_size", "get_floor", "get_order")}
        ns.update({d: d for d in DIRS})
        ns.update(Part=Part, Floor=Floor, FaultyBoardError=FaultyBoardError)
        return ns
