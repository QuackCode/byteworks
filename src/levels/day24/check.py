import numpy as np

SUCCESS = "📈 Benchmarks crunched in a blink. The stickers are printing!"


def setup(world):
    rng = world.rng
    scores = [round(rng.gauss(7500, 1600), 1) for _ in range(rng.randint(150, 400))]
    return {"scores": scores}


def close(a, b):
    try:
        return np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float))
    except (TypeError, ValueError):
        return False


def check(ctx):
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        ctx.need(r, "arr", "mean", "median", "spread", "failures", "elite", "rating", "grid", "row_means")
        arr = np.array(r.get("scores"))
        ctx.expect(isinstance(r.get("arr"), np.ndarray), "arr should be a NumPy array: np.array(scores).")
        ctx.expect(close(r.get("mean"), arr.mean()), "mean should be arr.mean().")
        ctx.expect(close(r.get("median"), np.median(arr)), "median should be np.median(arr).")
        ctx.expect(close(r.get("spread"), arr.std()), "spread should be the standard deviation: arr.std().")
        ctx.expect(r.get("failures") == int((arr < 5000).sum()) and isinstance(r.get("failures"), int),
                   "failures should COUNT the scores below 5000, as an int: int((arr < 5000).sum()).")
        ctx.expect(close(r.get("elite"), arr[arr >= 9000]), "elite should keep only scores of 9000 or more: arr[arr >= 9000].")
        ctx.expect(close(r.get("rating"), (arr - arr.min()) / (arr.max() - arr.min())),
                   "rating should be (arr - arr.min()) / (arr.max() - arr.min()), so every value is between 0 and 1.")
        grid = arr[:12].reshape(3, 4)
        ctx.expect(np.shape(r.get("grid")) == (3, 4) and close(r.get("grid"), grid), "grid should be arr[:12].reshape(3, 4).")
        ctx.expect(close(r.get("row_means"), grid.mean(axis=1)), "row_means should be the mean of each ROW: grid.mean(axis=1).")
        if seed == 1:
            for s in arr[:10]:
                ctx.show("part", label=f"{s:.0f} pts", result="ship" if s >= 5000 else "reject")
