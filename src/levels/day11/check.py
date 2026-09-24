SUCCESS = "🛠️ Your functions are bolted into the CPU Builder. Any order, any size, no problem!"


def check(ctx):
    r = ctx.run()
    ctx.need(r, "build_cpu", "is_faulty", "total_cores")
    build, faulty, total = r.get("build_cpu"), r.get("is_faulty"), r.get("total_cores")
    for f, name in ((build, "build_cpu"), (faulty, "is_faulty"), (total, "total_cores")):
        ctx.expect(callable(f), f"{name} should be a function. Define it with def {name}(...):")

    got = build(8, 4.5)
    ctx.expect(got is not None, "build_cpu gave back None. Did you forget to return the dict? (print only shows it.)")
    ctx.expect(got == {"cores": 8, "clock_ghz": 4.5, "score": 36.0},
               f"build_cpu(8, 4.5) should return {{'cores': 8, 'clock_ghz': 4.5, 'score': 36.0}} but gave {got!r}.")
    for cores, clock in ((4, 3.2), (16, 5.0), (2, 2.5)):
        ctx.expect(build(cores, clock) == {"cores": cores, "clock_ghz": clock, "score": cores * clock},
                   f"build_cpu({cores}, {clock}) gave the wrong dict.")
    try:
        default = build(6)
    except TypeError:
        default = None
    ctx.expect(default == {"cores": 6, "clock_ghz": 3.0, "score": 18.0},
               "build_cpu(6) should use a default clock_ghz of 3.0. Write clock_ghz=3.0 in the brackets.")

    cases = [
        ({"clock_ghz": 0, "temp_c": 50}, True), ({"clock_ghz": 3.6, "temp_c": 101}, True),
        ({"clock_ghz": 3.6, "temp_c": 100}, False), ({"clock_ghz": 4.4, "temp_c": 60}, False),
        ({"clock_ghz": 0, "temp_c": 120}, True),
    ]
    for cpu, want in cases:
        got = faulty(cpu)
        ctx.expect(got is not None, "is_faulty gave back None. Use return, not print.")
        ctx.expect(bool(got) == want and isinstance(got, bool),
                   f"is_faulty({cpu}) should return {want}.")

    chips = [{"cores": 4}, {"cores": 8}, {"cores": 16}]
    ctx.expect(total(*chips) == 28, "total_cores should add up the cores of every CPU passed in.")
    ctx.expect(total(chips[0]) == 4 and total() == 0,
               "total_cores should work with any number of CPUs, even one or none.")
    for spec in ((4, 3.2), (8, 4.5), (16, 5.0)):
        ctx.show("part", label=f"{spec[0]}-core", result="ship")
