# cli/service.py
import os
import subprocess
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("encryptsync-cli")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

WATCHER_UNITS = ("encryptsync-queue.path", "encryptsync-dispatch.timer")
DISPATCH_UNIT = "encryptsync-dispatch.service"
INSTANCE_GLOB = "encryptsync@*.service"

def _userctl(*args, check=False, quiet=True):
    kw = {}
    if quiet:
        kw["stdout"] = subprocess.DEVNULL
        kw["stderr"] = subprocess.DEVNULL
    return subprocess.run(["systemctl", "--user", *args], check=check, **kw)

def _is_enabled(unit: str) -> bool:
    return _userctl("is-enabled", unit).returncode == 0

def _is_active(unit: str) -> bool:
    return _userctl("is-active", unit).returncode == 0

def _queue_dir() -> Path:
    uid = os.getuid()
    xdg = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    q = Path(xdg) / "encryptsync"
    q.mkdir(parents=True, exist_ok=True)
    return q

def dispatch_now() -> None:
    _userctl("start", DISPATCH_UNIT)

def session_start(sid: str) -> bool:
    (_queue_dir() / f"open-{sid}").touch()
    dispatch_now()
    return True  # le dispatcher démarre l'instance

def session_stop(sid: str) -> bool:
    (_queue_dir() / f"close-{sid}").touch()
    dispatch_now()
    return True

def watcher_enable(enable: bool, start_now: bool = True) -> bool:
    cmd = "enable" if enable else "disable"
    ok = _userctl(cmd, *WATCHER_UNITS).returncode == 0
    if enable and start_now:
        _userctl("start", *WATCHER_UNITS)
    return ok

def list_instances() -> list[str]:
    out = subprocess.run(
        ["systemctl", "--user", "--plain", "--no-legend", "--no-pager", "list-units", INSTANCE_GLOB],
        capture_output=True, text=True
    )
    if out.returncode != 0 or not out.stdout.strip():
        return []
    return [line.split()[0] for line in out.stdout.strip().splitlines()]

# ---- Affichage (status) -----------------------------------------------------

def print_enabled(unit: str, label: str | None = None):
    label = label or unit
    status = f"{GREEN}[enabled]{RESET}" if _is_enabled(unit) else f"{RED}[disabled]{RESET}"
    logger.info(f"{label:<28}: {status}")

def print_active(unit: str, label: str | None = None):
    label = label or unit
    status = f"{GREEN}[ok]{RESET}" if _is_active(unit) else f"{RED}[down]{RESET}"
    logger.info(f"{label:<28}: {status}")

def status_cmd():
    # Watchers (déclencheurs)
    print_active("encryptsync-queue.path",   "queue.path active")
    print_enabled("encryptsync-queue.path",  "queue.path enabled")
    print_active("encryptsync-dispatch.timer","dispatch.timer active")
    print_enabled("encryptsync-dispatch.timer","dispatch.timer enabled")

    # Instances en cours
    inst = list_instances()
    if inst:
        logger.info("instances:")
        for u in inst:
            logger.info(f"  - {u}")
    else:
        logger.info("instances: (none)")

# Back-compat (si du code appelle encore ces noms) ----------------------------

def enable_services() -> bool:
    # ancien comportement “enable/start encryptsync*” remplacé par l’activation des watchers
    return watcher_enable(True, start_now=True)

def systemctl_cmd(action: str, service: str = "encryptsync") -> bool:
    # ne pilote plus les templates @ ; on expose juste enable/disable/start/stop pour watchers/dispatch
    if action in {"enable", "disable"}:
        return watcher_enable(action == "enable", start_now=(action == "enable"))
    if action == "start" and service == "dispatch":
        dispatch_now(); return True
    if action == "status":
        status_cmd(); return True
    logger.error(f"[{action}] unsupported direct systemctl on '{service}' with queue/dispatcher model")
    return False

def print_service_status(service: str, label: str | None = None):
    # redirige vers watchers; pour les instances, utiliser status_cmd()
    if service in {"encryptsync", "encryptsync-clear"}:
        status_cmd()
    else:
        print_active(service, label)

def print_service_enabled(service: str, label: str | None = None):
    if service in {"encryptsync", "encryptsync-clear"}:
        # ceux-ci sont dynamiques; on montre les watchers à la place
        print_enabled("encryptsync-queue.path",  "queue.path enabled")
        print_enabled("encryptsync-dispatch.timer", "dispatch.timer enabled")
    else:
        print_enabled(service, label)