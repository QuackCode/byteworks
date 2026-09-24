# Day 18: You're given scans (list of strings), memo (text) and phone (text)
import re

pattern = r"^MB-\d{4}-[A-Z]{2}$"
genuine = [s for s in scans if re.match(pattern, s)]
counterfeit = [s for s in scans if not re.match(pattern, s)]

batch_numbers = re.findall(r"\d{4}", memo)
redacted = re.sub(r"\d", "#", phone)

print("Genuine:", genuine)
print("FAKES:", counterfeit)
