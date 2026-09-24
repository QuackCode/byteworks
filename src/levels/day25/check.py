import io

import pandas as pd

SUCCESS = "🖨️ The weekly report is on head office's desk. The GPU floor is COMPLETE!"


def setup(world):
    rng = world.rng
    lines = ["day,model,built,faulty"]
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        for model in rng.sample(["GX-4060", "GX-4070", "RD-7800"], 2):
            built = rng.randint(60, 160)
            lines.append(f"{day},{model},{built},{rng.randint(0, built // 5)}")
    with open("gpu_week.csv", "w") as f:
        f.write("\n".join(lines) + "\n")
    return {}


def check(ctx):
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        ctx.need(r, "df", "busy", "worst_day", "by_model", "best_model")
        want = pd.read_csv(io.StringIO(r.files["gpu_week.csv"]))
        want["good"] = want["built"] - want["faulty"]
        want["fault_rate"] = want["faulty"] / want["built"] * 100
        df = r.get("df")
        ctx.expect(isinstance(df, pd.DataFrame), 'df should be a DataFrame: pd.read_csv("gpu_week.csv").')
        ctx.expect("good" in df.columns and df["good"].tolist() == want["good"].tolist(), "Add a good column: df[\"good\"] = df[\"built\"] - df[\"faulty\"].")
        ctx.expect("fault_rate" in df.columns and ((df["fault_rate"] - want["fault_rate"]).abs() < 1e-9).all(),
                   "Add a fault_rate column: faulty / built * 100.")
        busy = r.get("busy")
        ctx.expect(isinstance(busy, pd.DataFrame) and busy.index.tolist() == want[want["built"] > 100].index.tolist(),
                   "busy should be only the rows where built > 100: df[df[\"built\"] > 100].")
        ctx.expect(r.get("worst_day") == want.loc[want["fault_rate"].idxmax(), "day"],
                   "worst_day should be the day of the row with the highest fault_rate (idxmax, then .loc).")
        by_model = want.groupby("model")["good"].sum()
        got = r.get("by_model")
        ctx.expect(hasattr(got, "to_dict") and got.to_dict() == by_model.to_dict(),
                   "by_model should be df.groupby(\"model\")[\"good\"].sum().")
        ctx.expect(r.get("best_model") == by_model.idxmax(), "best_model should be the model with the most good GPUs: by_model.idxmax().")
        report = r.files.get("report.csv")
        ctx.expect(report is not None, 'Save the report: df.to_csv("report.csv", index=False).')
        saved = pd.read_csv(io.StringIO(report))
        ctx.expect(list(saved.columns) == ["day", "model", "built", "faulty", "good", "fault_rate"],
                   "report.csv should have the columns day, model, built, faulty, good, fault_rate (use index=False).")
        if seed == 1:
            for _, row in want.head(8).iterrows():
                ctx.show("part", label=f"{row['day']} {row['model'][-4:]}", result="reject" if row["fault_rate"] > 12 else "ship")
