import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "python"))

from game.errors import friendly_error  # noqa: E402


def raise_in(code, filename="main.py"):
    try:
        exec(compile(code, filename, "exec"), {})
    except BaseException as exc:  # noqa: BLE001
        return exc
    raise AssertionError("code did not raise")


class ErrorTests(unittest.TestCase):
    def test_names_line_and_type(self):
        msg = friendly_error(raise_in("x = 1\nprint(y)\n"), {"main.py"})
        self.assertTrue(msg.startswith("Line 2: NameError"))
        self.assertIn("doesn't know that name", msg)

    def test_syntax_error_line(self):
        try:
            compile("print('hi'\n", "main.py", "exec")
        except SyntaxError as exc:
            msg = friendly_error(exc, {"main.py"})
        self.assertTrue(msg.startswith("Line 1: SyntaxError"))

    def test_reports_line_in_other_user_file(self):
        msg = friendly_error(raise_in("1/0", "helpers.py"), {"main.py", "helpers.py"})
        self.assertIn("helpers.py line 1", msg)


from game import balance as B  # noqa: E402
from game.world import World, Tile  # noqa: E402


class WorldCoreTests(unittest.TestCase):
    def test_new_world_has_ready_ram_grid(self):
        w = World(seed=1)
        self.assertEqual(w.floor, "RAM")
        self.assertEqual(w.size(), B.START_SIZE)
        self.assertEqual(w.here().part, "RAM")
        self.assertTrue(w.is_ready(w.here()))

    def test_move_wraps_around(self):
        w = World()
        w.move("West")
        self.assertEqual((w.x, w.y), (B.START_SIZE - 1, 0))
        w.move("South")
        self.assertEqual((w.x, w.y), (B.START_SIZE - 1, B.START_SIZE - 1))

    def test_move_rejects_bad_direction(self):
        with self.assertRaises(ValueError):
            World().move("Up")

    def test_harvest_ram_then_regrow(self):
        w = World()
        self.assertEqual(w.harvest(), 1)
        self.assertEqual(w.inventory["RAM"], 1)
        self.assertEqual(w.harvest(), 0)  # not regrown yet
        w.clock += B.GROW_TICKS["RAM"][1]
        self.assertEqual(w.harvest(), 1)

    def test_state_round_trip_is_exact(self):
        w = World(seed=7)
        w.harvest(); w.move("East"); w.clock += 123
        w.open_floor("CPU")
        copy = World.from_state(w.to_state())
        self.assertEqual(copy.to_state(), w.to_state())
        self.assertEqual(copy.rng.random(), w.rng.random())

    def test_tile_json(self):
        t = Tile("GPU", 50, False, 7, 10)
        self.assertEqual(Tile.from_json(t.to_json()).to_json(), ["GPU", 50, False, 7, 10])


from game.world import FaultyBoardError  # noqa: E402


def world_on(floor, seed=1, **inventory):
    w = World(seed=seed)
    for f in ("CPU", "SSD", "BOARD", "GPU", "ASSEMBLY"):
        w.open_floor(f)
    w.goto_floor(floor)
    w.inventory.update(inventory)
    return w


def fill(w, part, faulty=False, score=None):
    n = w.size()
    for x in range(n):
        for y in range(n):
            w.grid()[x][y] = Tile(part, 0, faulty, score, 0)


