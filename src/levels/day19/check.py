import json

SUCCESS = "🗄️ Every file read, every log written. Head office loves the paperwork!"


def setup(world):
    rng = world.rng
    orders = [f"ORDER-{rng.randint(100, 999)} {rng.choice(['Gaming PC', 'Office PC', 'Workstation', 'Mini PC'])}" for _ in range(rng.randint(3, 7))]
    with open("orders.txt", "w") as f:
        f.write("\n".join(orders) + "\n")
    with open("specs.json", "w") as f:
        json.dump({"socket": rng.choice(["AM5", "LGA1851", "AM4"]), "ram_slots": rng.choice([2, 4]), "wifi": rng.random() < 0.5}, f)
    rows = [(world.serial("MB"), rng.choice(["PASS", "PASS", "FAIL"])) for _ in range(rng.randint(4, 8))]
    with open("boards.csv", "w") as f:
        f.write("serial,status\n" + "".join(f"{s},{st}\n" for s, st in rows))
    return {}


def check(ctx):
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        ctx.need(r, "orders", "socket", "rows", "passed", "log_exists")
        files = r.files
        orders = files["orders.txt"].splitlines()
        ctx.expect(r.get("orders") == orders, "orders should be a list of the lines in orders.txt. Try f.read().splitlines().")
        ctx.expect(r.get("socket") == json.loads(files["specs.json"])["socket"], 'socket should be the "socket" value from specs.json (json.load).')
        rows = [dict(zip(("serial", "status"), line.split(","))) for line in files["boards.csv"].splitlines()[1:]]
        ctx.expect(r.get("rows") == rows, "rows should be a list of dicts from boards.csv. Try list(csv.DictReader(f)).")
        ctx.expect(r.get("passed") == [x["serial"] for x in rows if x["status"] == "PASS"], 'passed should be the serials whose status is "PASS".')
        log = files.get("production.log")
        ctx.expect(log is not None, "I can't find production.log. Did you write it with open(\"production.log\", \"w\")?")
        want = "".join(f"BUILT {o}\n" for o in orders) + "SHIFT END\n"
        ctx.expect(log.startswith("".join(f"BUILT {o}\n" for o in orders)),
                   "production.log should start with one line BUILT <order> per order (remember the \\n).")
        ctx.expect(log == want, "production.log should end with a SHIFT END line, added in append (\"a\") mode.")
        ctx.expect("\"a\"" in ctx.code or "'a'" in ctx.code, "Add SHIFT END by opening the file again in append mode: open(\"production.log\", \"a\").")
        ctx.expect(r.get("log_exists") is True, 'log_exists should come from os.path.exists("production.log").')
        if seed == 1:
            for o in orders:
                ctx.show("part", label=o[:10], result="ship")
