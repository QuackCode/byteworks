SUCCESS = "🔀 Every chip lands in the right bin. The CPU sorter is running!"

# Tricky edge cases first, then random chips
CASES = [
    (4.4, 55), (4.0, 70), (3.9, 50), (2.5, 80), (2.4, 40), (5.0, 95),
    (5.0, 90), (3.2, 91), (4.0, 59), (4.0, 60), (2.1, 99),
]


def setup(world, clock=None, temp=None):
    rng = world.rng
    return {"cpu": {
        "serial": world.serial("CPU"),
        "clock_ghz": clock if clock is not None else rng.choice([2.1, 2.8, 3.2, 3.6, 4.0, 4.4, 5.0]),
        "temp_c": temp if temp is not None else rng.randint(40, 110),
    }}


def expected(cpu):
    if cpu["temp_c"] > 90:
        return "REJECT"
    if cpu["clock_ghz"] >= 4.0:
        return "GAMING"
    if cpu["clock_ghz"] >= 2.5:
        return "OFFICE"
    return "REJECT"


def describe(cpu):
    return f"a {cpu['clock_ghz']} GHz chip at {cpu['temp_c']}°C"


def check(ctx):
    runs = [ctx.run(seed=i, setup_args={"clock": c, "temp": t}) for i, (c, t) in enumerate(CASES, 1)]
    runs += [ctx.run(seed=s) for s in range(20, 32)]
    for r in runs:
        ctx.need(r, "grade", "premium")
        cpu = r.get("cpu")
        want = expected(cpu)
        ctx.expect(r.get("grade") == want, f"For {describe(cpu)} the grade should be {want!r} but you gave {r.get('grade')!r}.")
        prem = want == "GAMING" and cpu["temp_c"] < 60
        ctx.expect(r.get("premium") is prem, f"For {describe(cpu)}, premium should be {prem}.")
    for r in runs[:8]:
        cpu = r.get("cpu")
        ctx.show("part", label=f"{cpu['clock_ghz']}GHz", result="reject" if expected(cpu) == "REJECT" else "ship")
