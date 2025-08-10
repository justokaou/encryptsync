import subprocess
from utils.logger import get_logger
from cli.utils.service import is_service_running, is_service_enabled, unit_name

logger = get_logger("encryptsync-cli")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def systemctl_cmd(action, service="encryptsync"):
    full_service = unit_name(service)
    cmd = ["systemctl", "--user", action, full_service]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"[{action}] {full_service} {action}ed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[{action}] Failed to {action} {full_service}: {e}")
        return False


def print_service_enabled(service: str, label: str = None):
    full_service = unit_name(service)
    label = label or full_service
    status = f"{GREEN}[enabled]{RESET}" if is_service_enabled(full_service) else f"{RED}[disabled]{RESET}"
    logger.info(f"{label:<20}: {status}")


def print_service_status(service: str, label: str = None):
    full_service = unit_name(service)
    label = label or full_service
    status = f"{GREEN}[ok]{RESET}" if is_service_running(full_service) else f"{RED}[down]{RESET}"
    logger.info(f"{label:<20}: {status}")


def status_cmd():
    for svc, label in [("encryptsync", "encryptsync daemon"),
                       ("encryptsync-clear", "encryptsync-clear")]:
        print_service_status(svc, label)
        print_service_enabled(svc, label)


def enable_services():
    bases = ["encryptsync", "encryptsync-clear"]
    ok = True
    for base in bases:
        ok &= systemctl_cmd("enable", base)
        ok &= systemctl_cmd("start", base)
    return ok