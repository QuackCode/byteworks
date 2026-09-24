# Day 9: You're given cpu, e.g. {"serial": "CPU-1201", "clock_ghz": 4.4, "temp_c": 55}
print("Testing", cpu["serial"], cpu["clock_ghz"], "GHz", cpu["temp_c"], "°C")

if cpu["temp_c"] > 90:
    grade = "REJECT"
elif cpu["clock_ghz"] >= 4.0:
    grade = "GAMING"
elif cpu["clock_ghz"] >= 2.5:
    grade = "OFFICE"
else:
    grade = "REJECT"

premium = grade == "GAMING" and cpu["temp_c"] < 60
print("Grade:", grade)
