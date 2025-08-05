from pathlib import Path
import os, sys

from utils.logger import get_logger

logger = get_logger("encryptsync-cli")

def get_paths(mode, user=False):
    python_bin = "/usr/bin/python3"
    venv_bin = os.path.dirname(python_bin) if "VIRTUAL_ENV" in os.environ else "/usr/bin"

    if user:
        home = Path.home()
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
        state_home = Path(os.environ.get("XDG_STATE_HOME", home / ".local/state"))
        log_path = state_home / "encryptsync"
        systemd_user_path = home / ".config/systemd/user"
        config_path = config_home / "encryptsync" / "config.yaml"

        if mode == "1":
            project_path = Path(__file__).resolve().parent.parent.parent
        else:
            # If project already install via .deb
            if Path("/usr/lib/encryptsync").exists():
                project_path = Path("/usr/lib/encryptsync")
            else:
                # else, we install it in ~/opt/encryptsync
                project_path = home / "opt/encryptsync"

    else:
        config_path = Path("/etc/encryptsync/config.yaml")
        log_path = Path("/var/log/encryptsync")
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
        "log_path": str(log_path),
        "user_state_dir": str(log_path),
        "systemd_path": str(systemd_user_path),
    }