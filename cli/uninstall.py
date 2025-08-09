# cli/uninstall.py
import os
import shutil
from pathlib import Path

from utils.logger import get_logger
from cli.utils.mode import auto_detect_user_mode
from cli.utils.path import get_paths

logger = get_logger("encryptsync-cli")

def _rm(path: Path):
    try:
        if path.is_dir():
            shutil.rmtree(path)
            logger.info(f"[uninstall] Removed directory: {path}")
        elif path.exists():
            path.unlink()
            logger.info(f"[uninstall] Removed file: {path}")
        else:
            logger.info(f"[uninstall] Not found (skip): {path}")
        return True
    except Exception as e:
        logger.error(f"[uninstall] Failed to remove {path}: {e}")
        return False

def uninstall(user: bool | None = None, force: bool = False):
    """
    Remove EncryptSync configuration and logs.
    - user=True  : target user file path (~/.encryptsync/*)
    - user=False : target system file path (/etc/encryptsync, /var/log/encryptsync)
    - user=None  : auto-detect (user if XDG_RUNTIME_DIR and non-root, else system)
    - force=True : no interaction mode
    """
    effective_user = auto_detect_user_mode() if user is None else user

    paths = get_paths(mode="2", user=effective_user)
    config_path = Path(paths["config_path"])

    if effective_user:
        logs_dir = Path.home() / ".encryptsync" / "logs"
    else:
        logs_dir = Path("/var/log/encryptsync")

    targets = [config_path, logs_dir]

    logger.info("[uninstall] Targets to remove:")
    for t in targets:
        logger.info(f"  - {t}")

    if not force:
        try:
            ans = input("Proceed with deletion of the above config/logs? [y/N]: ").strip().lower()
        except EOFError:
            ans = "n"
        if ans != "y":
            logger.info("[uninstall] Aborted by user.")
            return

    if not effective_user and os.geteuid() != 0:
        logger.error("[uninstall] You must run this command as root to remove system-wide files.")
        return

    ok = True
    for t in targets:
        ok &= _rm(t)

    if ok:
        logger.info("[uninstall] Done.")
    else:
        logger.error("[uninstall] Completed with errors.")
