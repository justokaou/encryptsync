def ask_mode(context=None):
    print("Select environment mode:")
    print("1) Development (use local project and config in current folder)")

    if context == "install":
        print("2) System install (install code to /usr/lib or /opt, config to /etc or ~/.config)")
    else:
        print("2) System mode (use installed code from /usr/lib or /opt, config from /etc or ~/.config)")

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
