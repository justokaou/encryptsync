from model import SyncConfig
from watcher.dispatcher import start_watcher
import yaml
import time

def load_config(path="config.yaml") -> list[SyncConfig]:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return [SyncConfig(**entry) for entry in raw["syncs"]]

if __name__ == "__main__":
    syncs = load_config()
    observers = []
    for sync in syncs:
        if sync.direction in ("encrypt-only", "both"):
            observer = start_watcher(sync)
            observers.append(observer)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()
