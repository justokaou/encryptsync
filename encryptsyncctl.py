#!/usr/bin/env python3
import argparse
import pathlib
from utils.config import load_config

from cli.encrypt import encrypt_path
from cli.decrypt import decrypt_path
from cli.clear import clear_plain
from cli.service import systemctl_cmd, status_cmd, print_service_status, print_service_enabled
from cli.install import install
from cli.edit import edit
from cli.run import start_program
from cli.uninstall import uninstall
from utils.system import is_systemd_available
from utils.logger import get_logger

logger = get_logger("encryptsync-cli")

VERSION_FILE = pathlib.Path(__file__).resolve().parent / "version.txt"


def get_version():
    try:
        return VERSION_FILE.read_text().strip()
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="EncryptSync control utility")
    parser.add_argument("--version", action="store_true", help="Show EncryptSync version")
    subparsers = parser.add_subparsers(dest="command")

    enc = subparsers.add_parser("encrypt", help="Encrypt a file or directory")
    enc.add_argument("path", help="Path to file or directory to encrypt")
    enc.add_argument("--output", "-o", help="Override output directory")

    dec = subparsers.add_parser("decrypt", help="Decrypt a file or directory")
    dec.add_argument("path", help="Path to file or directory to decrypt")
    dec.add_argument("--output", "-o", help="Override output directory")

    clear = subparsers.add_parser("clear", help="Delete all plaintext files (with pause & lock)")
    clear.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    for cmd in ["start", "stop", "restart", "status", "enable", "disable"]:
        p = subparsers.add_parser(cmd, help=f"{cmd.capitalize()} a systemd user service")
        p.add_argument("--service", "-s", choices=["daemon", "clear", "all"], default="all",
                       help="Target service to control")

    _install = subparsers.add_parser("install", help="Install EncryptedSync (user services)")

    _uninstall = subparsers.add_parser("uninstall", help="Uninstall EncryptSync and services")
    _uninstall.add_argument("--force", "-f", action="store_true", help="Force uninstall without confirmation")

    _edit = subparsers.add_parser("edit", help="Edit configuration file")
    _edit.add_argument("--no-restart", action="store_true", help="Do not restart the daemon after editing")

    subparsers.add_parser("run", help="Run the EncryptSync daemon manually (CLI mode)")

    args = parser.parse_args()
    if args.version:
        print(f"EncryptSync version {get_version()}")
        raise SystemExit(0)

    if args.command is None:
        parser.print_help()
        raise SystemExit(0)

    if args.command in {"encrypt", "decrypt", "clear"}:
        config = load_config()

    if args.command in {"start", "stop", "restart", "enable", "disable", "status", "install"}:
        if not is_systemd_available():
            logger.error("systemd n'a pas été détecté. Ces commandes nécessitent systemd.")
            raise SystemExit(1)

    if args.command == "encrypt":
        encrypt_path(args.path, config, output_override=args.output)

    elif args.command == "decrypt":
        decrypt_path(args.path, config, output_override=args.output)

    elif args.command == "install":
        install()

    elif args.command == "uninstall":
        uninstall(force=args.force)

    elif args.command == "clear":
        clear_plain(config, confirm=not args.yes)

    elif args.command == "edit":
        edit(restart=not args.no_restart)

    elif args.command in {"start", "stop", "restart", "status", "enable", "disable"}:
        bases_map = {
            "daemon": ["encryptsync"],
            "clear": ["encryptsync-clear"],
            "all": ["encryptsync", "encryptsync-clear"],
        }
        bases = bases_map[args.service]

        if args.command == "status":
            if args.service == "all":
                for base in ["encryptsync", "encryptsync-clear"]:
                    print_service_status(base)
                    print_service_enabled(base)
            else:
                base = "encryptsync" if args.service == "daemon" else "encryptsync-clear"
                print_service_status(base)
                print_service_enabled(base)
        else:
            ok = True
            for base in bases:
                ok &= systemctl_cmd(args.command, base)
            raise SystemExit(0 if ok else 1)

    elif args.command == "run":
        start_program()


if __name__ == "__main__":
    main()