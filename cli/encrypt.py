from crypto.gpg import encrypt_file
from utils.hash import file_sha256
from cache import load_cache, save_cache
import os

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

def encrypt_path(target_path, config, output_override=None):
    cache = load_cache()
    target_path = os.path.abspath(target_path)
    sync = find_matching_sync(target_path, config, mode="encrypt")

    if not sync:
        print("[encrypt] No matching config found for this path.")
        return

    base_dir = sync.plain_dir
    out_dir = output_override or sync.encrypted_dir
    recipient = sync.recipient

    if os.path.isfile(target_path):
        files = [target_path]
    else:
        files = [
            os.path.join(dp, f)
            for dp, _, filenames in os.walk(target_path)
            for f in filenames
            if is_valid_file(os.path.join(dp, f))
        ]

    for f in files:
        rel_path = os.path.relpath(f, base_dir)
        file_hash = file_sha256(f)
        output_path = os.path.join(out_dir, rel_path + ".gpg")

        # Skip only if hash is unchanged AND output file exists
        if cache.get(rel_path) == file_hash and os.path.exists(output_path):
            print(f"[encrypt] Skipping unchanged: {rel_path}")
            continue

        try:
            encrypt_file(
                input_path=f,
                output_dir=out_dir,
                recipient=recipient,
                base_dir=base_dir
            )
            cache[rel_path] = file_hash
        except Exception as e:
            print(f"[encrypt] Failed to encrypt {f}: {e}")

    save_cache(cache)
