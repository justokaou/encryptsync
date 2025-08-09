from pathlib import Path
import os

def get_paths(mode: str, user: bool = False):
    python_bin = "/usr/bin/python3"
    venv_bin = os.path.dirname(python_bin) if "VIRTUAL_ENV" in os.environ else "/usr/bin"
    home = Path.home()

    # Code path
    project_path = Path(__file__).resolve().parent.parent.parent if mode == "1" else Path("/usr/lib/encryptsync")

    # Config & logs
    if user:
        config_path = home / ".encryptsync" / "config.yaml"
        logs_path   = home / ".encryptsync" / "logs"
    else:
        config_path = Path("/etc/encryptsync/config.yaml")
        logs_path   = Path("/var/log/encryptsync")

    return {
        "project_path": str(project_path),
        "python": python_bin,
        "venv_bin": venv_bin,
        "config_path": str(config_path),
        "logs_path": str(logs_path),
    }
