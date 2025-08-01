import os

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