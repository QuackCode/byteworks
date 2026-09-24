from factory.machines import make_board
from factory.pip_sim import Pip

SUCCESS = "📥 Package installed, boards scanned, setup written down. That's how the pros do it!"


def setup(world):
    rng = world.rng
    boards = [make_board(world, fault=rng.choice([None, None, None, "blown", "no_bios"])) for _ in range(rng.randint(5, 9))]
    return {"boards": boards, "pip": Pip()}


def check(ctx):
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        if r.error and "boardcheck" in r.error:
            ctx.expect(False, r.error + "\nInstall it BEFORE you import it: pip.install(\"boardcheck==2.1\")")
        ctx.need(r, "results")
        pip = r.get("pip")
        ctx.expect(pip.installed.get("boardcheck") == "2.1", 'Install version 2.1 exactly: pip.install("boardcheck==2.1").')
        ctx.expect("rgbglow" not in pip.installed and "pip.uninstall(" in ctx.code and 'install("rgbglow' in ctx.code,
                   'Install rgbglow with pip.install("rgbglow"), then remove it with pip.uninstall("rgbglow").')
        boards = r.get("boards")
        want = {b["serial"]: ("PASS" if b["volts"] <= 1.5 and "bios" in b else "FAIL") for b in boards}
        ctx.expect(r.get("results") == want, "results should map every board's serial to boardcheck.scan(board).")
        req = r.files.get("requirements.txt")
        ctx.expect(req is not None, 'Write requirements.txt: with open("requirements.txt", "w") as f: f.write(pip.freeze())')
        ctx.expect(req == "boardcheck==2.1\n", f"requirements.txt should contain exactly boardcheck==2.1 but has {req!r}.")
        if seed == 1:
            for b in boards:
                ctx.show("part", label=b["serial"], result="ship" if want[b["serial"]] == "PASS" else "reject")
