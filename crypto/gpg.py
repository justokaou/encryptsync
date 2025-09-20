from pathlib import Path
import os, tempfile, subprocess

def encrypt_file(input_path, output_dir, gpg_key, base_dir, logger):
    # Relative path of the input file from the base directory
    rel = os.path.relpath(input_path, base_dir)
    

    # New output path in the encrypted directory
    out_final = Path(output_dir) / (rel + ".gpg")
    out_final.parent.mkdir(parents=True, exist_ok=True)

    # Temporary file path in the same directory as the final output
    fd, tmp_path = tempfile.mkstemp(prefix=".enc_", suffix=".tmp", dir=str(out_final.parent))
    os.close(fd)

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(out_final), exist_ok=True)

    try:
        # GPG command to encrypt the file
        subprocess.run([
            "gpg", "--batch", "--yes",
            "--trust-model", "always",
            "--encrypt", "--recipient", gpg_key,
            "--output", tmp_path,
            input_path
        ], check=True)
        
        with open(tmp_path, "rb") as f:
            os.fsync(f.fileno())
        dirfd = os.open(out_final.parent, os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)

        os.replace(tmp_path, out_final)
        logger.info(f"[encrypt] {input_path} > {out_final}")
    
    except Exception as e:
        # If any error occurs, remove the temporary file
        try: os.unlink(tmp_path)
        except FileNotFoundError: pass
        raise

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