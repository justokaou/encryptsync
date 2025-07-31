import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import load_config
LOCK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".encryptsync.lock"))

def clear_plain(config):
    confirm = input("This will delete all plaintext files. Proceed? [y/N]: ")
    if confirm.lower() != "y":
        print("Operation cancelled by user.")
        return

    open(LOCK_PATH, "w").close()  # Create a lock file to prevent other operations

    for sync in config:
        plain_dir = sync.plain_dir

        print(f"Cleaning plaintext directory: {plain_dir}")
        for root, dirs, files in os.walk(plain_dir, topdown=False):
            for f in files:
                file_path = os.path.join(root, f)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Could not delete {file_path}: {e}")

            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    os.rmdir(dir_path)
                except OSError:
                    pass  # Ignore if not empty

        print(f"Done. Plaintext files removed for: {plain_dir}")

    os.remove(LOCK_PATH)

if __name__ == "__main__":
    config = load_config()
    clear_plain(config)
