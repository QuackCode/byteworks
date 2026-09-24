# Day 16: You're given made_at (text) and inspected (a datetime)
from datetime import datetime, timedelta

made = datetime.strptime(made_at, "%Y-%m-%d %H:%M")
warranty_ends = made + timedelta(days=1095)
ship_by = made + timedelta(hours=48)
label_date = made.strftime("%d/%m/%Y")
age_days = (inspected - made).days
night_shift = made.hour >= 22 or made.hour < 6

print("Made:", label_date, "| Ship by:", ship_by, "| Age:", age_days, "days")
