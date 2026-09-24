from factory.machines import make_ssd

SUCCESS = "⚡ Filtered in a flash! Dead drives out, good drives shelved."


def setup(world):
    rng = world.rng
    ssds = [make_ssd(world) for _ in range(rng.randint(8, 14))]
    rows = "ABCD"[: rng.randint(2, 4)]
    shelves = [[f"{r}{i}" for i in range(1, rng.randint(2, 5))] for r in rows]
    return {"ssds": ssds, "shelves": shelves}


def check(ctx):
    ctx.expect(".append(" not in ctx.code, "Today's challenge: no .append()! Build every list with a comprehension.")
    for seed in range(1, 5):
        r = ctx.run(seed=seed)
        ctx.need(r, "working", "serials", "to_tb", "sizes_tb", "capacity", "all_slots")
        ssds, shelves = r.get("ssds"), r.get("shelves")
        working = [s for s in ssds if s["health"] >= 20]
        ctx.expect(r.get("working") == working, "working should keep only drives with health 20 or more, in order.")
        ctx.expect(r.get("serials") == [s["serial"] for s in working], "serials should be the serial of every WORKING drive.")
        to_tb = r.get("to_tb")
        ctx.expect(callable(to_tb) and to_tb(2000) == 2 and to_tb(512) == 0.512,
                   "to_tb should be a lambda that divides by 1000: lambda gb: gb / 1000")
        ctx.expect("lambda" in ctx.code, "Make to_tb with the lambda keyword.")
        ctx.expect(r.get("sizes_tb") == [s["gb"] / 1000 for s in working], "sizes_tb should be each working drive's gb / 1000.")
        ctx.expect(r.get("capacity") == {s["serial"]: s["gb"] for s in working},
                   "capacity should be a dict of serial → gb for the working drives. Try {s[\"serial\"]: s[\"gb\"] for s in working}.")
        ctx.expect(r.get("all_slots") == [x for row in shelves for x in row],
                   "all_slots should be one flat list of every slot, row by row.")
        if seed == 1:
            for s in ssds:
                ctx.show("part", label=s["serial"], result="ship" if s["health"] >= 20 else "reject")
