#!/usr/bin/env python3
import argparse
from utils.config import load_config

from cli.encrypt import encrypt_path
from cli.decrypt import decrypt_path
from cli.clear import clear_plain
from cli.service import systemctl_cmd, status_cmd, print_service_status, print_service_enabled
from cli.install import install, edit

def main():
    parser = argparse.ArgumentParser(description="EncryptSync control utility")
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
        p = subparsers.add_parser(cmd, help=f"{cmd.capitalize()} a systemd service (sudo required for start/stop)")
        p.add_argument(
            "--service", choices=["daemon", "clear", "all"], default="main",
            help="Target service to control"
        )

    _install = subparsers.add_parser("install", help="Install EncryptedSync and services")
    _install.add_argument("--force", "-f" , action="store_true", help="Force reinstall services")

    _edit = subparsers.add_parser("edit", help="Edit configuration file")
    _edit.add_argument("--no-restart", action="store_true", help="Do not restart the daemon after editing")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        exit(0)
    config = load_config()

    if args.command == "encrypt":
        encrypt_path(args.path, config, output_override=args.output)
    elif args.command == "decrypt":
        decrypt_path(args.path, config, output_override=args.output)
    elif args.command == "install":
        install(force=args.force)
    elif args.command == "clear":
        clear_plain(config, confirm=not args.yes)
    elif args.command == "edit":
        edit(restart=args.no_restart)
    elif args.command in {"start", "stop", "restart", "status", "enable", "disable"}:
        if args.command == "status":
            if args.service == "all":
                status_cmd()
            else:
                target = "encryptsync" 
                if args.service == "daemon":
                    print_service_status(target, target)
                elif args.service == "clear":
                    target = "encryptsync-clear"
                    print_service_enabled(target, target)
        else:
            service_map = {
                "daemon": ["encryptsync"],
                "clear": ["encryptsync-clear"],
                "all": ["encryptsync", "encryptsync-clear"]
            }
            targets = service_map.get(args.service, [])
            
            for target in targets:
                systemctl_cmd(args.command, target)


if __name__ == "__main__":
    main()