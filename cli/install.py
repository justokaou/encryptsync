import subprocess
import shutil
from pathlib import Path

from utils.logger import get_logger

from cli.edit import edit
from cli.service import enable_services

from cli.utils.path import get_paths
from cli.utils.mode import auto_detect_user_mode
from cli.utils.service import is_service_running, wait_active, is_service_enabled


logger = get_logger("encryptsync-cli")

def copy_default_config(project_path, config_path):
    dst = Path(config_path)
    src = Path(project_path) / "config.template.yaml"

    if dst.exists():
        logger.info(f"[install] Config already exists at {dst}. Skipping copy.")
        return
    if not src.exists():
        logger.critical(f"[install] ERROR: Missing template config at {src}")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    logger.info(f"[install] Default config copied from {src} to {dst}.")

def maybe_edit_config(paths, user=False):
    if input("Edit config now? [y/N]: ").lower() == "y":
        edit(paths, context="install", user=user)

def install(user: bool | None = None):
    """
    user = True  -> force user mode
    user = False -> force system mode
    user = None  -> auto-detect (XDG_RUNTIME_DIR && non-root => user, else system)
    """
    effective_user = auto_detect_user_mode() if user is None else user

    paths = get_paths("2", user=effective_user)

    copy_default_config(paths["project_path"], paths["config_path"])
    maybe_edit_config(paths, user=effective_user)

    # Reload des unités systemd
    if effective_user:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    else:
        subprocess.run(["systemctl", "daemon-reload"], check=False)

    ok_actions = enable_services(user=effective_user)

    daemon_ok = wait_active("encryptsync", user=effective_user, timeout=15)

    clear_ok = is_service_enabled("encryptsync-clear", user=effective_user)

    if daemon_ok and clear_ok and ok_actions:
        logger.info("Installation complete.")
    else:
        logger.error(
            "[install] Post-check failed: "
            f"daemon_ok={daemon_ok}, clear_enabled={clear_ok}, actions_ok={ok_actions}"
        )

