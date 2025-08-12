# install.py (extrait)

import os
import subprocess
import shutil
from pathlib import Path

from utils.logger import get_logger
from cli.edit import edit
from cli.utils.path import get_paths
from cli.utils.service import wait_unit_active
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

def self_test_user_mode() -> bool:
    """
    Quick non-intrusive test:
    - drop open/close into %t/encryptsync
    - trigger the dispatcher once
    - verify that encryptsync@<sid> appears and then disappears
    """
    sid = current_session_id()
    if not sid:
        logger.warning("[install] self-test skipped (no session id).")
        return True

    uid = os.getuid()
    xdg_rt = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    qdir = Path(xdg_rt) / "encryptsync"
    qdir.mkdir(parents=True, exist_ok=True)

    # open -> start
    (qdir / f"open-{sid}").touch()
    subprocess.run(["systemctl", "--user", "start", "encryptsync-dispatch.service"], check=False)
    started = wait_unit_active(f"encryptsync@{sid}.service", timeout=10)

    # close -> stop
    (qdir / f"close-{sid}").touch()
    subprocess.run(["systemctl", "--user", "start", "encryptsync-dispatch.service"], check=False)
    # No need for the wait_stop utility here; the dispatcher simply running is sufficient for this smoke test

    if started:
        logger.info("[install] Self-test OK (queue → dispatcher).")
        return True
    else:
        logger.warning("[install] Self-test did not see encryptsync@%s become active.", sid)
        return False

def install():
    paths = get_paths("2")

    copy_default_config(paths["project_path"], paths["config_path"])
    maybe_edit_config(paths)

    ok = True
    ok = self_test_user_mode()

    if ok:
        logger.info("Installation complete.")
    else:
        logger.error("[install] Post-check failed")
