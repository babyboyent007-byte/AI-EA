import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_dir: Path, level=logging.INFO):
    """Configures a professional multi-handler logger for institutional telemetry."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'{name.lower()}.log'
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')

        # File Output
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger