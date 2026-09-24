from factory.machines import BoardTester, make_board

SUCCESS = "🛡️ Faulty boards caught, the line never stopped. Foreman Flo is doing a little dance!"


def setup(world):
    rng = world.rng
    boards = []
    for _ in range(rng.randint(10, 16)):
        roll = rng.random()
        boards.append(make_board(world, fault="blown" if roll < 0.18 else "no_bios" if roll < 0.3 else None))
    # every shift has at least one of each fault
    boards.insert(rng.randint(1, 4), make_board(world, fault="blown"))
    boards.insert(rng.randint(5, 9), make_board(world, fault="no_bios"))
    return {"boards": boards, "tester": BoardTester()}


def sort_boards(boards):
    ok, blown, no_bios = [], [], []
    for b in boards:
        if b["volts"] > 1.5:
            blown.append(b["serial"])
        elif "bios" not in b:
            no_bios.append(b["serial"])
        else:
            ok.append(b["serial"])
    return ok, blown, no_bios


def check(ctx):
    for seed in range(1, 5):
        r = ctx.run(seed=seed)
        boards = r.get("boards")
        ok, blown, no_bios = sort_boards(boards)
        if r.error:
            if seed == 1:
                done = len(r.get("tester").installed)
                for b in boards[:done]:
                    ctx.show("part", label=b["serial"], result="ship")
                if done < len(boards):
                    ctx.show("part", label=boards[done]["serial"], result="crash")
            ctx.expect(False, "💥 A faulty board crashed the whole line!\n" + r.error +
                       "\nWrap tester.install(board) in try: ... except ...: so one bad board can't stop everything.")
        ctx.need(r, "installed", "blown", "no_bios", "checked", "check_volts")
        ctx.expect(r.get("blown") == blown, f"blown should list the boards that raised ValueError: {blown}")
        ctx.expect(r.get("no_bios") == no_bios, f"no_bios should list the boards that raised KeyError: {no_bios}")
        ctx.expect(r.get("installed") == ok, "installed should only list boards that installed with NO error. Use else:.")
        ctx.expect(r.get("checked") == len(boards), "checked should count EVERY board. Put checked += 1 in a finally: block.")
        ctx.expect(sum("Blown" in l or "blew" in l for l in r.lines) >= len(blown),
                   "Print a message (including the error) for each blown board. Use except ValueError as err:.")
        if seed == 1:
            for b in boards:
                ctx.show("part", label=b["serial"], result="ship" if b["serial"] in ok else "reject")

    check_volts = r.get("check_volts")
    ctx.expect(callable(check_volts), "check_volts should be a function.")
    try:
        check_volts(1.9)
        raised = None
    except ValueError:
        raised = "ValueError"
    except Exception as exc:
        raised = type(exc).__name__
    ctx.expect(raised == "ValueError", "check_volts(1.9) should raise a ValueError. Use raise ValueError(\"...\").")
    ctx.expect(check_volts(1.2) is True and check_volts(1.5) is True, "check_volts should return True when volts is 1.5 or less.")
    ctx.expect("finally" in ctx.code, "Use a finally: block to count every checked board.")
