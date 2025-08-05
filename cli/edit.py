import os
import subprocess
from pathlib import Path

from utils.hash import file_sha256
from utils.logger import get_logger

from cli.service import systemctl_cmd

from cli.utils.path import get_paths
from cli.utils.mode import ask_mode

logger = get_logger("encryptsync-cli")

def edit(paths=None, context=None, restart=True, user=False):
    if paths is None:
        mode = ask_mode()
        paths = get_paths(mode, user=user)
    if not Path(paths["config_path"]).exists():
        logger.critical(f"[edit] Config file not found at {paths['config_path']}.")
        return
    hash_before = file_sha256(paths["config_path"])
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, paths["config_path"]])
    hash_after = file_sha256(paths["config_path"])
    if restart and context != "install":
        if hash_before != hash_after and mode != "1":
            logger.info(f"[edit] Config file edited at {paths['config_path']}. Restarting daemon service...")
            systemctl_cmd("restart", "encryptsync")
        elif mode == "1" and hash_before != hash_after:
            logger.info(f"[edit] Config file at {paths['config_path']} edited. You need to restart the program.")
        else:
            logger.info(f"[edit] Config file at {paths['config_path']} has not changed. No restart needed.")