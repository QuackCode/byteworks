import re

SUCCESS = "🕵️ Every counterfeit caught! The supply chain is clean again."

REAL = re.compile(r"MB-\d{4}-[A-Z]{2}")


def fakes(rng, real):
    digits, letters = real[3:7], real[8:10]
    return [
        f"MB-{digits}-{letters}Z",          # extra letter at the end
        f"XMB-{digits}-{letters}",          # extra letter at the start
        f"mb-{digits}-{letters}",           # lowercase
        f"MB-{digits[:3]}-{letters}",       # only 3 digits
        f"MB-{digits}-{letters.lower()}",   # lowercase letters
        f"MB-{digits[:2]}O{digits[3]}-{letters}",  # letter O instead of zero
        f"MB {digits}-{letters}",           # space instead of dash
    ]


def setup(world):
    rng = world.rng
    real = [f"MB-{rng.randint(0, 9999):04d}-{rng.choice('ABCDEFGHJKLMNPRSTXYZ')}{rng.choice('ABCDEFGHJKLMNPRSTXYZ')}" for _ in range(7)]
    fake = rng.sample(fakes(rng, real[0]), 4) + [fakes(rng, real[1])[0], fakes(rng, real[2])[1]]
    scans = real + fake
    rng.shuffle(scans)
    memo = f"Batches {rng.randint(1000, 9999)} and {rng.randint(1000, 9999)} passed; batch {rng.randint(1000, 9999)} is on hold (ref 42)."
    phone = f"07{rng.randint(100, 999)} {rng.randint(100000, 999999)}"
    return {"scans": scans, "memo": memo, "phone": phone}


def check(ctx):
    for seed in range(1, 6):
        r = ctx.run(seed=seed)
        ctx.need(r, "pattern", "genuine", "counterfeit", "batch_numbers", "redacted")
        scans = r.get("scans")
        genuine = [s for s in scans if REAL.fullmatch(s)]
        counterfeit = [s for s in scans if not REAL.fullmatch(s)]
        sneaky = [s for s in counterfeit if s in r.get("genuine")]
        ctx.expect(not sneaky, f"These fakes got through as genuine: {sneaky}. Tighten your pattern (don't forget ^ and $).")
        missed = [s for s in genuine if s not in r.get("genuine")]
        ctx.expect(not missed, f"These real serials were marked fake: {missed}.")
        ctx.expect(r.get("genuine") == genuine, "genuine should list the real serials in their original order.")
        ctx.expect(r.get("counterfeit") == counterfeit, "counterfeit should list every scan that ISN'T genuine, in order.")
        memo = r.get("memo")
        ctx.expect(r.get("batch_numbers") == re.findall(r"\d{4}", memo), "batch_numbers should be every 4-digit number in memo (re.findall).")
        ctx.expect(r.get("redacted") == re.sub(r"\d", "#", r.get("phone")), "redacted should be phone with every digit swapped for # (re.sub).")
        if seed == 1:
            for s in scans[:10]:
                ctx.show("part", label=s[:10], result="ship" if REAL.fullmatch(s) else "reject")
