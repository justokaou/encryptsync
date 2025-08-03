from watcher.handler import EncryptHandler, DecryptHandler

def start_watcher(sync_config):
    handlers = []

    if sync_config.direction in ("encrypt-only", "both"):
        plain_handler = EncryptHandler(sync_config)
        plain_handler.scan_existing_files()
        handlers.append((plain_handler, sync_config.plain_dir))

    if sync_config.direction in ("decrypt-only", "both"):
        decrypt_handler = DecryptHandler(sync_config)
        decrypt_handler.scan_existing_files()
        handlers.append((decrypt_handler, sync_config.encrypted_dir))

    return handlers

