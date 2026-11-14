#!/usr/bin/python3
"""Reset input at RDP connection entry without restarting either desktop."""

import ctypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def caps_off():
    x11 = ctypes.CDLL("libX11.so.6")
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XkbLockModifiers.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
    x11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    display = x11.XOpenDisplay(None)
    if not display:
        raise RuntimeError("X11 display unavailable")
    try:
        # LockMask only: preserve Num Lock and the user's other keyboard settings.
        if not x11.XkbLockModifiers(display, 0x100, 2, 0):
            raise RuntimeError("Caps Lock reset failed")
        x11.XSync(display, 0)
    finally:
        x11.XCloseDisplay(display)


def remote_display(processes):
    displays = set(re.findall(r"(?:^|\s)(:\d+)\s", processes))
    if len(displays) != 1:
        raise RuntimeError("Expected one existing remote Xorg display")
    return displays.pop()


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=4)


def reset_remote():
    processes = run(["pgrep", "-a", "-u", str(os.getuid()), "-x", "Xorg"]).stdout
    os.environ["DISPLAY"] = remote_display(processes)
    os.environ["XAUTHORITY"] = str(Path.home() / ".Xauthority")
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{os.getuid()}/bus"
    caps_off()
    run(["gsettings", "set", "org.freedesktop.ibus.engine.hangul", "initial-input-mode", "latin"])
    if run(["ibus", "engine"]).stdout.strip() == "hangul":
        run(["ibus", "engine", "xkb:us::eng"])
        run(["ibus", "engine", "hangul"])
    print("REMOTE_INPUT_RESET_OK")


def reset_local():
    caps_off()
    if shutil.which("fcitx5-remote"):
        run(["fcitx5-remote", "-c"])


def launch(profile):
    if profile not in ("msi-lan", "msi-vpn", "remote-192-168-31-91"):
        raise ValueError("Unknown MSI connection profile")
    reset_local()
    path = Path.home() / ".local/share/remmina" / f"{profile}.remmina"
    os.execlp("remmina", "remmina", f"--connect={path}")


def prepare():
    reset_local()
    result = subprocess.run(
        ["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
         "-o", "ConnectTimeout=3", "msi-vpn", "python3", "-", "--remote-input"],
        input=Path(__file__).read_text(), capture_output=True, text=True, timeout=15,
    )
    if result.returncode:
        raise RuntimeError("Remote input reset unavailable; local input was reset")
    print("LOCAL_AND_REMOTE_INPUT_RESET_OK")


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["--remote-input"]:
            reset_remote()
        elif sys.argv[1:] == ["--local-input"]:
            reset_local()
        elif len(sys.argv) == 3 and sys.argv[1] == "--connect":
            launch(sys.argv[2])
        elif not sys.argv[1:]:
            prepare()
        else:
            raise ValueError("Unsupported arguments")
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
        # Do not block RDP authentication if the independent SSH reset is unavailable.
        print(f"RDP input preparation: {type(exc).__name__}: {exc}", file=sys.stderr)
        if sys.argv[1:] == ["--remote-input"]:
            sys.exit(1)
