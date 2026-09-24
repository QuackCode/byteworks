SUCCESS = "⚡ The lights flicker on. ByteWorks is ONLINE!"


def check(ctx):
    r = ctx.run()
    ctx.no_crash(r)
    ctx.expect("Factory online" in r.lines,
               "The control computer is waiting for the exact message: Factory online")
    ctx.expect("168" in r.lines,
               "Now print how many hours are in a week, using 24 * 7.")
    ctx.expect("168" not in ctx.code,
               "Let Python do the maths! Write 24 * 7 instead of typing the answer.")
    ctx.show("power_on")
