from factory.machines import Press, make_cpu

SUCCESS = "🔁 The press thunders along, stops itself when things get hot, and never ships a dead chip!"


def setup(world, overheat=True):
    rng = world.rng
    n = rng.randint(8, 14)
    hot_at = rng.randint(n // 2, n - 2) if overheat else None
    chips = [make_cpu(world, dead=rng.random() < 0.25, hot=(i == hot_at)) for i in range(n)]
    return {"press": Press(chips)}


def expected(press):
    good, dead, stamped = [], 0, 0
    for chip in press._chips:
        stamped += 1
        if chip["temp_c"] > 100:
            break
        if chip["clock_ghz"] == 0:
            dead += 1
            continue
        good.append(chip)
    return good, dead, stamped


def check(ctx):
    cases = [(s, {"overheat": True}) for s in (1, 2, 3)] + [(s, {"overheat": False}) for s in (4, 5)]
    for seed, args in cases:
        r = ctx.run(seed=seed, setup_args=args)
        if seed == 1:
            ctx.no_crash(r)
            nums = [l for l in r.lines if l in ("3", "2", "1")]
            ctx.expect(nums[:3] == ["3", "2", "1"], "Print a countdown 3, 2, 1 with a for loop. range(3, 0, -1) counts down.")
            ctx.expect("range(" in ctx.code, "Use range() for the countdown.")
        ctx.need(r, "good", "dead")
        press = r.get("press")
        good, dead, stamped = expected(press)
        if args["overheat"]:
            ctx.expect(press.stamped <= stamped,
                       "A chip came out over 100°C but the press kept going! Use break to stop the loop straight away.")
        ctx.expect(press.stamped >= stamped, "The press stopped too early. Keep stamping while press.has_power() is True.")
        ctx.expect(all(c["clock_ghz"] != 0 for c in r.get("good")), "A dead chip (clock_ghz == 0) got into good. Skip those with continue.")
        ctx.expect(r.get("dead") == dead, f"dead should count the dead chips: {dead} this run, but you counted {r.get('dead')}.")
        ctx.expect(r.get("good") == good, "good should hold every working chip made before the press stopped, in order.")
        for chip in good:
            ctx.expect(chip["serial"] in r.lines, "At the end, print the serial of every good chip with a for loop.")
        if seed == 1:
            for chip in press._chips[:stamped]:
                result = "crash" if chip["temp_c"] > 100 else "reject" if chip["clock_ghz"] == 0 else "ship"
                ctx.show("part", label=chip["serial"], result=result)
