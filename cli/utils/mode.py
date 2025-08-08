import os
from pathlib import Path

def auto_detect_user_mode() -> bool:
    return bool(os.environ.get("XDG_RUNTIME_DIR")) and os.geteuid() != 0

def auto_detect_mode_for_run() -> str:
    # if .deb code exist -> mode "2" (prod), else "1" (dev)
    return "2" if Path("/usr/lib/encryptsync").exists() else "1"

def ask_mode():
    print("Select environment mode:")
    print("1) Development (use local project and config in current folder)")
    print("2) System mode (use installed code from /usr/lib, config from /etc or ~/.encryptsync)")

    choice = input("Choice [1/2]? ").strip()
    return choice if choice in {"1", "2"} else "1"

def ask_install_method():
    print("Select installation method:")
    print("1) System-wide (root only, runs at boot, requires key import in /root/.gnupg)")
    print("2) User-level (recommended for desktop use, uses your GPG agent)")
    choice = input("Your choice [1/2]: ").strip()

    if choice == "2":
        return "user"
    return "system"
