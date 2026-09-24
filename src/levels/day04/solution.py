# Day 4: The scanner gives you raw_code, e.g. "  ram-0042  "
print("Scanned:", repr(raw_code))

clean = raw_code.strip().upper()
part_type = clean[:3]
number = clean[-4:]
label = f"{part_type} #{number}"
print(label)

sku = clean.replace("-", "")
is_ram = clean.startswith("RAM")
