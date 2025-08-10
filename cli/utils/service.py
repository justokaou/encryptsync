import subprocess
import time
from typing import Optional
from cli.utils.mode import auto_detect_user_mode
from cli.utils.system import current_session_id

def _unit(name: str) -> str:
    # accept "encryptsync", "encryptsync@SID"
    return name if name.endswith(".service") else f"{name}.service"

def _resolve_user(user: Optional[bool]) -> bool:
    # None => auto-detect; True/False => respect
    return auto_detect_user_mode() if user is None else user

def _systemctl_base(user: Optional[bool]):
    eff_user = _resolve_user(user)
    return (["systemctl", "--user"] if eff_user else ["systemctl"]), eff_user

def unit_name(base: str, user_scope: bool) -> str:
    if user_scope:
        sid = current_session_id()
        return f"{base}@{sid}.service"
    return f"{base}.service"

def is_service_running(service_name: str = "encryptsync", user: Optional[bool] = None) -> bool:
    cmd, _ = _systemctl_base(user)
    rc = subprocess.run(cmd + ["is-active", "--quiet", _unit(service_name)]).returncode
    return rc == 0

def is_service_enabled(service_name: str = "encryptsync", user: Optional[bool] = None) -> bool:
    cmd, _ = _systemctl_base(user)
    rc = subprocess.run(cmd + ["is-enabled", "--quiet", _unit(service_name)]).returncode
    return rc == 0

def wait_active(service_name: str, user: Optional[bool] = None, timeout: float = 15.0, interval: float = 0.3) -> bool:
    cmd, _ = _systemctl_base(user)
    deadline = time.time() + timeout
    unit = _unit(service_name)
    while time.time() < deadline:
        if subprocess.run(cmd + ["is-active", "--quiet", unit]).returncode == 0:
            return True
        time.sleep(interval)
    return False

def is_active_or_exited(service_name: str, user: Optional[bool] = None) -> bool:
    cmd, _ = _systemctl_base(user)
    unit = _unit(service_name)
    out = subprocess.run(cmd + ["show", unit, "-p", "Type,ActiveState,SubState", "--value"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return False
    vals = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    try:
        typ, active, sub = vals
    except ValueError:
        return False
    if typ == "oneshot":
        return is_service_enabled(service_name, user=user)
    return active == "active"