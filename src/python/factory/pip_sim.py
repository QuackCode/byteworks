"""A pretend pip for the Parts Installer. Real pip downloads packages from PyPI (pypi.org);
this one "installs" small ByteWorks packages so the lesson works inside a browser."""
import sys
import types

from .core import FactoryError


def _boardcheck(version):
    mod = types.ModuleType("boardcheck")
    mod.__version__ = version

    def scan(board):
        """PASS if the board's voltage is safe and it has a BIOS, otherwise FAIL."""
        return "PASS" if board.get("volts", 99) <= 1.5 and "bios" in board else "FAIL"

    mod.scan = scan
    return mod


def _rgbglow(version):
    mod = types.ModuleType("rgbglow")
    mod.__version__ = version
    mod.glow = lambda colour="rainbow": f"✨ glowing {colour} ✨"
    return mod


CATALOGUE = {
    "boardcheck": {"versions": ["1.0", "2.0", "2.1"], "build": _boardcheck},
    "rgbglow": {"versions": ["0.9", "1.3"], "build": _rgbglow},
}


class Pip:
    def __init__(self):
        self.installed = {}
        for name in CATALOGUE:
            sys.modules.pop(name, None)

    def install(self, spec):
        name, _, version = spec.partition("==")
        name = name.strip().lower()
        if name not in CATALOGUE:
            print(f"ERROR: No matching distribution found for {spec}")
            raise FactoryError(f"There's no package called {name!r}. The Parts Installer knows: {', '.join(CATALOGUE)}")
        versions = CATALOGUE[name]["versions"]
        version = version.strip() or versions[-1]
        if version not in versions:
            raise FactoryError(f"{name} has no version {version}. Available: {', '.join(versions)}")
        print(f"Collecting {name}=={version}")
        sys.modules[name] = CATALOGUE[name]["build"](version)
        self.installed[name] = version
        print(f"Successfully installed {name}-{version}")

    def uninstall(self, name):
        name = name.lower()
        if name not in self.installed:
            print(f"WARNING: Skipping {name} as it is not installed.")
            return
        del self.installed[name]
        sys.modules.pop(name, None)
        print(f"Successfully uninstalled {name}")

    def list(self):
        print("Package     Version")
        print("----------- -------")
        for name, version in sorted(self.installed.items()):
            print(f"{name:<11} {version}")
        return dict(self.installed)

    def freeze(self):
        return "".join(f"{name}=={version}\n" for name, version in sorted(self.installed.items()))

    def __repr__(self):
        return "<pip: try pip.install('name'), pip.list(), pip.freeze()>"
