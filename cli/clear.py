import os, time

def clear_plain(config):
    from filelock import FileLock, Timeout

    PAUSE_FLAG = "/tmp/encryptsync.pause"
    LOCK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".encryptsync.lock"))
    LOCK = FileLock(LOCK_PATH, timeout=5)

    confirm = input("This will delete all plaintext files. Proceed? [y/N]: ")
    if confirm.lower() != "y":
        print("Operation cancelled by user.")
        return

    open(PAUSE_FLAG, "w").close()
    print("[clear] Pause asked. Waiting watchers...")

    time.sleep(1)  # Optionnal : give time for watchers to pause

    print(f"[clear] Acquiring lock: {LOCK_PATH}")
    try:
        with LOCK:
            print("[clear] Lock acquired. Deleting plaintext files.")

            for sync in config:
                plain_dir = sync.plain_dir
                print(f"[clear] Purging: {plain_dir}")

                for root, dirs, files in os.walk(plain_dir, topdown=False):
                    for f in files:
                        path = os.path.join(root, f)
                        try:
                            os.remove(path)
                            print(f"[clear] Deleted: {path}")
                        except Exception as e:
                            print(f"[clear] Could not delete {path}: {e}")

                    for d in dirs:
                        dpath = os.path.join(root, d)
                        try:
                            os.rmdir(dpath)
                        except OSError:
                            pass

    except Timeout:
        print("[clear] Could not acquire lock.")
    finally:
        if os.path.exists(PAUSE_FLAG):
            os.remove(PAUSE_FLAG)
            print("[clear] Watchers can resume.")