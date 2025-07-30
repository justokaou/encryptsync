import subprocess
import os

def encrypt_file(input_path, output_dir, recipient):
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, filename + ".gpg")

    cmd = [
        "gpg",
        "--trust-model", "always",
        "--batch",
        "--yes",
        "--encrypt",
        "-r", recipient,
        "-o", output_path,
        input_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Encrypted {input_path} > {output_path}")
