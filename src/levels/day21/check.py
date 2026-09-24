SUCCESS = "🏗️ Blueprints approved! The Motherboard floor is COMPLETE. Boards are heading up to the GPU floor."


def check(ctx):
    r = ctx.run()
    ctx.need(r, "Motherboard", "GamingBoard")
    MB, GB = r.get("Motherboard"), r.get("GamingBoard")
    ctx.expect(isinstance(MB, type) and isinstance(GB, type), "Motherboard and GamingBoard should both be classes (class Name:).")

    b = MB("MB-7777", "LGA1851")
    ctx.expect((getattr(b, "serial", None), getattr(b, "socket", None), getattr(b, "ram_slots", None)) == ("MB-7777", "LGA1851", 4),
               "Motherboard(\"MB-7777\", \"LGA1851\") should store self.serial, self.socket and self.ram_slots (default 4).")
    ctx.expect(getattr(b, "ram", None) == [], "Each new board should start with self.ram = [] (an empty list).")
    ctx.expect(MB("MB-1", "AM5").ram is not b.ram, "Each board needs its OWN ram list. Create it inside __init__.")
    ctx.expect(str(b) == "Motherboard MB-7777 (LGA1851)", f"str(board) should be 'Motherboard MB-7777 (LGA1851)' but was {str(b)!r}. Does __str__ return it?")

    small = MB("MB-2", "AM5", ram_slots=2)
    small.install_ram("A")
    small.install_ram("B")
    ctx.expect(small.ram == ["A", "B"], "install_ram should add the stick to self.ram.")
    try:
        small.install_ram("C")
        raised = None
    except ValueError:
        raised = "ValueError"
    except Exception as exc:
        raised = type(exc).__name__
    ctx.expect(raised == "ValueError", "Installing RAM into a full board should raise a ValueError.")
    ctx.expect(small.ram == ["A", "B"], "When the board is full, don't add the stick.")

    g = GB("MB-9000", "AM5")
    ctx.expect(issubclass(GB, MB), "GamingBoard should inherit from Motherboard: class GamingBoard(Motherboard):")
    ctx.expect(g.ram_slots == 8 and g.ram == [] and g.serial == "MB-9000", "GamingBoard should use super().__init__(serial, socket, ram_slots=8).")
    ctx.expect(getattr(g, "rgb", None) is True, "GamingBoard should set self.rgb = True.")
    ctx.expect("super()" in ctx.code, "Use super().__init__(...) in GamingBoard.")
    ctx.expect(str(g) == "Motherboard MB-9000 (AM5)", "GamingBoard should inherit __str__ from Motherboard.")
    for i in range(8):
        g.install_ram(f"DDR5-{i}")
    ctx.show("part", label="MB-7777", result="ship")
    ctx.show("part", label="MB-9000 RGB", result="ship")
