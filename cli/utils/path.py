from pathlib import Path
import os

def get_paths(mode: str):
    python_bin = "/usr/bin/python3"
    venv_bin = os.path.dirname(python_bin) if "VIRTUAL_ENV" in os.environ else "/usr/bin"
    home = Path.home()

    # Code path
    project_path = Path(__file__).resolve().parent.parent.parent if mode == "1" else Path("/usr/lib/encryptsync")

    config_path = home / ".encryptsync" / "config.yaml"
    logs_path   = home / ".encryptsync" / "logs"

    return {
        "project_path": str(project_path),
        "python": python_bin,
        "venv_bin": venv_bin,
        "config_path": str(config_path),
        "logs_path": str(logs_path),
    }
