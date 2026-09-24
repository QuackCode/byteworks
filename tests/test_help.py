import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

from game import unlocks as U  # noqa: E402
from game.gating import check  # noqa: E402
from game.sandbox import run_snippet  # noqa: E402
from game.runner import run_program  # noqa: E402
from game.world import World  # noqa: E402

HELP = ROOT / "src" / "help"
FENCE = "`" * 3
BLOCK = re.compile(FENCE + r"(python|py)\n(.*?)" + FENCE, re.S)


def owned_at(page):
    if page == "start":
        return set()
    wanted, todo = set(), [page]
    while todo:
        uid = todo.pop()
        if uid not in wanted:
            wanted.add(uid)
            todo.extend(U.BY_ID[uid].requires)
    return wanted


class HelpPageTests(unittest.TestCase):
    def test_every_help_id_has_a_page(self):
        ids = {u.help for u in U.UNLOCKS if u.help} | {"start"}
        missing = [i for i in sorted(ids) if not (HELP / f"{i}.md").exists()]
        self.assertEqual(missing, [])

    def test_examples(self):
        for path in sorted(HELP.glob("*.md")):
            text = path.read_text()
            self.assertTrue(text.startswith("# "), f"{path.name} must start with '# Title'")
            unlocked = owned_at(path.stem)
            for kind, code in BLOCK.findall(text):
                if kind == "python":
                    result = run_snippet(code)
                    self.assertIsNone(result["error"], f"{path.name} example failed:\n{code}\n{result['error']}")
                else:
                    problems = check(code, unlocked, "main.py", {"helpers"})  # examples may import a window called helpers
                    self.assertEqual(problems, [], f"{path.name} drone example uses locked things:\n{code}")

    def test_drone_examples_never_bonk_a_wall(self):
        for path in sorted(HELP.glob("*.md")):
            for kind, code in BLOCK.findall(path.read_text()):
                if kind != "py" or "import helpers" in code:
                    continue
                world = World(seed=1)
                world.inventory.update({p: 10**6 for p in world.inventory})
                for u in U.UNLOCKS:              # list order is a valid buying order
                    if u.id in owned_at(path.stem):
                        U.buy(world, u.id)
                bonks = []
                run_program(world, {"main.py": code}, max_ticks=20_000,
                            on_print=lambda text: text.startswith("Bonk") and bonks.append(text))
                self.assertEqual(bonks, [], f"{path.name} example walks into a wall:\n{code}")


if __name__ == "__main__":
    unittest.main()
