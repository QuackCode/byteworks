SUCCESS = "🎛️ The control panel beeps happily. Settings saved!"

OPERATORS = ["Ada", "Grace", "Alan", "Linus", "Margaret"]


def check(ctx):
    name = OPERATORS[0]
    r = ctx.run(inputs=[name])
    ctx.need(r, "factory_name", "machines", "power_kw", "is_open", "name_length", "operator")
    ctx.expect(r.get("factory_name") == "ByteWorks", 'factory_name should be the text "ByteWorks" (in quotes).')
    ctx.expect(type(r.get("machines")) is int and r.get("machines") == 3, "machines should be the whole number 3 (no quotes).")
    ctx.expect(type(r.get("power_kw")) is float and r.get("power_kw") == 12.5, "power_kw should be the decimal 12.5.")
    ctx.expect(r.get("is_open") is True, "is_open should be True (capital T, no quotes).")
    ctx.expect(r.get("name_length") == 9, "name_length should be the length of factory_name. Use len().")
    ctx.expect("len(" in ctx.code, "Use len() to work out name_length. Don't count by hand!")
    ctx.expect(r.get("operator") == name, "Store what input() gives back in the variable operator.")
    ctx.expect(f"Welcome, {name}" in r.lines, f"Greet the operator: for {name} it should print Welcome, {name}")
    other = ctx.run(seed=2, inputs=[OPERATORS[3]])
    ctx.expect(f"Welcome, {OPERATORS[3]}" in other.lines,
               "Greet whoever is using the panel, not one fixed name. Use the operator variable.")
    ctx.show("display", text=f"Welcome, {name}")
