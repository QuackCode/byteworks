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


if __name__ == "__main__":
    unittest.main()
