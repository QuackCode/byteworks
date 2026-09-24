# Day 20: You're given boards (list of dicts) and pip
# 1. install boardcheck version 2.1
pip.install("boardcheck==2.1")

# 2. import it
import boardcheck

results = {b["serial"]: boardcheck.scan(b) for b in boards}

# 4. install rgbglow, then uninstall it
pip.install("rgbglow")
pip.uninstall("rgbglow")

# 5. save requirements.txt
with open("requirements.txt", "w") as f:
    f.write(pip.freeze())

print(results)
