import os
import shutil
import subprocess
from pathlib import Path
from cli.templates.daemon import DAEMON_TEMPLATE
from cli.templates.clear import CLEAR_TEMPLATE

def ask_mode():
    print("Install mode:")
    print("1) Development (current path)")
    print("2) System (recommended: install to /opt/encryptsync)")
    choice = input("Choice [1/2]? ").strip()
    return choice if choice in {"1", "2"} else "1"

def get_paths(mode):
    python_bin = shutil.which("python3")
    venv_bin = os.path.dirname(python_bin) if "VIRTUAL_ENV" in os.environ else "/usr/bin"

    if mode == "1":  # Dev
        project_path = Path(__file__).resolve().parent.parent
    else:  # System mode (deb or /opt install)
        # Check if installed with .deb (standard debian path)
        deb_path = Path("/usr/lib/encryptsync")
        opt_path = Path("/opt/encryptsync")

        if deb_path.exists():
            project_path = deb_path
        else:
            project_path = opt_path  # fallback

    return {
        "project_path": str(project_path),
        "python": python_bin,
        "venv_bin": venv_bin,
    }

def copy_project_if_needed(mode, target_path):
    if mode == "2":
        if Path(target_path).exists():
            choice = input(f"[install] Project already exists at {target_path}. Overwrite? [y/N]: ").strip().lower()
            if choice == "y":
                shutil.rmtree(target_path)
                print(f"[install] Removed existing directory: {target_path}")
            else:
                print("[install] Skipping project copy.")
                return
        print(f"[install] Copying project to {target_path}...")
        shutil.copytree(Path(__file__).resolve().parent.parent, target_path)

def install_service(name, content):
    if os.geteuid() != 0:
        print("You must run this installer as root to install systemd services.")
        return

    path = f"/etc/systemd/system/{name}.service"
    with open(path, "w") as f:
        f.write(content)
    subprocess.run(["systemctl", "daemon-reexec"], check=True)
    subprocess.run(["systemctl", "enable", name], check=True)
    subprocess.run(["systemctl", "start", name], check=True)
    print(f"[install] {name} service installed and started.")

def install():
    mode = ask_mode()
    paths = get_paths(mode)
    copy_project_if_needed(mode, paths["project_path"])

    if input("Install EncryptedSync daemon? [y/N]: ").lower() == "y":
        install_service("encryptsync", DAEMON_TEMPLATE.format(**paths))

    if input("Install clear-plain service on shutdown? [y/N]: ").lower() == "y":
        install_service("encryptsync-clear", CLEAR_TEMPLATE.format(**paths))

    print("Installation complete.")
