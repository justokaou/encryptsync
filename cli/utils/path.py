from pathlib import Path
import shutil
import os

def get_paths(mode):
    python_bin = shutil.which("python3")
    venv_bin = os.path.dirname(python_bin) if "VIRTUAL_ENV" in os.environ else "/usr/bin"

    if mode == "1":  # Dev
        project_path = Path(__file__).resolve().parent.parent.parent
        config_path = project_path / "config.yaml"
    else:
        project_path = Path("/usr/lib/encryptsync") if Path("/usr/lib/encryptsync").exists() else Path("/opt/encryptsync")
        config_path = Path("/etc/encryptsync/config.yaml")

    return {
        "project_path": str(project_path),
        "python": python_bin,
        "venv_bin": venv_bin,
        "config_path": str(config_path),
    }