class FloorRulesTests(unittest.TestCase):
    def test_place_cpu_bakes_then_harvests(self):
        w = world_on("CPU")
        self.assertTrue(w.place("CPU"))
        self.assertFalse(w.can_harvest())
        w.clock += B.GROW_TICKS["CPU"][1]
        self.assertTrue(w.can_harvest())
        self.assertEqual(w.harvest(), 1)
        self.assertIsNone(w.get_part())

    def test_early_harvest_destroys(self):
        w = world_on("CPU")
        w.place("CPU")
        self.assertEqual(w.harvest(), 0)
        self.assertIsNone(w.get_part())
        self.assertEqual(w.inventory["CPU"], 0)

    def test_place_rules(self):
        w = world_on("SSD")
        self.assertFalse(w.place("CPU"))           # wrong floor
        self.assertFalse(w.place("SSD"))           # can't afford
        w.inventory.update(RAM=3, CPU=1)
        self.assertTrue(w.place("SSD"))
        self.assertEqual((w.inventory["RAM"], w.inventory["CPU"]), (0, 0))
        w.inventory.update(RAM=3, CPU=1)
        self.assertFalse(w.place("SSD"))           # tile occupied
        self.assertEqual(w.inventory["RAM"], 3)    # nothing paid

    def test_faulty_board_raises_and_can_be_replaced(self):
        w = world_on("BOARD", SSD=2)
        w.grid()[0][0] = Tile("BOARD", 0, True, None, 0)
        self.assertTrue(w.is_faulty())
        self.assertTrue(w.can_harvest())
        with self.assertRaises(FaultyBoardError):
            w.harvest()
        self.assertTrue(w.place("BOARD"))
        self.assertEqual(w.inventory["SSD"], 0)

    def test_board_square_merges(self):
        w = world_on("BOARD")
        fill(w, "BOARD")
        self.assertEqual(w.harvest(), 27)          # 3x3 square -> 3**3
        self.assertTrue(all(t.part is None for col in w.grid() for t in col))

    def test_board_with_one_fault_merges_smaller_square(self):
        w = world_on("BOARD")
        fill(w, "BOARD")
        w.grid()[2][2].faulty = True
        self.assertEqual(w.harvest(), 8)           # best square containing (0,0) is 2x2

    def test_gpu_sorted_bonus(self):
        w = world_on("GPU")
        n = w.size()
        for x in range(n):
            for y in range(n):
                w.grid()[x][y] = Tile("GPU", 0, False, x + y, 0)
        self.assertTrue(w.gpu_grid_sorted())
        self.assertEqual(w.harvest(), n * n * n * n)

    def test_gpu_unsorted_and_swap(self):
        w = world_on("GPU")
        fill(w, "GPU", score=5)
        w.grid()[0][0].score = 9
        self.assertFalse(w.gpu_grid_sorted())
        self.assertEqual(w.measure(), 9)
        self.assertFalse(w.swap("West"))           # edge: no wrap
        self.assertTrue(w.swap("East"))
        self.assertEqual(w.measure(), 5)
        self.assertEqual(w.harvest(), 1)

    def test_goto_floor(self):
        w = World()
        self.assertFalse(w.goto_floor("CPU"))      # not open yet
        w.open_floor("CPU")
        self.assertTrue(w.goto_floor("CPU"))
        self.assertEqual(w.floor, "CPU")

    def test_orders_and_assemble(self):
        w = world_on("ASSEMBLY")
        order = dict(w.order)
        self.assertGreaterEqual(len(order), 2)
        self.assertFalse(w.assemble())
        for part, qty in order.items():
            w.inventory[part] = qty
        self.assertTrue(w.assemble())
        self.assertEqual(w.inventory["COMPUTER"], 1)
        self.assertTrue(all(w.inventory[p] == 0 for p in order))
        self.assertNotEqual(w.order, None)

    def test_assemble_needs_assembly_floor(self):
        w = world_on("RAM")
        for part, qty in w.order.items():
            w.inventory[part] = qty
        self.assertFalse(w.assemble())


from game import unlocks as U  # noqa: E402


