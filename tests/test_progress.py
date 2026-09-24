"""Plays the whole game with the reference bots: proves it can be finished, and in a sensible time."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

from game import balance as B  # noqa: E402
from game import unlocks as U  # noqa: E402
from game.runner import run_program  # noqa: E402
from game.world import World  # noqa: E402

BOTS = Path(__file__).parent / "bots"
CHUNK = 20_000            # ticks per run before the test checks progress again
MAX_TOTAL = 6_000_000     # ~3.3 hours of drone time at speed x1

STAGES = [
    ("s0_start", ["loops"]),
    ("s1_loop", ["speed1", "variables", "conditionals", "floor_cpu"]),
    ("s2_cpu", ["for_loops", "positions", "functions", "speed2", "grid_ram_4", "floor_ssd"]),
    ("s3_ssd", ["lists", "strings", "speed3", "grid_cpu_4", "floor_board"]),
    ("s4_board", ["sets", "dicts", "comprehensions", "hof", "speed4", "floor_gpu"]),
    ("s5_gpu", ["modules", "exceptions", "speed5", "floor_assembly"]),
    ("s6_assembly", ["classes", "turbo"]),
]


def bot(name):
    return {"main.py": (BOTS / f"{name}.py").read_text()}


class ProgressionTest(unittest.TestCase):
    def farm_until(self, world, name, done):
        while not done():
            self.assertLess(world.clock, MAX_TOTAL, f"too slow / stuck at {name}: {world.inventory}")
            result = run_program(world, bot(name), max_ticks=CHUNK)
            self.assertTrue(result["ok"], f"{name} failed: {result.get('error')}")

    def test_game_can_be_finished(self):
        world = World(seed=3)
        for name, buys in STAGES:
            for uid in buys:
                cost = U.BY_ID[uid].cost
                self.farm_until(world, name, lambda: all(world.inventory[p] >= n for p, n in cost.items()))
                ok, message = U.buy(world, uid)
                self.assertTrue(ok, f"{name}: {message}")
        self.farm_until(world, "s6_assembly", lambda: world.inventory["COMPUTER"] >= B.WIN_COMPUTERS)
        hours = world.clock * B.MS_PER_TICK / 3_600_000
        print(f"\nReference bots finished in {world.clock:,} ticks (~{hours:.1f} h at x1)", file=sys.stderr)


if __name__ == "__main__":
    unittest.main()
