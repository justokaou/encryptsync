import subprocess
import os

def encrypt_file(input_path, output_dir, gpg_key, base_dir, logger):
    # 1. Relative path of the input file from the base directory
    rel_path = os.path.relpath(input_path, base_dir)

    # 2. New output path in the encrypted directory
    output_path = os.path.join(output_dir, rel_path + ".gpg")

    # 3. Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 4. GPG command to encrypt the file
    cmd = [
        "gpg",
        "--trust-model", "always",
        "--batch",
        "--yes",
        "--encrypt",
        "-r", gpg_key,
        "-o", output_path,
        input_path
    ]
    subprocess.run(cmd, check=True)
    logger.info(f"[encrypt] {input_path} > {output_path}")


def decrypt_file(input_path, output_dir, base_dir, logger):
    # Rebuild relative path
    rel_path = os.path.relpath(input_path, base_dir).replace(".gpg", "")
    output_path = os.path.join(output_dir, rel_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "gpg",
        "--batch",
        "--yes",
        "--decrypt",
        "-o", output_path,
        input_path
    ]

    result = subprocess.run(cmd, capture_output=True)

    if result.returncode == 0:
        logger.info(f"[decrypt] {input_path} > {output_path}")
    else:
        logger.error(f"[Error] Failed to decrypt {input_path}")
        logger.error(result.stderr.decode())