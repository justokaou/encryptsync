import os
import shutil
import subprocess
from pathlib import Path
from cli.templates.daemon import DAEMON_TEMPLATE
from cli.templates.clear import CLEAR_TEMPLATE
from utils.system import is_systemd_available
from utils.logger import get_logger
from cli.service import systemctl_cmd
from utils.hash import file_sha256

logger = get_logger("encryptsync-cli")

def is_deb_install():
    return Path("/usr/lib/encryptsync").exists()

def is_service_installed(name):
    return Path(f"/etc/systemd/system/{name}.service").exists()

def ask_mode(context=None):
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

def copy_default_config(project_path):
    dst = Path("/etc/encryptsync/config.yaml")
    src = Path(project_path) / "config.template.yaml"

    if dst.exists():
        logger.info("[install] Config already exists. Skipping default copy.")
        return
    if not src.exists():
        logger.critical("[install] ERROR: Missing template config at", src)
        return

    os.makedirs(dst.parent, exist_ok=True)
    shutil.copy(src, dst)
    logger.info(f"[install] Default config copied from {src} to {dst}.")

def edit(paths=None, context=None, restart=True):
    if paths is None:
        mode = ask_mode()
        paths = get_paths(mode)
    if not Path(paths["config_path"]).exists():
        logger.critical(f"[edit] Config file not found at {paths['config_path']}.")
        return
    hash_before = file_sha256(paths["config_path"])
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, paths["config_path"]])
    hash_after = file_sha256(paths["config_path"])
    if restart and context != "install":
        if hash_before != hash_after and mode != "1":
            logger.info(f"[edit] Config file edited at {paths['config_path']}. Restarting daemon service...")
            systemctl_cmd("restart", "encryptsync")
        elif mode == "1" and hash_before != hash_after:
            logger.info(f"[edit] Config file at {paths['config_path']} edited. You need to restart the program.")
        else:
            logger.info(f"[edit] Config file at {paths['config_path']} has not changed. No restart needed.")


def maybe_edit_config(paths):
    if input("Edit config now? [y/N]: ").lower() == "y":
        edit(paths, context="install")

def copy_project_if_needed(mode, target_path):
    if mode == "2":
        if target_path == "/usr/lib/encryptsync":
            logger.info("[install] Detected system install via .deb — skipping project copy.")
            return

        if Path(target_path).exists():
            choice = input(f"[install] Project already exists at {target_path}. Overwrite? [y/N]: ").strip().lower()
            if choice == "y":
                shutil.rmtree(target_path)
                logger.info(f"[install] Removed existing directory: {target_path}")
            else:
                logger.info("[install] Skipping project copy.")
                return

        logger.info(f"[install] Copying project to {target_path}...")
        shutil.copytree(Path(__file__).resolve().parent.parent, target_path)

def install_service(name, content):
    if not is_systemd_available():
        logger.warning("[error] Systemd not detected. Service installation may fail.")
        if input("Proceed anyway? [y/N]: ").strip().lower() != "y":
            return
    
    if os.geteuid() != 0:
        logger.warning("You must run this installer as root to install systemd services.")
        return
    
    log_dir = Path("/var/log/encryptsync")
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
        logger.info("[install] Created log directory at /var/log/encryptsync")

    path = f"/etc/systemd/system/{name}.service"
    with open(path, "w") as f:
        f.write(content)
    subprocess.run(["systemctl", "daemon-reexec"], check=True)
    subprocess.run(["systemctl", "enable", name], check=True)
    subprocess.run(["systemctl", "start", name], check=True)
    logger.info(f"[install] {name} service installed and started.")

def maybe_install_service(name, template, paths, force=False):
    service_path = Path(f"/etc/systemd/system/{name}.service")

    if is_service_installed(name) and not force:
        logger.info(f"[install] {name}.service already installed. Skipping.")
        return

    if force:
        logger.info(f"[install] Forcing reinstallation of {name}.service...")
        if service_path.exists():
            service_path.unlink()
            logger.info(f"[install] Removed existing {name}.service before reinstalling.")
    else:
        confirm = input(f"Install {name} service? [y/N]: ").lower()
        if confirm != "y":
            logger.info(f"[install] Skipping {name}.service.")
            return

    install_service(name, template.format(**paths))

def install(force=False):
    if is_deb_install():
        mode = "2"
    else:
        mode = ask_mode("install")

    paths = get_paths(mode)
    copy_project_if_needed(mode, paths["project_path"])

    if mode == "2":
        copy_default_config(paths["project_path"])

    maybe_edit_config(paths)

    maybe_install_service("encryptsync", DAEMON_TEMPLATE, paths, force)
    maybe_install_service("encryptsync-clear", CLEAR_TEMPLATE, paths, force)

    logger.info("Installation complete.")