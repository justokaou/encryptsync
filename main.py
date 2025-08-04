import os
import time
from utils.config import load_config
from watcher.dispatcher import start_watchers
from watchdog.observers import Observer
from utils.log import logger

def create_observers(handlers):
    observers = []
    for handler, path in handlers:
        obs = Observer()
        obs.schedule(handler, path, recursive=True)
        obs.start()
        observers.append(obs)
    return observers

def run_watchers():
    syncs = load_config()
    all_handlers = []

    valid_syncs = []
    for sync in syncs:
        for path in [sync.plain_dir, sync.encrypted_dir]:
            if not os.path.isdir(path):
                logger.error(f"[encryptsync] [ERROR] Directory does not exist: {path}")
                break
        else:
            valid_syncs.append(sync)

    all_handlers = start_watchers(valid_syncs)


    observers = create_observers(all_handlers)

    PAUSE_FLAG = "/tmp/encryptsync.pause"
    paused = False

    try:
        while True:
            if os.path.exists(PAUSE_FLAG) and not paused:
                logger.info("[encryptsync] Pause asked : complete shutdown of observers")
                for obs in observers:
                    obs.stop()
                for obs in observers:
                    obs.join()
                observers = []
                paused = True

            elif not os.path.exists(PAUSE_FLAG) and paused:
                logger.info("[encryptsync] Restart : restarting observers")
                observers = create_observers(all_handlers)
                paused = False

            time.sleep(1)

    except KeyboardInterrupt:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()

if __name__ == "__main__":
    run_watchers()