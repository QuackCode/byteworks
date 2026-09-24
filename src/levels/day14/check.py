import contextlib
import io

from factory.machines import make_ssd

SUCCESS = "🔗 The pipeline is humming: functions feeding functions, and every label is logged!"


def setup(world):
    return {"ssds": [make_ssd(world) for _ in range(world.rng.randint(8, 12))]}


def check(ctx):
    code = ctx.code
    for word in ("map(", "filter(", "reduce(", "sorted("):
        ctx.expect(word in code, f"Use {word[:-1]}() for today's pipeline.")
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        ctx.need(r, "gbs", "healthy", "total_gb", "ranked", "logged", "make_label")
        ssds = r.get("ssds")
        ctx.expect(r.get("gbs") == [s["gb"] for s in ssds], "gbs should be a list of every drive's gb. Remember list(map(...)).")
        ctx.expect(r.get("healthy") == [s for s in ssds if s["health"] >= 20],
                   "healthy should be the drives with health >= 20. Remember list(filter(...)).")
        ctx.expect(r.get("total_gb") == sum(s["gb"] for s in ssds), "total_gb should add up all the gbs using reduce.")
        ranked = sorted(ssds, key=lambda s: s["health"], reverse=True)
        ctx.expect([s["health"] for s in r.get("ranked")] == [s["health"] for s in ranked],
                   "ranked should be sorted by health, HIGHEST first. Use key=... and reverse=True.")

    # Test the decorator on a brand-new function
    logged = r.get("logged")
    def spin_up(a, b):
        return a * b
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            wrapped = logged(spin_up)
            result = wrapped(6, 7) if callable(wrapped) else None
        except Exception as exc:
            ctx.expect(False, f"Your logged decorator crashed: {type(exc).__name__}: {exc}")
    ctx.expect(callable(wrapped), "logged should RETURN the wrapper function (return wrapper, no brackets).")
    ctx.expect(result == 42, "The wrapper should return whatever the original function returns: return func(*args).")
    ctx.expect("Running spin_up" in out.getvalue(), "The wrapper should print Running followed by func.__name__ before calling it.")
    ctx.expect("@logged" in code, "Put @logged on the line above def make_label.")
    ctx.expect(any(l.startswith("Running make_label") for l in r.lines), "Calling make_label should print Running make_label.")
    for s in ranked[:6]:
        ctx.show("part", label=s["serial"], result="ship" if s["health"] >= 20 else "reject")