class UnlockTests(unittest.TestCase):
    def test_every_requirement_exists_and_tree_is_acyclic(self):
        seen = set()
        for u in U.UNLOCKS:  # list order must already be a valid buying order
            for r in u.requires:
                self.assertIn(r, seen, f"{u.id} requires {r}, which must come earlier in UNLOCKS")
            seen.add(u.id)

    def test_buy_pays_and_applies(self):
        w = World()
        w.inventory["RAM"] = 100
        ok, _ = U.buy(w, "loops")
        self.assertTrue(ok)
        self.assertIn("loops", w.unlocks)
        self.assertEqual(w.inventory["RAM"], 100 - U.BY_ID["loops"].cost["RAM"])

    def test_buy_refuses_missing_prereq_money_or_repeat(self):
        w = World()
        self.assertFalse(U.buy(w, "loops")[0])               # can't afford
        w.inventory["RAM"] = 10_000
        self.assertFalse(U.buy(w, "conditionals")[0])        # missing prerequisite
        self.assertTrue(U.buy(w, "loops")[0])
        self.assertFalse(U.buy(w, "loops")[0])               # already bought
        self.assertFalse(U.buy(w, "nope")[0])

    def test_floor_grid_speed_effects(self):
        w = World()
        w.inventory.update(RAM=100_000, CPU=100_000)
        for uid in ["loops", "variables", "conditionals", "floor_cpu", "speed1", "grid_ram_4"]:
            self.assertTrue(U.buy(w, uid)[0], uid)
        self.assertIn("CPU", w.floors)
        self.assertEqual(w.size("RAM"), 4)
        self.assertEqual(w.speed_level, 1)

    def test_tree_json_is_plain_data(self):
        import json
        data = json.loads(json.dumps(U.tree_json()))
        self.assertEqual(len(data), len(U.UNLOCKS))
        self.assertEqual({d["kind"] for d in data} >= {"feature", "floor", "grid", "speed"}, True)


from game.gating import check  # noqa: E402


class GatingTests(unittest.TestCase):
    def test_start_code_is_allowed(self):
        self.assertEqual(check("# hi\nharvest()\nmove(East)\nprint('x')\n", set(), "main.py", set()), [])

    def test_locked_while_is_reported_with_line_and_title(self):
        problems = check("harvest()\nwhile True:\n    harvest()\n", set(), "main.py", set())
        self.assertEqual(len(problems), 1)
        self.assertIn("Line 2", problems[0])
        self.assertIn("Loops", problems[0])

    def test_unlocked_while_passes(self):
        self.assertEqual(check("while True:\n    harvest()\n", {"loops"}, "main.py", set()), [])

    def test_locked_api_function(self):
        problems = check("while True:\n    if can_harvest():\n        harvest()\n", {"loops"}, "main.py", set())
        self.assertTrue(any("Conditionals" in p for p in problems))

    def test_locked_builtin(self):
        problems = check("for i in range(3):\n    harvest()\n", {"loops", "for_loops"}, "main.py", set())
        self.assertEqual(problems, [])
        problems = check("x = len([1])\n", {"variables"}, "main.py", set())
        self.assertTrue(any("Lists" in p for p in problems))

    def test_forbidden_names_and_dunders(self):
        self.assertTrue(check("open('x')\n", set(), "main.py", set()))
        self.assertTrue(check("harvest.__globals__\n", set(), "main.py", set()))

    def test_imports(self):
        all_on = {"modules", "variables"}
        self.assertEqual(check("import math\nimport helpers\n", all_on, "main.py", {"helpers"}), [])
        self.assertTrue(check("import os\n", all_on, "main.py", set()))
        self.assertTrue(check("import helpers\n", {"variables"}, "main.py", {"helpers"}))  # modules locked

    def test_other_file_names_itself(self):
        problems = check("while True:\n    pass\n", set(), "helpers.py", set())
        self.assertIn("helpers.py line 1", problems[0])

    def test_cannot_swallow_stop(self):
        on = {"exceptions", "loops"}
        self.assertTrue(check("try:\n    harvest()\nexcept:\n    pass\n", on, "main.py", set()))
        self.assertTrue(check("try:\n    harvest()\nexcept BaseException:\n    pass\n", on, "main.py", set()))
        self.assertEqual(check("try:\n    harvest()\nexcept Exception:\n    pass\n", on, "main.py", set()), [])

    def test_syntax_error_is_friendly(self):
        problems = check("harvest(\n", set(), "main.py", set())
        self.assertIn("SyntaxError", problems[0])


if __name__ == "__main__":
    unittest.main()
