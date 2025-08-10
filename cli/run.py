from main import run_watchers
from utils.logger import get_logger
from utils.system import is_systemd_available
from cli.utils.service import is_service_running, unit_name
from cli.utils.mode import auto_detect_mode_for_run
from cli.utils.path import get_paths
from pathlib import Path

logger = get_logger("encryptsync-cli")


def start_program():
    service_running = False
    if is_systemd_available():
        service_running = is_service_running(unit_name("encryptsync"))

    if service_running:
        logger.error("[run] EncryptSync service is already running.")
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