SUCCESS = "🧯 All six bugs squashed. The report prints perfectly. You're a real debugger now!"

EXPECTED = [
    "Drives: 4",
    "Last drive: SSD-04",
    "Total GB: 5512",
    "Warehouse capacity: 2000",
    "Drives after restock: 5",
]


def check(ctx):
    r = ctx.run()
    ctx.no_crash(r)
    for line in EXPECTED:
        ctx.expect(line in r.lines, f"The report should include the line: {line}")
    ctx.expect(r.get("total") == 5512, "total should add up every drive's gb (5512).")
    ctx.expect(len(r.get("ssds", [])) == 5, "After the restock there should be 5 drives in ssds.")
    for s in r.get("ssds"):
        ctx.show("part", label=s["serial"], result="ship")
