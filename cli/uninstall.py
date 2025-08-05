from cli.service import uninstall_service

def uninstall(force=False, user=False):
    if force or input("This will remove the encryptsync service. Proceed? [y/N]: ").strip().lower() == "y":
        uninstall_service("encryptsync", user=user)

    if force or input("This will remove the encryptsync-clear service. Proceed? [y/N]: ").strip().lower() == "y":
        uninstall_service("encryptsync-clear", user=user)
