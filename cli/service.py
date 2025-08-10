import subprocess, os
from utils.logger import get_logger
from cli.utils.service import is_service_running, is_service_enabled
from cli.utils.mode import auto_detect_user_mode
from cli.utils.system import unit_name  # ajout pour récupérer nom complet avec SID

logger = get_logger("encryptsync-cli")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def systemctl_cmd(action, service="encryptsync", user=None):
    if user is None:
        user = auto_detect_user_mode()

    full_service = unit_name(service, user_scope=user)

    if action in {"start","stop","restart","enable","disable"} and not user and os.geteuid() != 0:
        logger.error(f"[{action}] You must run this command as root (or with sudo) to {action} a system-wide service.")
        return False

    cmd = ["systemctl", "--user"] if user else ["systemctl"]
    cmd += [action, full_service]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"[{action}] {full_service} {action}ed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[{action}] Failed to {action} {full_service}: {e}")
        return False

def print_service_enabled(service: str, label: str = None, user=None):
    if user is None:
        user = auto_detect_user_mode()
    full_service = unit_name(service, user_scope=user)
    label = label or full_service
    status = f"{GREEN}[enabled]{RESET}" if is_service_enabled(full_service, user=user) else f"{RED}[disabled]{RESET}"
    logger.info(f"{label:<20}: {status}")

def print_service_status(service: str, label: str = None, user=None):
    if user is None:
        user = auto_detect_user_mode()
    full_service = unit_name(service, user_scope=user)
    label = label or full_service
    status = f"{GREEN}[ok]{RESET}" if is_service_running(full_service, user=user) else f"{RED}[down]{RESET}"
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

    bases = ["encryptsync", "encryptsync-clear"]
    ok = True

    for base in bases:
        unit = unit_name(base, user_scope=user)  # => encryptsync@<SID>.service in user
        if user:
            # PAM manage user services, so not needed to enable them
            ok &= systemctl_cmd("start", unit, user=user)
        else:
            ok &= systemctl_cmd("enable", unit, user=user)
            ok &= systemctl_cmd("start", unit, user=user)
    return ok
