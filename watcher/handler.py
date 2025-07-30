from watchdog.events import FileSystemEventHandler
from crypto.gpg import encrypt_file  # à écrire
import os

class EncryptHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config

    def on_modified(self, event):
        if not event.is_directory:
            encrypt_file(event.src_path, self.config.encrypted_dir, self.config.recipient)
