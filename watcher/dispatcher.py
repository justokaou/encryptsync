from watchdog.observers import Observer
from watcher.handler import EncryptHandler
import time
import os

def start_watcher(sync_config):
    event_handler = EncryptHandler(sync_config)
    observer = Observer()
    observer.schedule(event_handler, sync_config.plain_dir, recursive=True)
    observer.start()
    print(f"Watcher started for: {sync_config.plain_dir}")
    return observer
