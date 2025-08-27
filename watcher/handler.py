from watchdog.events import FileSystemEventHandler
from crypto.gpg import encrypt_file, decrypt_file 
from utils.cache import load_cache, save_cache
from utils.hash import file_sha256
from utils.file import is_valid_file, is_forbidden_file, tombstone_path, TOMBSTONE_DIRNAME, ORPHAN_GRACE_SECONDS
from utils.recent import mark_recent_output, is_recent_output
from filelock import FileLock, Timeout
import os, time
from utils.log import logger
import tempfile
import threading

uid = os.getuid()
LOCK_PATH = os.path.join(tempfile.gettempdir(), f"encryptsync-{uid}.lock")
LOCK = FileLock(LOCK_PATH)

def is_locked() -> bool:
    try:
        with LOCK.acquire(timeout=0.1):
            return False
    except Timeout:
        return True

class EncryptHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.cache = load_cache()
        self.processing = set()
        self.scanning = False

    def on_created(self, event):
        self.on_modified(event)


    def on_modified(self, event):
        if is_locked() or self.scanning or event.is_directory or not is_valid_file(event.src_path):
            return
        
        if is_forbidden_file(event.src_path, self.config.plain_dir, "encrypt"):
            logger.warning(f"[WARN] Skipping invalid file in plain_dir: {event.src_path}")
            return

        rel_path = os.path.relpath(event.src_path, self.config.plain_dir)
        if rel_path in self.processing:
            return

        file_hash = file_sha256(event.src_path)
        if self.cache.get(rel_path) == file_hash:
            return

        self.processing.add(rel_path)
        try:
            mark_recent_output(os.path.join(self.config.encrypted_dir, rel_path + ".gpg"))
            encrypt_file(
                input_path=event.src_path,
                output_dir=self.config.encrypted_dir,
                gpg_key=self.config.gpg_key,
                base_dir=self.config.plain_dir,
                logger=logger
            )
            self.cache[rel_path] = file_hash
            save_cache(self.cache)
        except Exception as e:
            logger.error(f"[Error] Failed to encrypt {event.src_path}: {e}")
        finally:
            self.processing.remove(rel_path)

    def on_deleted(self, event):
        if is_locked() or event.is_directory or not is_valid_file(event.src_path):
            return

        rel_path = os.path.relpath(event.src_path, self.config.plain_dir)
        encrypted_path = os.path.join(self.config.encrypted_dir, rel_path + ".gpg")

        # 1) toujours poser un tombstone côté chiffré (propagation de l’intention)
        tpath = tombstone_path(self.config.encrypted_dir, rel_path)
        try:
            os.makedirs(os.path.dirname(tpath), exist_ok=True)
            # un petit contenu avec un horodatage aide au debug
            with open(tpath, "w") as f:
                f.write(f"ts={int(time.time())}\nrel={rel_path}\n")
            logger.info(f"[tombstone] {tpath}")
        except Exception as e:
            logger.error(f"[Error] Failed to create tombstone {tpath}: {e}")

        # 2) si le .gpg existe déjà, on le supprime maintenant (Syncthing répliquera)
        if os.path.exists(encrypted_path):
            try:
                os.remove(encrypted_path)
                logger.info(f"[delete] {encrypted_path}")
            except Exception as e:
                logger.error(f"[Error] Failed to delete encrypted {encrypted_path}: {e}")

        # 3) mettre à jour le cache
        self.cache.pop(rel_path, None)
        save_cache(self.cache)


    def scan_existing_files(self):
        self.scanning = True
        try:
            for root, _, files in os.walk(self.config.plain_dir):
                for f in files:
                    full_path = os.path.join(root, f)
                    if not is_valid_file(full_path):
                        continue

                    if is_forbidden_file(full_path, self.config.plain_dir, "encrypt"):
                        logger.warning(f"[WARN] Skipping invalid file in plain_dir during scan: {full_path}")
                        continue

                    rel_path = os.path.relpath(full_path, self.config.plain_dir)
                    file_hash = file_sha256(full_path)

                    if self.cache.get(rel_path) == file_hash:
                        continue

                    try:
                        mark_recent_output(os.path.join(self.config.encrypted_dir, rel_path + ".gpg"))
                        encrypt_file(
                            input_path=full_path,
                            output_dir=self.config.encrypted_dir,
                            gpg_key=self.config.gpg_key,
                            base_dir=self.config.plain_dir,
                            logger=logger
                        )
                        self.cache[rel_path] = file_hash
                    except Exception as e:
                        logger.error(f"[Error] Failed to encrypt {full_path}: {e}")

            save_cache(self.cache)
        finally:
            self.scanning = False
            logger.info("Scan completed for encryption handler.")


class DecryptHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.cache = load_cache()
        self.processing = set()
        self.scanning = False

    def on_created(self, event):
        self._handle_event(event)

    def on_modified(self, event):
        self._handle_event(event)

    def _handle_event(self, event):
        if is_locked() or self.scanning or event.is_directory:
            return

        if event.src_path.endswith(".del"):
            self._apply_tombstone(event.src_path)
            return
    
        if not event.src_path.endswith(".gpg"):
            return
        
        if is_forbidden_file(event.src_path, self.config.encrypted_dir, "decrypt"):
            logger.warning(f"[WARN] Skipping invalid file in encrypted_dir: {event.src_path}")
            return
        
        if is_recent_output(event.src_path):
            return

        rel_path = os.path.splitext(os.path.relpath(event.src_path, self.config.encrypted_dir))[0]
        if rel_path in self.processing:
            return

        output_path = os.path.join(self.config.plain_dir, rel_path)

        if os.path.exists(output_path):
            current_hash = file_sha256(output_path)
            if self.cache.get(rel_path) == current_hash:
                return

        self.processing.add(rel_path)
        try:
            decrypt_file(
                input_path=event.src_path,
                output_dir=self.config.plain_dir,
                base_dir=self.config.encrypted_dir,
                logger=logger
            )
            if os.path.exists(output_path):
                mark_recent_output(output_path)
                file_hash = file_sha256(output_path)
                self.cache[rel_path] = file_hash
                save_cache(self.cache)
        except Exception as e:
            logger.error(f"[Error] Failed to decrypt {event.src_path}: {e}")
        finally:
            self.processing.remove(rel_path)

    def on_deleted(self, event):
        if is_locked() or event.is_directory or not event.src_path.endswith(".gpg"):
            return

        rel_path = os.path.splitext(os.path.relpath(event.src_path, self.config.encrypted_dir))[0]
        plain_path = os.path.join(self.config.plain_dir, rel_path)

        tpath = tombstone_path(self.config.encrypted_dir, rel_path)
        if os.path.exists(tpath):
            self._apply_tombstone(tpath)
            return

        threading.Thread(
            target=self._delayed_delete_plain,
            args=(plain_path, event.src_path, rel_path),
            daemon=True
        ).start()


    def scan_existing_files(self):
        self.scanning = True
        try:
            tdir = os.path.join(self.config.encrypted_dir, TOMBSTONE_DIRNAME)
            if os.path.isdir(tdir):
                for root, _, files in os.walk(tdir):
                    for f in files:
                        if f.endswith(".del"):
                            self._apply_tombstone(os.path.join(root, f))

            for root, _, files in os.walk(self.config.encrypted_dir):
                for f in files:
                    if not f.endswith(".gpg"):
                        continue

                    full_path = os.path.join(root, f)
                    if not is_valid_file(full_path):
                        continue

                    rel_path = os.path.splitext(os.path.relpath(full_path, self.config.encrypted_dir))[0]
                    plain_path = os.path.join(self.config.plain_dir, rel_path)

                    if os.path.exists(plain_path):
                        plain_hash = file_sha256(plain_path)
                        if self.cache.get(rel_path) == plain_hash:
                            continue

                    try:
                        decrypt_file(
                            input_path=full_path,
                            output_dir=self.config.plain_dir,
                            base_dir=self.config.encrypted_dir,
                            logger=logger
                        )
                        if os.path.exists(plain_path):
                            file_hash = file_sha256(plain_path)
                            self.cache[rel_path] = file_hash
                    except Exception as e:
                        logger.error(f"[Error] Failed to decrypt {full_path}: {e}")

            save_cache(self.cache)
        finally:
            self.scanning = False
            logger.info("Scan completed for decryption handler.")

        def _apply_tombstone(self, tpath: str):
            try:
                rel_with_ext = os.path.relpath(tpath, os.path.join(self.config.encrypted_dir, TOMBSTONE_DIRNAME))
                rel_path = rel_with_ext[:-4] if rel_with_ext.endswith(".del") else rel_with_ext
                gpg_path = os.path.join(self.config.encrypted_dir, rel_path + ".gpg")
                plain_path = os.path.join(self.config.plain_dir, rel_path)

                # supprimer le clair si présent
                if os.path.exists(plain_path):
                    try:
                        os.remove(plain_path)
                        logger.info(f"[delete] {plain_path}")
                    except Exception as e:
                        logger.error(f"[Error] Failed to delete plaintext {plain_path}: {e}")

                # si le .gpg est apparu entre-temps, le supprimer aussi (idempotent)
                if os.path.exists(gpg_path):
                    try:
                        os.remove(gpg_path)
                        logger.info(f"[delete] {gpg_path}")
                    except Exception as e:
                        logger.error(f"[Error] Failed to delete encrypted {gpg_path}: {e}")

                # nettoyer cache et tombstone
                self.cache.pop(rel_path, None)
                save_cache(self.cache)
            finally:
                try:
                    os.remove(tpath)
                    logger.info(f"[tombstone-applied] {tpath}")
                except FileNotFoundError:
                    pass
                except Exception as e:
                    logger.error(f"[Error] Failed to remove tombstone {tpath}: {e}")

        def _delayed_delete_plain(self, plain_path: str, gpg_path: str, rel_path: str):
            deadline = time.time() + ORPHAN_GRACE_SECONDS
            while time.time() < deadline:
                if os.path.exists(gpg_path):
                    logger.info(f"[delete-cancel] {rel_path}: encrypted reappeared during grace")
                    return
                # si un tombstone arrive pendant l'attente, appliquer tout de suite
                tpath = tombstone_path(self.config.encrypted_dir, rel_path)
                if os.path.exists(tpath):
                    self._apply_tombstone(tpath); return
                time.sleep(1.0)

            if os.path.exists(plain_path):
                try:
                    os.remove(plain_path)
                    logger.info(f"[delete] {plain_path}")
                except Exception as e:
                    logger.error(f"[Error] Failed to delete plaintext {plain_path}: {e}")
            self.cache.pop(rel_path, None)
            save_cache(self.cache)