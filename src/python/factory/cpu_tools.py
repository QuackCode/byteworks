"""CPU tools: the sorting rules you wrote on Day 9, packed into a module.
A module is just a .py file full of code that other files can import."""

GAMING_GHZ = 4.0
OFFICE_GHZ = 2.5
MAX_TEMP = 90


def grade(cpu):
    """Return "GAMING", "OFFICE" or "REJECT" for a CPU dict."""
    if cpu["temp_c"] > MAX_TEMP:
        return "REJECT"
    if cpu["clock_ghz"] >= GAMING_GHZ:
        return "GAMING"
    if cpu["clock_ghz"] >= OFFICE_GHZ:
        return "OFFICE"
    return "REJECT"
