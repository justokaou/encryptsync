import os
from pathlib import Path

def auto_detect_mode_for_run() -> str:
    # if .deb code exist -> mode "2" (prod), else "1" (dev)
    return "2" if Path("/usr/lib/encryptsync").exists() else "1"

def ask_mode():
    print("Select environment mode:")
    print("1) Development (use local project and config in current folder)")
    print("2) Production (installed package; uses XDG paths in your home)")

    choice = input("Choice [1/2]? ").strip()
    return choice if choice in {"1", "2"} else "1"