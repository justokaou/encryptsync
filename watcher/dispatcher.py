from watcher.handler import EncryptHandler, DecryptHandler

def start_watchers(syncs):
    handlers = []
    encrypt_paths = {}
    decrypt_paths = {}

    for sync in syncs:
        # EncryptHandler for unique plain_dir
        if sync.direction in ("encrypt-only", "both"):
            if sync.plain_dir not in encrypt_paths:
                encrypt_paths[sync.plain_dir] = sync

        # DecryptHandler for unique encrypted_dir
        if sync.direction in ("decrypt-only", "both"):
            if sync.encrypted_dir not in decrypt_paths:
                decrypt_paths[sync.encrypted_dir] = sync

    for plain_dir, config in encrypt_paths.items():
        handler = EncryptHandler(config)
        handler.scan_existing_files()
        handlers.append((handler, plain_dir))

    for encrypted_dir, config in decrypt_paths.items():
        handler = DecryptHandler(config)
        handler.scan_existing_files()
        handlers.append((handler, encrypted_dir))

    return handlers