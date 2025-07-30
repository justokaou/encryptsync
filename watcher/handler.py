from watchdog.events import FileSystemEventHandler
from crypto.gpg import encrypt_file 
from cache import load_cache, save_cache
from utils.hash import file_sha256
import os

def is_valid_file(path: str) -> bool:
    filename = os.path.basename(path)
    return (
        not filename.startswith(".")
        and not filename.endswith("~")
        and not filename.endswith(".swp")
        and not filename.startswith("#")
    )


class EncryptHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.cache = load_cache()

    def on_modified(self, event):
        if not event.is_directory and is_valid_file(event.src_path):
            file_hash = file_sha256(event.src_path)
            cached_hash = self.cache.get(event.src_path)

            if cached_hash == file_hash:
                return  # not modified > skipped
            else:
                self.process(event.src_path, new_hash=file_hash)

    def process(self, src_path, new_hash):
        try:
            encrypt_file(src_path, self.config.encrypted_dir, self.config.recipient)
            self.cache[src_path] = new_hash
            save_cache(self.cache)
        except Exception as e:
            print(f"[Error] Failed to encrypt {src_path}: {e}")
