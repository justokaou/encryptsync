import subprocess
import time
from cli.utils.system import current_session_id


def _unit(name: str) -> str:
    # accept "encryptsync", "encryptsync@SID"
    return name if name.endswith(".service") else f"{name}.service"


def unit_name(base: str) -> str:
    # Always user scope with a session-bound instance
    sid = current_session_id()
    return f"{base}@{sid}.service"


def is_service_running(service_name: str = "encryptsync") -> bool:
    rc = subprocess.run(["systemctl", "--user", "is-active", "--quiet", _unit(service_name)]).returncode
    return rc == 0


def is_service_enabled(service_name: str = "encryptsync") -> bool:
    rc = subprocess.run(["systemctl", "--user", "is-enabled", "--quiet", _unit(service_name)]).returncode
    return rc == 0


def wait_active(service_name: str, timeout: float = 15.0, interval: float = 0.3) -> bool:
    deadline = time.time() + timeout
    unit = _unit(service_name)
    while time.time() < deadline:
        if subprocess.run(["systemctl", "--user", "is-active", "--quiet", unit]).returncode == 0:
            return True
        time.sleep(interval)
    return False


def is_active_or_exited(service_name: str) -> bool:
    unit = _unit(service_name)
    out = subprocess.run(
        ["systemctl", "--user", "show", unit, "-p", "Type,ActiveState,SubState", "--value"],
        capture_output=True, text=True
    )
    if out.returncode != 0:
        return False
    vals = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    try:
        typ, active, sub = vals
    except ValueError:
        return False
    if typ == "oneshot":
        return is_service_enabled(service_name)
    return active == "active"