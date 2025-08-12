import os
import subprocess
from pathlib import Path

from utils.hash import file_sha256
from utils.logger import get_logger

from cli.service import restart_session
from cli.utils.path import get_paths
from cli.utils.mode import ask_mode
from cli.utils.system import current_session_id

logger = get_logger("encryptsync-cli")

def edit(paths=None, context=None, restart=True):
    mode = None
    if paths is None:
        mode = ask_mode()
        paths = get_paths(mode)

    cfg = Path(paths["config_path"])
    if not cfg.exists():
        logger.critical(f"[edit] Config file not found at {cfg}.")
        return

    hash_before = file_sha256(cfg)
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, str(cfg)])
    hash_after = file_sha256(cfg)

    if not restart or context == "install":
        return

    if hash_before == hash_after:
        logger.info(f"[edit] Config unchanged. No restart needed.")
        return

    if mode == "1":
        logger.info(f"[edit] Config updated at {cfg}. Please restart the foreground program.")
        return

    sid = current_session_id()
    if not sid:
        logger.warning("[edit] Config changed but no session id found; it will apply on next login.")
        return

    logger.info(f"[edit] Config updated at {cfg}. Restarting daemon for current session (@{sid})...")
    ok = restart_session(sid)
    if ok:
        logger.info("[edit] Restart request dispatched.")
    else:
        logger.error("[edit] Restart failed to dispatch.")
