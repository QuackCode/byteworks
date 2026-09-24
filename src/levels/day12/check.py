import math
import statistics

from factory.cpu_tools import grade
from factory.machines import make_cpu

SUCCESS = "📦 Audit passed! The CPU floor is COMPLETE, and chips are heading upstairs."


def setup(world):
    rng = world.rng
    return {"batch": [make_cpu(world, dead=rng.random() < 0.1, hot=rng.random() < 0.1) for _ in range(rng.randint(13, 30))]}


def check(ctx):
    code = ctx.code
    ctx.expect("import statistics as stats" in code, "Import statistics with the nickname stats: import statistics as stats")
    ctx.expect("from factory.cpu_tools import grade" in code, "Import the grade function: from factory.cpu_tools import grade")
    for seed in range(1, 5):
        r = ctx.run(seed=seed)
        ctx.need(r, "boxes", "audit", "avg_clock", "grades")
        batch = r.get("batch")
        ctx.expect(r.get("boxes") == math.ceil(len(batch) / 12),
                   f"{len(batch)} chips need {math.ceil(len(batch) / 12)} boxes of 12. Round UP with math.ceil.")
        ctx.expect(r.get("audit") in batch, "audit should be one chip picked from batch. Try random.choice(batch).")
        ctx.expect(abs(r.get("avg_clock") - statistics.mean(c["clock_ghz"] for c in batch)) < 1e-9,
                   "avg_clock should be the mean clock_ghz of the whole batch. Use stats.mean(clocks).")
        ctx.expect(r.get("grades") == [grade(c) for c in batch], "grades should hold grade(cpu) for every chip, in order.")
        if seed == 1:
            for cpu in batch[:10]:
                ctx.show("part", label=cpu["serial"], result="reject" if grade(cpu) == "REJECT" else "ship")
