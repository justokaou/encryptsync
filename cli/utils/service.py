import subprocess

def _systemctl_base(user: bool):
    return ["systemctl", "--user"] if user else ["systemctl"]

def is_service_running(service_name="encryptsync", user: bool = False) -> bool:
    try:
        subprocess.run(_systemctl_base(user) + ["is-active", "--quiet", f"{service_name}.service"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_service_enabled(service_name="encryptsync", user: bool = False) -> bool:
    try:
        subprocess.run(_systemctl_base(user) + ["is-enabled", "--quiet", f"{service_name}.service"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
