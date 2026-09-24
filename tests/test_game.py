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


if __name__ == "__main__":
    unittest.main()
