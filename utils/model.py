from dataclasses import dataclass

@dataclass
class SyncConfig:
    name: str
    plain_dir: str
    encrypted_dir: str
    gpg_key: str
    direction: str  # "encrypt-only", "decrypt-only", "both"
    clear_on_shutdown: bool = False