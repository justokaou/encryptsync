from pathlib import Path

def is_deb_install():
    return Path("/usr/lib/encryptsync").exists()

def is_service_installed(name, user=False):
    if user:
        return Path.home().joinpath(".config/systemd/user", f"{name}.service").exists()
    else:
        return Path(f"/etc/systemd/system/{name}.service").exists()