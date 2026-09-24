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


if __name__ == "__main__":
    unittest.main()
