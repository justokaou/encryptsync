from main import run_watchers
from utils.logger import get_logger
from utils.system import is_systemd_available
from cli.utils.mode import auto_detect_mode_for_run
from cli.utils.path import get_paths
from pathlib import Path

from cli.utils.service import is_unit_active, list_instances
from cli.utils.system import current_session_id

logger = get_logger("encryptsync-cli")


def start_program():
    # Don't start foreground if the per-session systemd instance is already running.
    service_running = False
    if is_systemd_available():
        sid = current_session_id()
        if sid:
            # check the current session instance
            service_running = is_unit_active(f"encryptsync@{sid}.service")
        else:
            # fallback: if we can't determine SID, bail out if any instance is active
            service_running = bool(list_instances("encryptsync@*.service"))

    if service_running:
        logger.error("[run] EncryptSync systemd instance is already running for this session.")
        raise SystemExit(1)

    mode = auto_detect_mode_for_run()
    paths = get_paths(mode)

    cfg = Path(paths["config_path"])
    if not cfg.exists():
        logger.error(f"[run] Config file not found at {cfg}. Use `encryptsyncctl edit`.")
        raise SystemExit(1)

    logger.info(f"[run] Starting EncryptSync in CLI mode with config: {cfg}")
    try:
        run_watchers(str(cfg))
    except KeyboardInterrupt:
        logger.info("[run] EncryptSync stopped manually.")