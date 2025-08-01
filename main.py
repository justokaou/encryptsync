import os
import time
from utils.config import load_config
from watcher.dispatcher import start_watcher
from watchdog.observers import Observer

def create_observers(handlers):
    observers = []
    for handler, path in handlers:
        obs = Observer()
        obs.schedule(handler, path, recursive=True)
        obs.start()
        observers.append(obs)
    return observers

if __name__ == "__main__":
    syncs = load_config()
    all_handlers = []

    for sync in syncs:
        all_handlers += start_watcher(sync)

    observers = create_observers(all_handlers)

    PAUSE_FLAG = "/tmp/encryptsync.pause"
    paused = False

    try:
        while True:
            if os.path.exists(PAUSE_FLAG) and not paused:
                print("[encryptsync] Pause asked : complete shutdown of observers")
                for obs in observers:
                    obs.stop()
                for obs in observers:
                    obs.join()
                observers = []
                paused = True

            elif not os.path.exists(PAUSE_FLAG) and paused:
                print("[encryptsync] Restart : restarting observers")
                observers = create_observers(all_handlers)
                paused = False

            time.sleep(1)

    except KeyboardInterrupt:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()