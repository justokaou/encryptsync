from pathlib import Path
import os
import json

def get_cache_path():
    # Use ~/.encryptsync/cache/ if XDG not defined
    base_dir = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".encryptsync"))
    cache_dir = base_dir / "cache"
    cache_file = cache_dir / "cache.json"
    return cache_dir, cache_file

def load_cache():
    _, cache_file = get_cache_path()
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    cache_dir, cache_file = get_cache_path()
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)
