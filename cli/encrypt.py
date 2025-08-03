from crypto.gpg import encrypt_file
from utils.hash import file_sha256
from utils.cache import load_cache, save_cache
from utils.file import is_valid_file
from utils.lookup import find_matching_sync
import os
from utils.logger import get_logger

logger = get_logger("encryptsync-cli")

def encrypt_path(target_path, config, output_override=None):
    cache = load_cache()
    target_path = os.path.abspath(target_path)
    sync = find_matching_sync(target_path, config, mode="encrypt")

    if not sync:
        logger.error("[encrypt] No matching config found for this path.")
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
            logger.info(f"[encrypt] Skipping unchanged: {rel_path}")
            continue

        try:
            encrypt_file(
                input_path=f,
                output_dir=out_dir,
                recipient=recipient,
                base_dir=base_dir,
                logger=logger
            )
            cache[rel_path] = file_hash
        except Exception as e:
            logger.error(f"[encrypt] Failed to encrypt {f}: {e}")

    save_cache(cache)
