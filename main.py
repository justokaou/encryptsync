import yaml
from model import SyncConfig

def load_config(path="config.yaml") -> list[SyncConfig]:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return [SyncConfig(**entry) for entry in raw["syncs"]]

if __name__ == "__main__":
    syncs = load_config()
    for sync in syncs:
        print(f"[{sync.name}] Plain: {sync.plain_dir} → Encrypted: {sync.encrypted_dir}")