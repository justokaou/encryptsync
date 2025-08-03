import os
from utils.cache import load_cache, save_cache
from crypto.gpg import decrypt_file
from utils.hash import file_sha256
from utils.file import is_valid_file
from utils.lookup import find_matching_sync
from utils.logger import get_logger

logger = get_logger("encryptsync-cli")

def decrypt_path(target_path, config, output_override=None):
    cache = load_cache()
    target_path = os.path.abspath(target_path)
    sync = find_matching_sync(target_path, config, mode="decrypt")

    if not sync:
        logger.error("[decrypt] No matching config found for this path. Make sure you are targeting the encrypted directory.")
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
                logger.info(f"[decrypt] Skipping unchanged: {rel_path}")
                continue

        try:
            decrypt_file(
                input_path=f,
                output_dir=out_dir,
                base_dir=base_dir,
                logger=logger
            )
            if os.path.exists(output_path):
                cache[rel_path] = file_sha256(output_path)
        except Exception as e:
            logger.error(f"[decrypt] Failed to decrypt {f}: {e}")

    save_cache(cache)