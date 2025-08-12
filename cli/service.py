# cli/service.py
# Queue/dispatcher-based control helpers for systemd --user integration.
# We DO NOT call `systemctl --user start/stop encryptsync@<SID>` directly.
# Instead, we:
#   1) drop a marker into %t/encryptsync (open-<SID> / close-<SID>)
#   2) trigger the dispatcher oneshot service
# The dispatcher is the only component that starts/stops the instances.

import os
from pathlib import Path
from typing import List

from utils.logger import get_logger

# generic systemd --user helpers
from cli.utils.service import (
    run_userctl,
    is_unit_active,
    is_unit_enabled,
    list_instances,
    units_to_sids,
)

logger = get_logger("encryptsync-cli")

# --- UI colors for simple status lines ---------------------------------------
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# --- Unit names / patterns ----------------------------------------------------
WATCHER_UNITS: tuple[str, str] = ("encryptsync-queue.path", "encryptsync-dispatch.timer")
DISPATCH_UNIT: str = "encryptsync-dispatch.service"

# --- Queue helpers ------------------------------------------------------------
def _queue_dir() -> Path:
    """
    Resolve the per-user runtime queue directory: %t/encryptsync
    (%t == $XDG_RUNTIME_DIR or /run/user/<uid>)
    """
    uid = os.getuid()
    xdg = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    q = Path(xdg) / "encryptsync"
    q.mkdir(parents=True, exist_ok=True)
    return q


def dispatch_now() -> None:
    """Trigger the dispatcher oneshot to process the queue immediately."""
    run_userctl("start", DISPATCH_UNIT)


def session_start(sid: str) -> bool:
    """
    Request start of the per-session instance via the queue.
    The dispatcher will start encryptsync@<sid> and encryptsync-clear@<sid>.
    """
    (_queue_dir() / f"open-{sid}").touch()
    dispatch_now()
    return True


def session_stop(sid: str) -> bool:
    """
    Request stop of the per-session instance via the queue.
    The dispatcher will stop encryptsync@<sid> and encryptsync-clear@<sid>.
    """
    (_queue_dir() / f"close-{sid}").touch()
    dispatch_now()
    return True


def is_instance_active(sid: str) -> bool:
    """Check if encryptsync@<sid>.service is currently active."""
    return is_unit_active(f"encryptsync@{sid}.service")


def restart_session(sid: str) -> bool:
    """
    Idempotent restart of the current session instance through the queue:
    - if active, request stop
    - then request start
    """
    if is_instance_active(sid):
        session_stop(sid)
    return session_start(sid)


def restart_all_sessions() -> bool:
    """
    Restart all active session instances via the queue/dispatcher.
    """
    ok = True
    for sid in units_to_sids(list_instances("encryptsync@*.service")):
        ok &= restart_session(sid)
    return ok


def watcher_enable(enable: bool, start_now: bool = True) -> bool:
    """
    Enable/disable the queue watcher (.path) and the safety-net (.timer).
    This replaces the old 'enable/start encryptsync*' behavior.
    """
    cmd = "enable" if enable else "disable"
    ok = run_userctl(cmd, *WATCHER_UNITS).returncode == 0
    if enable and start_now:
        # Start both the .path and the .timer (idempotent)
        run_userctl("start", *WATCHER_UNITS)
    return ok


# --- Pretty status printing ---------------------------------------------------
def _print_enabled(unit: str, label: str | None = None) -> None:
    label = label or unit
    status = f"{GREEN}[enabled]{RESET}" if is_unit_enabled(unit) else f"{RED}[disabled]{RESET}"
    logger.info(f"{label:<28}: {status}")


def _print_active(unit: str, label: str | None = None) -> None:
    label = label or unit
    status = f"{GREEN}[ok]{RESET}" if is_unit_active(unit) else f"{RED}[down]{RESET}"
    logger.info(f"{label:<28}: {status}")


def status_cmd() -> None:
    """
    Show watcher/timer state and the list of currently running instances.
    """
    # Watchers (triggers)
    _print_active("encryptsync-queue.path",    "queue.path active")
    _print_enabled("encryptsync-queue.path",   "queue.path enabled")
    _print_active("encryptsync-dispatch.timer","dispatch.timer active")
    _print_enabled("encryptsync-dispatch.timer","dispatch.timer enabled")

    # Active instances
    inst = list_instances("encryptsync@*.service")
    if inst:
        logger.info("instances:")
        for u in inst:
            logger.info(f"  - {u}")
    else:
        logger.info("instances: (none)")


# --- Back-compat shim (for older callers) ------------------------------------
def enable_services() -> bool:
    """
    Legacy entry point used by older code paths.
    Now maps to enabling the watcher + timer (user units).
    """
    return watcher_enable(True, start_now=True)


def systemctl_cmd(action: str, service: str = "encryptsync") -> bool:
    """
    Legacy shim to avoid breaking imports.
    We no longer control encryptsync@*.service directly from the CLI here.
    Supported:
      - enable/disable -> watcher_enable()
      - start (only for 'dispatch') -> dispatch_now()
      - status -> status_cmd()
    """
    if action in {"enable", "disable"}:
        return watcher_enable(action == "enable", start_now=(action == "enable"))
    if action == "start" and service == "dispatch":
        dispatch_now()
        return True
    if action == "status":
        status_cmd()
        return True
    logger.error(f"[{action}] unsupported direct systemctl on '{service}' with queue/dispatcher model")
    return False


def print_service_status(service: str, label: str | None = None) -> None:
    """
    Legacy function kept for older callers.
    For encryptsync/encryptsync-clear, we display watcher/timer + instances.
    """
    if service in {"encryptsync", "encryptsync-clear"}:
        status_cmd()
    else:
        _print_active(service, label)


def print_service_enabled(service: str, label: str | None = None) -> None:
    """
    Legacy function kept for older callers.
    For dynamic templates (@), "enabled" is meaningless; report watchers instead.
    """
    if service in {"encryptsync", "encryptsync-clear"}:
        _print_enabled("encryptsync-queue.path",     "queue.path enabled")
        _print_enabled("encryptsync-dispatch.timer", "dispatch.timer enabled")
    else:
        _print_enabled(service, label)
