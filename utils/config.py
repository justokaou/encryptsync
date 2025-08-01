import yaml
from utils.model import SyncConfig

def load_config(path="config.yaml") -> list[SyncConfig]:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return [SyncConfig(**entry) for entry in raw["syncs"]]