import os
from config import load_config
from cache import load_cache, save_cache
from crypto.gpg import decrypt_file
from utils.hash import file_sha256

def is_valid_file(path):
    fname = os.path.basename(path)
    return (
        not fname.startswith(".")
        and not fname.endswith("~")
        and not fname.endswith(".swp")
        and not fname.startswith("#")
    )

def find_matching_sync(path, config, mode):
    for sync in config:
        base = sync.plain_dir if mode == "encrypt" else sync.encrypted_dir
        if os.path.commonpath([os.path.abspath(path), base]) == os.path.abspath(base):
            return sync
    return None

def decrypt_path(target_path, config, output_override=None):
    cache = load_cache()
    target_path = os.path.abspath(target_path)
    sync = find_matching_sync(target_path, config, mode="decrypt")

    if not sync:
        print("[decrypt] No matching config found for this path.")
        return

    base_dir = sync.encrypted_dir
    out_dir = output_override or sync.plain_dir

    if os.path.isfile(target_path):
        files = [target_path] if target_path.endswith(".gpg") else []
    else:
        files = [
            os.path.join(dp, f)
            for dp, _, filenames in os.walk(target_path)
            for f in filenames
            if f.endswith(".gpg") and is_valid_file(os.path.join(dp, f))
        ]

    for f in files:
        rel_path = os.path.splitext(os.path.relpath(f, base_dir))[0]
        output_path = os.path.join(out_dir, rel_path)

        if os.path.exists(output_path):
            output_hash = file_sha256(output_path)
            if cache.get(rel_path) == output_hash:
                print(f"[decrypt] Skipping unchanged: {rel_path}")
                continue

        try:
            decrypt_file(
                input_path=f,
                output_dir=out_dir,
                base_dir=base_dir
            )
            if os.path.exists(output_path):
                cache[rel_path] = file_sha256(output_path)
        except Exception as e:
            print(f"[decrypt] Failed to decrypt {f}: {e}")

    save_cache(cache)