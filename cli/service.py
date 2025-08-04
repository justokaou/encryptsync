import subprocess, os
from pathlib import Path
from utils.logger import get_logger
from utils.system import is_systemd_available

logger = get_logger("encryptsync-cli")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def systemctl_cmd(action, service="encryptsync"):
    if action in {"start", "stop", "restart", "enable", "disable"} and os.geteuid() != 0:
        logger.error(f"[{action}] You must run this command as root (or with sudo) to {action} a service.")
        return
    
    try:
        subprocess.run(["systemctl", action, f"{service}.service"], check=True)
        logger.info(f"[{action}] {service}.service {action}ed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"[{action}] Failed to {action} {service}.service: {e}")

def print_service_enabled(service: str, label: str = None):
    label = label or service
    try:
        subprocess.run(
            ["systemctl", "is-enabled", "--quiet", f"{service}.service"],
            check=True
        )
        status = f"{GREEN}[enabled]{RESET}"
    except subprocess.CalledProcessError:
        status = f"{RED}[disabled]{RESET}"

    logger.info(f"{label:<20}: {status}")

def print_service_status(service: str, label: str = None):
    label = label or service
    try:
        subprocess.run(
            ["systemctl", "is-active", "--quiet", f"{service}.service"],
            check=True
        )
        status = f"{GREEN}[ok]{RESET}"
    except subprocess.CalledProcessError:
        status = f"{RED}[down]{RESET}"
    logger.info(f"{label:<20}: {status}")

def status_cmd():
    print_service_status("encryptsync", "encryptsync daemon")
    print_service_enabled("encryptsync-clear", "encryptsync-clear")

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

def uninstall_service(name):
    if os.geteuid() != 0:
        logger.error(f"[uninstall] You must run this command as root (or with sudo) to remove services files.")
        return

    subprocess.run(["systemctl", "disable", name], check=False)
    service_path = Path(f"/etc/systemd/system/{name}.service")
    if service_path.exists():
        service_path.unlink()
        logger.info(f"[uninstall] Removed {service_path}")
    else:
        logger.info(f"[uninstall] {name}.service not found. Skipping.")
