import os
from watchdog.observers import Observer
from watcher.handler import EncryptHandler

def start_watcher(sync_config):
    if not os.path.exists(sync_config.plain_dir):
        raise FileNotFoundError(f"Plain directory not found: {sync_config.plain_dir}")
    
    event_handler = EncryptHandler(sync_config)
    observer = Observer()
    observer.schedule(event_handler, sync_config.plain_dir, recursive=True)
    observer.start()
    print(f"Watcher started for: {sync_config.plain_dir}")
    return observer