"""Plays the whole game with the reference bots: proves it can be finished, and in a sensible time."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

from game import balance as B  # noqa: E402
from game import unlocks as U  # noqa: E402
from game.quests import QUEST_FOR_UNLOCK  # noqa: E402
from game.runner import run_program  # noqa: E402
from game.world import World  # noqa: E402

BOTS = Path(__file__).parent / "bots"
QUEST_BOTS = Path(__file__).parent / "quests"   # a reference solution for every quest
QUEST_CHUNK = 100_000
CHUNK = 20_000            # ticks per run (a full bot lap must fit, or it never reaches later floors)
MAX_TOTAL = 6_000_000     # safety limit on game ticks
MAX_GAP_MS = 5 * 60_000   # never more than 5 minutes of waiting for the next upgrade (or computer)

STAGES = [
    ("s0_start", ["loops"]),
    ("s1_loop", ["speed1", "variables", "conditionals", "floor_cpu"]),
    ("s2_cpu", ["for_loops", "positions", "functions", "speed2", "grid_ram_4", "floor_ssd"]),
    ("s3_ssd", ["lists", "strings", "speed3", "grid_cpu_4", "floor_board"]),
    ("s4_board", ["sets", "dicts", "comprehensions", "hof", "speed4", "floor_gpu"]),
    ("s5_gpu", ["modules", "exceptions", "speed5", "floor_assembly"]),
    ("s6_assembly", ["classes"]),
]


def bot(name):
    return {"main.py": (BOTS / f"{name}.py").read_text()}


class ProgressionTest(unittest.TestCase):
    """Real waiting time = game ticks x MS_PER_TICK / drone speed (there's no fast-forward button)."""

    def farm_chunk(self, world, name):
        start, speed = world.clock, B.SPEEDS[world.speed_level]
        result = run_program(world, bot(name), max_ticks=CHUNK)
        self.assertTrue(result["ok"], f"{name} failed: {result.get('error')}")
        self.real_ms += (world.clock - start) * B.MS_PER_TICK / speed

    def farm_until(self, world, name, done):
        while not done():
            self.assertLess(world.clock, MAX_TOTAL, f"stuck at {name}: {world.inventory}")
            self.farm_chunk(world, name)

    def do_quest(self, world, quest, stage):
        """Run the quest's reference solution until the game marks the quest done."""
        files = {"main.py": (QUEST_BOTS / f"{quest}.py").read_text()}
        helpers = QUEST_BOTS / f"{quest}_helpers.py"
        if helpers.exists():
            files["helpers.py"] = helpers.read_text()
        for attempt in range(30):
            if quest in world.quests:
                return
            # Test scaffolding: each attempt starts in the RAM floor's corner, because the early
            # quest bots can't use get_pos() yet (players would walk the drone back themselves).
            world.goto_floor("RAM")
            world.x = world.y = 0
            start, speed = world.clock, B.SPEEDS[world.speed_level]
            result = run_program(world, files, max_ticks=QUEST_CHUNK)
            self.assertTrue(result["ok"], f"quest bot {quest} failed: {result.get('error')}")
            self.real_ms += (world.clock - start) * B.MS_PER_TICK / speed
            if quest not in world.quests:      # probably short of parts: farm for a while, then retry
                for _ in range(3):
                    self.farm_chunk(world, stage)
        self.assertIn(quest, world.quests, f"the {quest} quest bot never completed its quest")

    def reached(self, what):
        gap = self.real_ms - self.last_goal_ms
        self.gaps.append((gap, what))
        self.last_goal_ms = self.real_ms

    def test_game_can_be_finished_with_short_waits(self):
        self.real_ms, self.last_goal_ms, self.gaps = 0.0, 0.0, []
        world = World(seed=3)
        for name, buys in STAGES:
            for uid in buys:
                if uid in QUEST_FOR_UNLOCK:
                    self.do_quest(world, QUEST_FOR_UNLOCK[uid], name)
                cost = U.BY_ID[uid].cost
                self.farm_until(world, name, lambda: all(world.inventory[p] >= n for p, n in cost.items()))
                ok, message = U.buy(world, uid)
                self.assertTrue(ok, f"{name}: {message}")
                self.reached(uid)
        for n in range(1, B.WIN_COMPUTERS + 1):
            self.farm_until(world, "s6_assembly", lambda: world.inventory["COMPUTER"] >= n)
            self.reached(f"computer {n}")
        worst, what = max(self.gaps)
        print(f"\nReference bots finished in {self.real_ms / 60_000:.0f} min of drone time; "
              f"longest wait {worst / 60_000:.1f} min (for {what})", file=sys.stderr)
        slow = [f"{w} ({g / 60_000:.1f} min)" for g, w in self.gaps if g > MAX_GAP_MS]
        self.assertEqual(slow, [], "these took more than 5 minutes of waiting")


if __name__ == "__main__":
    unittest.main()
