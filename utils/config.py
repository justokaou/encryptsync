import yaml
import os
from pathlib import Path
from utils.model import SyncConfig

DEFAULT_CONFIG_PATHS = [
    os.path.join(os.getcwd(), "config.yaml"),                            # priorité dev
    os.path.join(Path.home(), ".encryptsync", "config.yaml"),           # user mode
    "/etc/encryptsync/config.yaml"                                      # fallback prod
]

def load_config(path=None) -> list[SyncConfig]:
    if path:
        paths_to_try = [path]
    else:
        paths_to_try = DEFAULT_CONFIG_PATHS

    for config_path in paths_to_try:
        if os.path.exists(config_path):
            with open(config_path) as f:
                raw = yaml.safe_load(f)
            return [SyncConfig(**entry) for entry in raw["syncs"]]

    raise FileNotFoundError("No configuration file found in expected locations.")
