import subprocess, os
from utils.logger import get_logger

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