import os
import shutil
from pathlib import Path

from utils.logger import get_logger

from cli.templates.daemon import DAEMON_TEMPLATE
from cli.templates.clear import CLEAR_TEMPLATE

from cli.edit import edit
from cli.service import install_service

from cli.utils.path import get_paths
from cli.utils.system import is_deb_install, is_service_installed
from cli.utils.mode import ask_mode

logger = get_logger("encryptsync-cli")

def copy_default_config(project_path):
    dst = Path("/etc/encryptsync/config.yaml")
    src = Path(project_path) / "config.template.yaml"

    if dst.exists():
        logger.info("[install] Config already exists. Skipping default copy.")
        return
    if not src.exists():
        logger.critical("[install] ERROR: Missing template config at", src)
        return

    os.makedirs(dst.parent, exist_ok=True)
    shutil.copy(src, dst)
    logger.info(f"[install] Default config copied from {src} to {dst}.")

def maybe_edit_config(paths):
    if input("Edit config now? [y/N]: ").lower() == "y":
        edit(paths, context="install")

def copy_project_if_needed(mode, target_path):
    if mode == "2":
        if target_path == "/usr/lib/encryptsync":
            logger.info("[install] Detected system install via .deb — skipping project copy.")
            return

        if Path(target_path).exists():
            choice = input(f"[install] Project already exists at {target_path}. Overwrite? [y/N]: ").strip().lower()
            if choice == "y":
                shutil.rmtree(target_path)
                logger.info(f"[install] Removed existing directory: {target_path}")
            else:
                logger.info("[install] Skipping project copy.")
                return

        logger.info(f"[install] Copying project to {target_path}...")
        shutil.copytree(Path(__file__).resolve().parent.parent, target_path)



def maybe_install_service(name, template, paths, force=False):
    service_path = Path(f"/etc/systemd/system/{name}.service")

    if is_service_installed(name) and not force:
        logger.info(f"[install] {name}.service already installed. Skipping.")
        return

    if force:
        logger.info(f"[install] Forcing reinstallation of {name}.service...")
        if service_path.exists():
            service_path.unlink()
            logger.info(f"[install] Removed existing {name}.service before reinstalling.")
    else:
        confirm = input(f"Install {name} service? [y/N]: ").lower()
        if confirm != "y":
            logger.info(f"[install] Skipping {name}.service.")
            return

    install_service(name, template.format(**paths))

def install(force=False):
    if is_deb_install():
        mode = "2"
    else:
        mode = ask_mode("install")

    paths = get_paths(mode)
    copy_project_if_needed(mode, paths["project_path"])

    if mode == "2":
        copy_default_config(paths["project_path"])

    maybe_edit_config(paths)

    maybe_install_service("encryptsync", DAEMON_TEMPLATE, paths, force)
    maybe_install_service("encryptsync-clear", CLEAR_TEMPLATE, paths, force)

    logger.info("Installation complete.")