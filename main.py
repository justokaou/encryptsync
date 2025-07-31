from watcher.dispatcher import start_watcher
from config import load_config
import time

if __name__ == "__main__":
    syncs = load_config()
    observers = []
    for sync in syncs:
        if sync.direction in ("encrypt-only", "both"):
            observers += start_watcher(sync)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()
