# Day 25: Your folder has gpu_week.csv (day, model, built, faulty)
import pandas as pd

df = pd.read_csv("gpu_week.csv")
df["good"] = df["built"] - df["faulty"]
df["fault_rate"] = df["faulty"] / df["built"] * 100

busy = df[df["built"] > 100]
worst_day = df.loc[df["fault_rate"].idxmax(), "day"]
by_model = df.groupby("model")["good"].sum()
best_model = by_model.idxmax()

df.to_csv("report.csv", index=False)

print(df)
print("Worst day:", worst_day, "| Best model:", best_model)
