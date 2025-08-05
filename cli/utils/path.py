from pathlib import Path
import os

from utils.logger import get_logger

logger = get_logger("encryptsync-cli")

def get_paths(mode, user=False):
    python_bin = "/usr/bin/python3"
    venv_bin = os.path.dirname(python_bin) if "VIRTUAL_ENV" in os.environ else "/usr/bin"

    home = Path.home()

    if user:
        config_path = home / ".encryptsync" / "config.yaml"
        systemd_user_path = home / ".config/systemd/user"

        if mode == "1":
            project_path = Path(__file__).resolve().parent.parent.parent
        else:
            project_path = Path("/usr/lib/encryptsync") if Path("/usr/lib/encryptsync").exists() else home / "opt/encryptsync"

    else:
        config_path = Path("/etc/encryptsync/config.yaml")
        systemd_user_path = Path("/etc/systemd/system")

        if mode == "1":
            project_path = Path(__file__).resolve().parent.parent.parent
        else:
            project_path = Path("/usr/lib/encryptsync") if Path("/usr/lib/encryptsync").exists() else Path("/opt/encryptsync")

    return {
        "project_path": str(project_path),
        "python": python_bin,
        "venv_bin": venv_bin,
        "config_path": str(config_path),
        "systemd_path": str(systemd_user_path),
    }