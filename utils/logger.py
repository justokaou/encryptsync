import logging
import sys, os
from pathlib import Path

def get_log_path(name: str) -> str:
    if os.geteuid() == 0:
        # Root user > use system log directory
        return f"/var/log/encryptsync/{name}.log"
    else:
        # Normal user > use local user directory
        return str(Path.home() / ".encryptsync" / "logs" / f"{name}.log")

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Avoid duplicate handlers if called multiple times

    logger.setLevel(logging.INFO)

    log_path = get_log_path(name)

    # Create log dir if needed
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    # File handler
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Stream handler (for stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
