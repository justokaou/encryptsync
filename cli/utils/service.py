import subprocess
import time
from typing import Optional
from cli.utils.mode import auto_detect_user_mode

def _resolve_user(user: Optional[bool]) -> bool:
    # None => auto-detect; True/False => respect
    return auto_detect_user_mode() if user is None else user

def _systemctl_base(user: Optional[bool]):
    eff_user = _resolve_user(user)
    return (["systemctl", "--user"] if eff_user else ["systemctl"]), eff_user

def is_service_running(service_name: str = "encryptsync", user: Optional[bool] = None) -> bool:
    cmd, _ = _systemctl_base(user)
    # avoid raising exceptions; just check returncode
    rc = subprocess.run(cmd + ["is-active", "--quiet", f"{service_name}.service"]).returncode
    return rc == 0

def is_service_enabled(service_name: str = "encryptsync", user: Optional[bool] = None) -> bool:
    cmd, _ = _systemctl_base(user)
    rc = subprocess.run(cmd + ["is-enabled", "--quiet", f"{service_name}.service"]).returncode
    return rc == 0

# Optionnel, utile après un "start" pour attendre vraiment l'état actif
def wait_active(service_name: str, user: Optional[bool] = None, timeout: float = 15.0, interval: float = 0.3) -> bool:
    cmd, _ = _systemctl_base(user)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if subprocess.run(cmd + ["is-active", "--quiet", f"{service_name}.service"]).returncode == 0:
            return True
        time.sleep(interval)
    return False

# Optionnel, si tu veux considérer les oneshot "réussis"
def is_active_or_exited(service_name: str, user: Optional[bool] = None) -> bool:
    cmd, _ = _systemctl_base(user)
    # systemctl show: ActiveState & SubState
    out = subprocess.run(cmd + ["show", f"{service_name}.service", "-p", "Type,ActiveState,SubState", "--value"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return False
    vals = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    # expected order: Type, ActiveState, SubState
    try:
        typ, active, sub = vals
    except ValueError:
        return False
    if typ == "oneshot":
        # oneshot is often 'inactive' with sub 'dead' after successful start; consider enabled success separately
        return is_service_enabled(service_name, user=user)
    return active == "active"