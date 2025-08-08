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
        systemd_path = home / ".config/systemd/user"
        project_path = (
            Path(__file__).resolve().parent.parent.parent
            if mode == "1"
            else Path("/usr/lib/encryptsync")
        )
    else:
        config_path = Path("/etc/encryptsync/config.yaml")
        systemd_path = Path("/lib/systemd/system")  # standard Debian systemd unit dir
        project_path = (
            Path(__file__).resolve().parent.parent.parent
            if mode == "1"
            else Path("/usr/lib/encryptsync")
        )

    return {
        "project_path": str(project_path),
        "python": python_bin,
        "venv_bin": venv_bin,
        "config_path": str(config_path),
        "systemd_path": str(systemd_path),
    }