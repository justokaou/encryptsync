import subprocess, os
from utils.logger import get_logger
from cli.utils.service import is_service_running, is_service_enabled
from cli.utils.mode import auto_detect_user_mode

logger = get_logger("encryptsync-cli")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def systemctl_cmd(action, service="encryptsync", user=None):
    if user is None:
        user = auto_detect_user_mode()

    if action in {"start","stop","restart","enable","disable"} and not user and os.geteuid() != 0:
        logger.error(f"[{action}] You must run this command as root (or with sudo) to {action} a system-wide service.")
        return False

    cmd = ["systemctl", "--user"] if user else ["systemctl"]
    cmd += [action, f"{service}.service"]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"[{action}] {service}.service {action}ed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[{action}] Failed to {action} {service}.service: {e}")
        return False

def print_service_enabled(service: str, label: str = None, user=None):
    if user is None:
        user = auto_detect_user_mode()
    label = label or service
    status = f"{GREEN}[enabled]{RESET}" if is_service_enabled(service, user=user) else f"{RED}[disabled]{RESET}"
    logger.info(f"{label:<20}: {status}")

def print_service_status(service: str, label: str = None, user=None):
    if user is None:
        user = auto_detect_user_mode()
    label = label or service
    status = f"{GREEN}[ok]{RESET}" if is_service_running(service, user=user) else f"{RED}[down]{RESET}"
    logger.info(f"{label:<20}: {status}")

def status_cmd(user=None):
    if user is None:
        user = auto_detect_user_mode()
    for svc, label in [("encryptsync", "encryptsync daemon"),
                       ("encryptsync-clear", "encryptsync-clear")]:
        print_service_status(svc, label, user=user)
        print_service_enabled(svc, label, user=user)

def enable_services(user=None):
    if user is None:
        user = auto_detect_user_mode()
    services = ["encryptsync", "encryptsync-clear"]
    ok = True
    for s in services:
        ok &= systemctl_cmd("enable", s, user=user)
        ok &= systemctl_cmd("start", s, user=user)
    return ok