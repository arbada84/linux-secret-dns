import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("prepare_input", Path(__file__).with_name("prepare_input.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InputResetTests(unittest.TestCase):
    def test_laptop_reset_precedes_remmina_start(self):
        calls = []
        with patch.object(module, "reset_local", side_effect=lambda: calls.append("reset")), patch.object(
            module.os, "execlp", side_effect=lambda *args: calls.append("launch")
        ):
            module.launch("msi-lan")
        self.assertEqual(calls, ["reset", "launch"])

    def test_unknown_profile_does_not_change_input_or_launch(self):
        with patch.object(module, "reset_local") as reset, patch.object(module.os, "execlp") as launch:
            with self.assertRaises(ValueError):
                module.launch("other")
            reset.assert_not_called()
            launch.assert_not_called()

    def test_existing_display_is_detected_without_fixed_display_number(self):
        self.assertEqual(module.remote_display("1984 /usr/lib/xorg/Xorg :12 -auth .Xauthority\n"), ":12")

    def test_ambiguous_or_absent_sessions_are_not_changed(self):
        for processes in ("", "1 Xorg :10 -auth x\n2 Xorg :11 -auth y\n"):
            with self.assertRaises(RuntimeError):
                module.remote_display(processes)

    def test_caps_reset_changes_only_lock_modifier(self):
        with patch.object(module.ctypes, "CDLL") as library:
            library.return_value.XOpenDisplay.return_value = 42
            module.caps_off()
            library.return_value.XkbLockModifiers.assert_called_once_with(42, 0x100, 2, 0)
            library.return_value.XCloseDisplay.assert_called_once_with(42)


if __name__ == "__main__":
    unittest.main()
