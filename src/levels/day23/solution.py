# Day 23: You're given venv (the virtual environment manager)

render = venv.create("gpu-render")
render.install("rgbglow==0.9")
render.install("boardcheck==2.1")

tester = venv.create("gpu-tester")
tester.install("rgbglow==1.3")

venv.activate("gpu-tester")
import rgbglow
tester_version = rgbglow.__version__

for env in [render, tester]:
    with open(f"{env.name}-requirements.txt", "w") as f:
        f.write(env.freeze())

print("Tester is using rgbglow", tester_version)
