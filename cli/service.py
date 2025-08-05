import subprocess, os
from pathlib import Path
from utils.logger import get_logger
from utils.system import is_systemd_available

logger = get_logger("encryptsync-cli")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def systemctl_cmd(action, service="encryptsync", user=False):
    if action in {"start", "stop", "restart", "enable", "disable"} and not user and os.geteuid() != 0:
        logger.error(f"[{action}] You must run this command as root (or with sudo) to {action} a system-wide service.")
        return

    cmd = ["systemctl"]
    if user:
        cmd.append("--user")
    cmd += [action, f"{service}.service"]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"[{action}] {service}.service {action}ed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"[{action}] Failed to {action} {service}.service: {e}")

def print_service_enabled(service: str, label: str = None, user: bool = False):
    label = label or service
    cmd = ["systemctl"]
    if user:
        cmd.append("--user")
    cmd += ["is-enabled", "--quiet", f"{service}.service"]

    try:
        subprocess.run(cmd, check=True)
        status = f"{GREEN}[enabled]{RESET}"
    except subprocess.CalledProcessError:
        status = f"{RED}[disabled]{RESET}"

    logger.info(f"{label:<20}: {status}")

def print_service_status(service: str, label: str = None, user: bool = False):
    label = label or service
    cmd = ["systemctl"]
    if user:
        cmd.append("--user")
    cmd += ["is-active", "--quiet", f"{service}.service"]

    try:
        subprocess.run(cmd, check=True)
        status = f"{GREEN}[ok]{RESET}"
    except subprocess.CalledProcessError:
        status = f"{RED}[down]{RESET}"

    logger.info(f"{label:<20}: {status}")

def status_cmd(user: bool = False):
    print_service_status("encryptsync", "encryptsync daemon", user=user)
    print_service_enabled("encryptsync-clear", "encryptsync-clear", user=user)

def install_service(name, content, user=False):
    if not is_systemd_available():
        logger.warning("[error] Systemd not detected. Service installation may fail.")
        if input("Proceed anyway? [y/N]: ").strip().lower() != "y":
            return
    
    if not user and os.geteuid() != 0:
        logger.warning("You must run this installer as root to install system-wide services.")
        return
    
    if not user:
        log_dir = Path("/var/log/encryptsync")
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[install] Created log directory at /var/log/encryptsync")

    if user:
        path = Path.home() / ".config/systemd/user" / f"{name}.service"
        os.makedirs(path.parent, exist_ok=True)
    else:
        path = Path(f"/etc/systemd/system/{name}.service")

    with open(path, "w") as f:
        f.write(content)
    
    if user:
        subprocess.run(["systemctl", "--user", "daemon-reexec"], check=True)
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "--now", name], check=True)
    else:
        subprocess.run(["systemctl", "daemon-reexec"], check=True)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "--now", name], check=True)
    logger.info(f"[install] {name} service installed and started.")

def uninstall_service(name, user=False):
    if not user and os.geteuid() != 0:
        logger.error(f"[uninstall] You must run this command as root (or with sudo) to remove system-wide services.")
        return

    try:
        if user:
            subprocess.run(["systemctl", "--user", "stop", name], check=False)
            subprocess.run(["systemctl", "--user", "disable", name], check=False)
            service_path = Path.home() / ".config/systemd/user" / f"{name}.service"
        else:
            subprocess.run(["systemctl", "stop", name], check=False)
            subprocess.run(["systemctl", "disable", name], check=False)
            service_path = Path(f"/etc/systemd/system/{name}.service")

        if service_path.exists():
            service_path.unlink()
            logger.info(f"[uninstall] Removed {service_path}")
        else:
            logger.info(f"[uninstall] {name}.service not found. Skipping.")
    except Exception as e:
        logger.error(f"[uninstall] Failed to uninstall {name}: {e}")

