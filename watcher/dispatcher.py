import os
from watchdog.observers import Observer
from watcher.handler import EncryptHandler, DecryptHandler

def start_watcher(sync_config):
    observers = []

    if sync_config.direction in ("encrypt-only", "both"):
        plain_handler = EncryptHandler(sync_config)

        if not os.path.exists(sync_config.plain_dir):
            raise FileNotFoundError(f"Plain directory not found: {sync_config.plain_dir}")
        
        plain_observer = Observer()
        plain_observer.schedule(plain_handler, sync_config.plain_dir, recursive=True)
        
        # Scan after scheduling but before starting
        plain_handler.scan_existing_files()
        
        plain_observer.start()
        print(f"Watcher started for encryption: {sync_config.plain_dir}")
        observers.append(plain_observer)

    if sync_config.direction in ("decrypt-only", "both"):
        encrypted_handler = DecryptHandler(sync_config)

        if not os.path.exists(sync_config.encrypted_dir):
            raise FileNotFoundError(f"Encrypted directory not found: {sync_config.encrypted_dir}")
        
        decrypt_observer = Observer()
        decrypt_observer.schedule(encrypted_handler, sync_config.encrypted_dir, recursive=True)
        
        # Scan after scheduling but before starting
        encrypted_handler.scan_existing_files()
        
        decrypt_observer.start()
        print(f"Watcher started for decryption: {sync_config.encrypted_dir}")
        observers.append(decrypt_observer)

    return observers
