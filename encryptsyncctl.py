#!/usr/bin/env python3
import os, time
import argparse
from config import load_config

from cli.encrypt import encrypt_path
from cli.decrypt import decrypt_path
from cli.clear import clear_plain

def main():
    parser = argparse.ArgumentParser(description="EncryptedSync control utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enc = subparsers.add_parser("encrypt", help="Encrypt a file or directory")
    enc.add_argument("path", help="Path to file or directory to encrypt")
    enc.add_argument("--output", "-o", help="Override output directory")

    dec = subparsers.add_parser("decrypt", help="Decrypt a file or directory")
    dec.add_argument("path", help="Path to file or directory to decrypt")
    dec.add_argument("--output", "-o", help="Override output directory")

    clear = subparsers.add_parser("clear", help="Delete all plaintext files (with pause & lock)")

    args = parser.parse_args()
    config = load_config()

    if args.command == "encrypt":
        encrypt_path(args.path, config, output_override=args.output)
    elif args.command == "decrypt":
        decrypt_path(args.path, config, output_override=args.output)
    elif args.command == "clear":
        clear_plain(config)


if __name__ == "__main__":
    main()