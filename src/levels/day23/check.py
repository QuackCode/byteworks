from factory.pip_sim import VenvManager

SUCCESS = "🧪 Two pods, two versions, zero fights. Both GPU teams are happy!"


def setup(world):
    return {"venv": VenvManager()}


def check(ctx):
    r = ctx.run()
    ctx.need(r, "render", "tester", "tester_version")
    venv = r.get("venv")
    envs = venv.envs
    ctx.expect("gpu-render" in envs and "gpu-tester" in envs, 'Create both environments: venv.create("gpu-render") and venv.create("gpu-tester").')
    ctx.expect(envs["gpu-render"].installed == {"rgbglow": "0.9", "boardcheck": "2.1"},
               "gpu-render should have exactly rgbglow 0.9 and boardcheck 2.1 installed.")
    ctx.expect(envs["gpu-tester"].installed == {"rgbglow": "1.3"}, "gpu-tester should have only rgbglow 1.3 installed.")
    ctx.expect(venv.active == "gpu-tester", 'Activate the tester environment: venv.activate("gpu-tester").')
    ctx.expect(r.get("tester_version") == "1.3", "tester_version should be rgbglow.__version__ after activating gpu-tester (1.3).")
    files = r.files
    ctx.expect(files.get("gpu-render-requirements.txt") == "boardcheck==2.1\nrgbglow==0.9\n",
               "gpu-render-requirements.txt should contain gpu-render's freeze() text.")
    ctx.expect(files.get("gpu-tester-requirements.txt") == "rgbglow==1.3\n",
               "gpu-tester-requirements.txt should contain gpu-tester's freeze() text.")
    ctx.show("part", label="render 0.9", result="ship")
    ctx.show("part", label="tester 1.3", result="ship")
