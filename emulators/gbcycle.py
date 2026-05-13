from util import *
from emulator import Emulator
from test import *
import os


def _is_windows_x86_64_asset(name):
    name = name.lower()
    return (
        name.endswith(".zip")
        and ("windows" in name or "win64" in name)
        and ("x86_64" in name or "x64" in name or "win64" in name or "amd64" in name)
        and "arm64" not in name
        and "aarch64" not in name
        and "debug" not in name
        and "symbols" not in name
        and "pdb" not in name
    )


class GbCycle(Emulator):
    def __init__(self):
        super().__init__("gb-cycle", "https://github.com/pakitovic/gb-cycle", startup_time=8.0, features=(PCM,))
        self.title_check = lambda title: title.startswith("gb-desktop |")
        self.executable = None

    def setup(self):
        downloadGithubRelease(
            "pakitovic/gb-cycle",
            "downloads/gb-cycle.zip",
            filter=_is_windows_x86_64_asset,
            require_asset=True,
        )
        extract("downloads/gb-cycle.zip", "emu/gb-cycle")
        self.executable = os.path.abspath(self._find_executable())
        setDPIScaling(self.executable)

    def _find_executable(self):
        for root, _dirs, files in os.walk("emu/gb-cycle"):
            if "gb-desktop.exe" in files:
                return os.path.join(root, "gb-desktop.exe")
        raise RuntimeError("Could not find gb-desktop.exe in gb-cycle release archive")

    def startProcess(self, rom, *, model, required_features):
        model = {DMG: "DMG", CGB: "CGB"}.get(model)
        if model is None:
            return None

        env = os.environ.copy()
        env["SDL_RENDER_DRIVER"] = "software"
        return subprocess.Popen([
            self.executable,
            os.path.abspath(rom),
            "--model", model,
            "--palette", "grey",
            "--startup", "custom-boot",
            "--mode", "permissive",
            "--scale", "1",
            "--mute",
            "--no-saves",
            "--no-rewind",
            "--no-gamepad",
            "--no-vsync",
        ], cwd=os.path.dirname(self.executable), env=env)
