## pandas: spreadsheets inside Python

**pandas** is the go-to package for tables of data. Its main object is the **DataFrame**: rows and columns, like a spreadsheet. Each column is a **Series**.

```python
import pandas as pd
df = pd.DataFrame({
    "model": ["GX-60", "GX-70", "GX-60"],
    "built": [120, 80, 95],
    "faulty": [6, 2, 12],
})
print(df)
print(df.shape)            # (rows, columns)
print(df.columns.tolist())
```

## Loading data

```python
import pandas as pd
with open("tiny.csv", "w") as f:
    f.write("day,built\nMon,120\nTue,98\n")
df = pd.read_csv("tiny.csv")
print(df.head())           # the first 5 rows
```

You can load Excel files and JSON too, and save with `df.to_csv("out.csv", index=False)`.

## Columns

```python
import pandas as pd
df = pd.DataFrame({"built": [120, 80], "faulty": [6, 2]})
print(df["built"])                     # one column (a Series)
print(df["built"].sum(), df["built"].mean(), df["built"].max())
df["good"] = df["built"] - df["faulty"]  # new column, calculated for EVERY row
print(df)
```

## Filtering rows

Just like NumPy masks:

```python
import pandas as pd
df = pd.DataFrame({"model": ["A", "B", "C"], "built": [120, 80, 150]})
print(df[df["built"] > 100])
print(df[(df["built"] > 100) & (df["model"] != "C")])   # & = and, | = or
```

## Finding a specific value

- `df.loc[row_label, "column"]` reads one cell
- `series.idxmax()` / `idxmin()` gives the **label** of the biggest or smallest value

```python
import pandas as pd
df = pd.DataFrame({"day": ["Mon", "Tue", "Wed"], "built": [120, 80, 150]})
best = df["built"].idxmax()
print(best, df.loc[best, "day"])
```

## Grouping

`groupby` splits the rows into groups, then summarises each group:

```python
import pandas as pd
df = pd.DataFrame({"model": ["A", "B", "A"], "built": [10, 20, 30]})
totals = df.groupby("model")["built"].sum()
print(totals)
print(totals.idxmax())
```

## Your task

Your folder has `gpu_week.csv` with the columns `day`, `model`, `built` and `faulty`.

1. `df`: load the CSV
2. Add a column `good` = built − faulty
3. Add a column `fault_rate` = faulty ÷ built × 100
4. `busy`: only the rows where `built` is more than 100
5. `worst_day`: the `day` of the row with the **highest** fault rate
6. `by_model`: the total `good` GPUs for each model (`groupby`)
7. `best_model`: the model with the most good GPUs
8. Save the whole `df` to `report.csv` (without the index)
