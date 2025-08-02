import os
import shutil
import subprocess
from pathlib import Path
from cli.templates.daemon import DAEMON_TEMPLATE
from cli.templates.clear import CLEAR_TEMPLATE
from utils.system import is_systemd_available

def is_deb_install():
    return Path("/usr/lib/encryptsync").exists()

def is_service_installed(name):
    return Path(f"/etc/systemd/system/{name}.service").exists()

def ask_mode(context="install"):
    print("Choose mode:")
    print("1) Development (current path)")
    if context == "install":
        print("2) System (recommended: install to /opt/encryptsync)")
    else:
        print("2) System (installed via .deb or /opt)")

    choice = input("Choice [1/2]? ").strip()
    return choice if choice in {"1", "2"} else "1"

def get_paths(mode):
    python_bin = shutil.which("python3")
    venv_bin = os.path.dirname(python_bin) if "VIRTUAL_ENV" in os.environ else "/usr/bin"

    if mode == "1":  # Dev
        project_path = Path(__file__).resolve().parent.parent
        config_path = project_path / "config.yaml"
    else:  # System mode (deb or /opt)
        project_path = Path("/usr/lib/encryptsync") if Path("/usr/lib/encryptsync").exists() else Path("/opt/encryptsync")
        config_path = Path("/etc/encryptsync/config.yaml")

    return {
        "project_path": str(project_path),
        "python": python_bin,
        "venv_bin": venv_bin,
        "config_path": str(config_path),
    }

def copy_default_config():
    dst = Path("/etc/encryptsync/config.yaml")
    src = Path("/usr/lib/encryptsync/config.template.yaml")

    if dst.exists():
        print("[install] Config already exists. Skipping default copy.")
        return
    if not src.exists():
        print("[install] ERROR: Missing template config at", src)
        return
    
    if not dst.exists() and src.exists():
        os.makedirs(dst.parent, exist_ok=True)
        shutil.copy(src, dst)
        print("[install] Default config copied to /etc/encryptsync/config.yaml")

def edit(paths=None):
    if paths is None:
        mode = ask_mode()
        paths = get_paths(mode)
    if not Path(paths["config_path"]).exists():
        print(f"[edit] Config file not found at {paths['config_path']}.")
        return
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, paths["config_path"]])

def maybe_edit_config(paths):
    if input("Edit config now? [y/N]: ").lower() == "y":
        edit(paths)

def copy_project_if_needed(mode, target_path):
    if mode == "2":
        if target_path == "/usr/lib/encryptsync":
            print("[install] Detected system install via .deb — skipping project copy.")
            return

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
    if not is_systemd_available():
        print("[error] Systemd not detected. Service installation may fail.")
        if input("Proceed anyway? [y/N]: ").strip().lower() != "y":
            return
    
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

def maybe_install_service(name, template, paths):
    if not is_service_installed(name):
        if input(f"Install {name} service? [y/N]: ").lower() == "y":
            install_service(name, template.format(**paths))
    else:
        print(f"[install] {name}.service already installed. Skipping.")

def install():
    if is_deb_install():
        mode = "2"
    else:
        mode = ask_mode("install")

    paths = get_paths(mode)
    copy_project_if_needed(mode, paths["project_path"])

    if mode == "2":
        copy_default_config()

    maybe_edit_config(paths)

    maybe_install_service("encryptsync", DAEMON_TEMPLATE, paths)
    maybe_install_service("encryptsync-clear", CLEAR_TEMPLATE, paths)

    print("Installation complete.")