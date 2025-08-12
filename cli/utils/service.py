# cli/utils/service.py
# Low-level helpers for interacting with systemd --user.
# These utilities are generic and do not encode EncryptSync-specific logic,
# so they can be reused by higher-level modules.

import subprocess
import time
from typing import List


def run_userctl(*args: str, check: bool = False, quiet: bool = True) -> subprocess.CompletedProcess:
    """
    Run `systemctl --user ...`.
    - quiet=True: suppress stdout/stderr (good for probes like is-active/is-enabled).
    - check=True: raise CalledProcessError on non-zero return code.
    """
    kw = {}
    if quiet:
        kw["stdout"] = subprocess.DEVNULL
        kw["stderr"] = subprocess.DEVNULL
    return subprocess.run(["systemctl", "--user", *args], check=check, **kw)


def is_unit_active(unit: str) -> bool:
    """Return True if the given user unit is currently active."""
    return run_userctl("is-active", unit).returncode == 0


def is_unit_enabled(unit: str) -> bool:
    """Return True if the given user unit is enabled."""
    return run_userctl("is-enabled", unit).returncode == 0


def wait_unit_active(unit: str, timeout: float = 15.0, interval: float = 0.3) -> bool:
    """
    Wait until a user unit is active, up to `timeout` seconds.
    Returns True if it became active, False on timeout.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_unit_active(unit):
            return True
        time.sleep(interval)
    return False


def list_units(glob: str) -> List[str]:
    """
    Return the list of user unit names matching `glob` (e.g. 'encryptsync@*.service').
    """
    out = subprocess.run(
        ["systemctl", "--user", "--plain", "--no-legend", "--no-pager", "list-units", glob],
        capture_output=True, text=True
    )
    if out.returncode != 0 or not out.stdout.strip():
        return []
    return [line.split()[0] for line in out.stdout.strip().splitlines()]


def list_instances(pattern: str = "encryptsync@*.service") -> List[str]:
    """
    Convenience wrapper to list EncryptSync instance unit names.
    """
    return list_units(pattern)


def units_to_sids(units: List[str]) -> List[str]:
    """
    Extract <SID> from instance unit names: 'encryptsync@<SID>.service' -> '<SID>'.
    """
    sids: List[str] = []
    for u in units:
        if u.startswith("encryptsync@") and u.endswith(".service"):
            sids.append(u[len("encryptsync@"):-len(".service")])
    return sids
