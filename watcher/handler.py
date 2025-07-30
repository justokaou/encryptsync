from watchdog.events import FileSystemEventHandler
from crypto.gpg import encrypt_file 
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

    def on_modified(self, event):
        if not event.is_directory and is_valid_file(event.src_path):
            self.process(event.src_path)

    def process(self, src_path):
        try:
            encrypt_file(src_path, self.config.encrypted_dir, self.config.recipient)
        except Exception as e:
            print(f"[Error] Failed to encrypt {src_path}: {e}")
