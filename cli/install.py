import os
import shutil
from pathlib import Path

from utils.logger import get_logger

from cli.templates.daemon import DAEMON_TEMPLATE
from cli.templates.clear import CLEAR_TEMPLATE
from cli.templates.daemon_user import DAEMON_USER_TEMPLATE
from cli.templates.clear_user import CLEAR_USER_TEMPLATE

from cli.edit import edit
from cli.service import install_service

from cli.utils.path import get_paths
from cli.utils.system import is_deb_install, is_service_installed
from cli.utils.mode import ask_mode, ask_install_method

logger = get_logger("encryptsync-cli")

def copy_default_config(project_path, config_path):
    dst = Path(config_path)
    src = Path(project_path) / "config.template.yaml"

    if dst.exists():
        logger.info(f"[install] Config already exists at {dst}. Skipping copy.")
        return
    if not src.exists():
        logger.critical(f"[install] ERROR: Missing template config at {src}")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    logger.info(f"[install] Default config copied from {src} to {dst}.")

def maybe_edit_config(paths, user=False):
    if input("Edit config now? [y/N]: ").lower() == "y":
        edit(paths, context="install", user=user)

def copy_project_if_needed(mode, target_path, user=False):
    if mode == "2":
        target = Path(target_path)

        if user and target_path == "/usr/lib/encryptsync":
            logger.info("[install] Detected system install via .deb — skipping project copy.")
            return

        if target.exists():
            choice = input(f"[install] Project already exists at {target}. Overwrite? [y/N]: ").strip().lower()
            if choice == "y":
                shutil.rmtree(target)
                logger.info(f"[install] Removed existing directory: {target}")
            else:
                logger.info("[install] Skipping project copy.")
                return

        logger.info(f"[install] Copying project to {target}...")
        shutil.copytree(Path(__file__).resolve().parent.parent, target)

def maybe_install_service(name, template, paths, force=False, user=False):
    if user:
        service_path = Path.home() / ".config/systemd/user" / f"{name}.service"
    else:
        service_path = Path(f"/etc/systemd/system/{name}.service")

    if user:
        os.makedirs(service_path.parent, exist_ok=True)

    if is_service_installed(name, user=user) and not force:
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
    
    install_service(name, template.format(**paths), user=user)

def install(force=False, user=False):
    if not user:
        install_method = ask_install_method()
        user = install_method == "user"
    else:
        install_method = "user" if user else "system"

    if user:
        mode = ask_mode("install")
    else:
        if is_deb_install():
            logger.info("[install] Detected code installed via .deb package.")
            mode = "2"
        else:
            mode = ask_mode("install")


    paths = get_paths(mode, user=user)
    copy_project_if_needed(mode, paths["project_path"], user=user)

    if mode == "2":
        copy_default_config(paths["project_path"], paths["config_path"])

    maybe_edit_config(paths)

    if user:
        maybe_install_service("encryptsync", DAEMON_USER_TEMPLATE, paths, force, user=True)
        maybe_install_service("encryptsync-clear", CLEAR_USER_TEMPLATE, paths, force, user=True)
    else:
        maybe_install_service("encryptsync", DAEMON_TEMPLATE, paths, force)
        maybe_install_service("encryptsync-clear", CLEAR_TEMPLATE, paths, force)

    logger.info("Installation complete.")