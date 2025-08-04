from main import run_watchers
from utils.logger import get_logger
from cli.utils.service import is_service_running

logger = get_logger("encryptsync-cli")

def start_program():
    if is_service_running("encryptsync"):
        logger.info("[run] Starting EncryptSync daemon manually (CLI mode)...")
        try:
            run_watchers()
        except KeyboardInterrupt:
            logger.info("[run] EncryptSync stopped manually.")
    else:
        logger.error("[run] EncryptSync service is running.")
        exit(1)
