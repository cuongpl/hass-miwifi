import logging

import os
from logging.handlers import RotatingFileHandler

log_dir = "/config/custom_components/miwifi/Logs"
os.makedirs(log_dir, exist_ok=True)

_LOGGER = logging.getLogger("miwifi")
_LOGGER.setLevel(logging.DEBUG)


def add_handler(level, filename):
    path = os.path.join(log_dir, filename)
    handler = RotatingFileHandler(path, maxBytes=5_000_000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # Filtro para que solo se registren logs de ese nivel
    handler.addFilter(lambda record: record.levelno == level)

    _LOGGER.addHandler(handler)


# Añadir handlers por nivel
add_handler(logging.DEBUG, "miwifi_debug.log")
add_handler(logging.INFO, "miwifi_info.log")
add_handler(logging.WARNING, "miwifi_warning.log")
add_handler(logging.ERROR, "miwifi_error.log")
add_handler(logging.CRITICAL, "miwifi_critical.log")

__all__ = ["_LOGGER"]
