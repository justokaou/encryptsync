import os, time
from filelock import FileLock, Timeout
from utils.logger import get_logger
import tempfile

logger = get_logger("encryptsync-clear")

def clear_plain(config, confirm=True):
    uid = os.getuid()

    PAUSE_FLAG = "/tmp/encryptsync.pause"
    LOCK_PATH = os.path.join(tempfile.gettempdir(), f"encryptsync-{uid}.lock")
    LOCK = FileLock(LOCK_PATH, timeout=5)

    if confirm:
        user_input = input("This will delete all plaintext files. Proceed? [y/N]: ")
        if user_input.lower() != "y":
            logger.warning("[clear] Operation cancelled by user.")
            return

    open(PAUSE_FLAG, "w").close()
    logger.info("[clear] Pause asked. Waiting watchers...")

    time.sleep(1)  # Optionnal : give time for watchers to pause

    logger.info(f"[clear] Acquiring lock: {LOCK_PATH}")
    try:
        with LOCK:
            logger.info("[clear] Lock acquired. Deleting plaintext files.")

            for sync in config:
                plain_dir = sync.plain_dir
                logger.info(f"[clear] Purging: {plain_dir}")

                for root, dirs, files in os.walk(plain_dir, topdown=False):
                    for f in files:
                        path = os.path.join(root, f)
                        try:
                            os.remove(path)
                            logger.info(f"[clear] Deleted: {path}")
                        except Exception as e:
                            logger.error(f"[clear] Could not delete {path}: {e}")

                    for d in dirs:
                        dpath = os.path.join(root, d)
                        try:
                            os.rmdir(dpath)
                        except OSError:
                            pass

    except Timeout:
        logger.error("[clear] Could not acquire lock.")
    finally:
        if os.path.exists(PAUSE_FLAG):
            os.remove(PAUSE_FLAG)
            logger.info("[clear] Watchers can resume.")