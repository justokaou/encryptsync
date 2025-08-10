import subprocess
import shutil
from pathlib import Path

from utils.logger import get_logger

from cli.edit import edit
from cli.service import enable_services

from cli.utils.path import get_paths
from cli.utils.mode import auto_detect_user_mode
from cli.utils.service import is_service_running, wait_active, is_service_enabled
from cli.utils.system import current_session_id

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
    effective_user = auto_detect_user_mode() if user is None else user
    paths = get_paths("2", user=effective_user)

    copy_default_config(paths["project_path"], paths["config_path"])
    maybe_edit_config(paths, user=effective_user)

    # reload
    subprocess.run(["systemctl","--user" if effective_user else "", "daemon-reload"][0:2 if effective_user else 1], check=False)

    if effective_user:
        sid = current_session_id()
        subprocess.run(["systemctl","--user","start", f"encryptsync@{sid}.service",
                                                   f"encryptsync-clear@{sid}.service"], check=False)

        daemon_ok = wait_active(f"encryptsync@{sid}", user=True, timeout=15)
        clear_ok  = is_service_enabled("encryptsync-clear", user=True)
        ok_actions = True
    else:
        ok_actions = enable_services(user=False)
        daemon_ok = wait_active(f"encryptsync@{sid}", user=False, timeout=15)
        clear_ok  = is_service_enabled(f"encryptsync-clear@{sid}", user=False)

    if daemon_ok and ok_actions:
        logger.info("Installation complete.")
    else:
        logger.error("[install] Post-check failed")

