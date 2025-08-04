def ask_mode(context=None):
    print("Choose mode:")
    print("1) Development (current path)")
    if context == "install":
        print("2) System (recommended: install to /opt/encryptsync)")
    else:
        print("2) System (installed via .deb or /opt)")

    choice = input("Choice [1/2]? ").strip()
    return choice if choice in {"1", "2"} else "1"