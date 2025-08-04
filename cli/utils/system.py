from pathlib import Path

def is_deb_install():
    return Path("/usr/lib/encryptsync").exists()

def is_service_installed(name):
    return Path(f"/etc/systemd/system/{name}.service").exists()