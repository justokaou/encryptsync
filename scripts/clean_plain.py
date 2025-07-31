import os
import sys
import time
from filelock import FileLock, Timeout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import load_config

LOCK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".encryptsync.lock"))
LOCK = FileLock(LOCK_PATH, timeout=5)

PAUSE_FLAG = "/tmp/encryptsync.pause"

def clear_plain(config):
    confirm = input("This will delete all plaintext files. Proceed? [y/N]: ")
    if confirm.lower() != "y":
        print("Operation cancelled by user.")
        return

    # Create the pause flag to signal watchers
    open(PAUSE_FLAG, "w").close()
    print("[clear_plain] Pause demandée. Attente de la désactivation des watchers...")

    # Wait for watchers to stop in main.py
    time.sleep(1)

    print(f"[clear_plain] Acquiring lock: {LOCK_PATH}")
    try:
        with LOCK:
            print("[clear_plain] Lock acquired. Proceeding with plaintext deletion.")

            for sync in config:
                plain_dir = sync.plain_dir
                print(f"[clear_plain] Cleaning plaintext directory: {plain_dir}")

                for root, dirs, files in os.walk(plain_dir, topdown=False):
                    for f in files:
                        file_path = os.path.join(root, f)
                        try:
                            os.remove(file_path)
                            print(f"[clear_plain] Deleted file: {file_path}")
                        except Exception as e:
                            print(f"[clear_plain] Could not delete {file_path}: {e}")

                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        try:
                            os.rmdir(dir_path)
                        except OSError:
                            pass  # Ignore if not empty

                print(f"[clear_plain] Done. Plaintext files removed for: {plain_dir}")

    except Timeout:
        print("[clear_plain] Could not acquire lock. Another process might be using the sync.")
    finally:
        # Delete the pause flag to allow watchers to restart
        if os.path.exists(PAUSE_FLAG):
            os.remove(PAUSE_FLAG)
            print("[clear_plain] Pause levée. Les watchers peuvent redémarrer.")

if __name__ == "__main__":
    config = load_config()
    clear_plain(config)