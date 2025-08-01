import os

def find_matching_sync(path, config, mode):
    for sync in config:
        base = sync.plain_dir if mode == "encrypt" else sync.encrypted_dir
        if os.path.commonpath([os.path.abspath(path), base]) == os.path.abspath(base):
            return sync
    return None