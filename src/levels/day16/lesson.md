## The `datetime` module

Dates are surprisingly tricky: months have different lengths, there are leap years, and so on. Python's `datetime` module handles all of it.

```python
from datetime import datetime, date, timedelta

now = datetime.now()
print(now)
print(now.year, now.month, now.day, now.hour, now.minute)
```

## Making a specific date

```python
from datetime import datetime
launch = datetime(2026, 3, 14, 9, 30)    # year, month, day, hour, minute
print(launch)
print(launch.strftime("%A"))             # the day of the week
```

## Text → datetime: `strptime` ("string parse time")

Timestamps often arrive as text. Tell `strptime` the **format** using these codes:

| Code | Means | Example |
|---|---|---|
| `%Y` | 4-digit year | 2026 |
| `%m` | month (01–12) | 03 |
| `%d` | day (01–31) | 14 |
| `%H` | hour (00–23) | 09 |
| `%M` | minute | 30 |
| `%B` | month name | March |
| `%A` | weekday name | Saturday |

```python
from datetime import datetime
made = datetime.strptime("2026-03-14 09:30", "%Y-%m-%d %H:%M")
print(made.month, made.hour)
```

## datetime → text: `strftime` ("string format time")

```python
from datetime import datetime
made = datetime(2026, 3, 14, 9, 30)
print(made.strftime("%d/%m/%Y"))          # 14/03/2026
print(made.strftime("%B %d, %Y at %H:%M"))
```

## Date maths with `timedelta`

A `timedelta` is a **length of time**. Add or subtract it from a datetime:

```python
from datetime import datetime, timedelta
made = datetime(2026, 3, 14, 9, 30)
print(made + timedelta(days=30))
print(made - timedelta(hours=12))
```

Subtracting two datetimes gives you a `timedelta`:

```python
from datetime import datetime
a = datetime(2026, 1, 1)
b = datetime(2026, 3, 1)
gap = b - a
print(gap.days)          # 59
```

## Your task

You're given `made_at` (text like `"2026-03-14 09:30"`) and `inspected` (a datetime when the drive was inspected).

1. `made`: `made_at` turned into a datetime
2. `warranty_ends`: `made` + 1095 days (3 years)
3. `ship_by`: `made` + 48 hours
4. `label_date`: `made` as text in the form `14/03/2026`
5. `age_days`: how many whole days from `made` to `inspected`
6. `night_shift`: `True` if the drive was made at 22:00 or later, **or** before 06:00
