import os
import time

ORPHAN_GRACE_SECONDS = 30  # délai avant de supprimer le clair si le .gpg a disparu “sans intention”
TOMBSTONE_DIRNAME = ".encryptsync-deletes"

def tombstone_path(encrypted_dir: str, rel_path: str) -> str:
    p = os.path.join(encrypted_dir, TOMBSTONE_DIRNAME, rel_path + ".del")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p

def is_valid_file(path: str) -> bool:
    filename = os.path.basename(path)
    return (
        not filename.startswith(".")
        and not filename.endswith("~")
        and not filename.endswith(".swp")
        and not filename.startswith("#")
    )

def is_forbidden_file(path: str, base_dir: str, mode: str) -> bool:
    rel = os.path.relpath(path, base_dir)
    if mode == "encrypt" and rel.endswith(".gpg"):
        return True
    if mode == "decrypt" and not rel.endswith(".gpg"):
        return True
    return False

def is_stable(path, checks=3, delay=0.2):
    try:
        prev = -1
        for _ in range(checks):
            now = os.path.getsize(path)
            if now == prev:
                return True
            prev = now
            time.sleep(delay)
    except FileNotFoundError:
        return False
    return False
