import subprocess
from cli.utils.mode import auto_detect_user_mode

def _systemctl_base(user: bool):
    return ["systemctl", "--user"] if user else ["systemctl"]

def is_service_running(service_name="encryptsync", user=None):
    cmd = ["systemctl"]

    # mode auto-detect 
    if user is None:
        # If $XDG_RUNTIME_DIR is defined and user isn't root, we suppose it's a user service
        user = auto_detect_user_mode()

    if user:
        cmd.append("--user")

    cmd += ["is-active", "--quiet", f"{service_name}.service"]

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_service_enabled(service_name="encryptsync", user: bool = False) -> bool:
    try:
        subprocess.run(_systemctl_base(user) + ["is-enabled", "--quiet", f"{service_name}.service"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
