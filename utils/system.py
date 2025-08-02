import shutil
from pathlib import Path
import platform
import os

def is_systemd_available():
    # Must be a Linux system
    if platform.system() != "Linux":
        return False

    # Must be PID 1 and actually running systemd
    try:
        with open("/proc/1/comm") as f:
            if f.read().strip() != "systemd":
                return False
    except FileNotFoundError:
        return False

    # systemctl must be available and systemd socket present
    return shutil.which("systemctl") is not None and Path("/run/systemd/system").exists()
