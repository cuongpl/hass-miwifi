import logging
import os
from logging.handlers import RotatingFileHandler
from homeassistant.helpers import storage

# Carpeta de logs en /config/miwifi/logs
log_dir = os.path.join(storage.STORAGE_DIR, '..', 'miwifi', 'logs')
os.makedirs(log_dir, exist_ok=True)

_LOGGER = logging.getLogger("miwifi")
_LOGGER.setLevel(logging.NOTSET)

# Handlers por nivel
def add_level_handler(level, filename):
    path = os.path.join(log_dir, filename)
    handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.NOTSET)
    handler.addFilter(lambda record: record.levelno == level)
    _LOGGER.addHandler(handler)

# Añadimos los logs siempre activos
add_level_handler(logging.INFO, "miwifi_info.log")
add_level_handler(logging.WARNING, "miwifi_warning.log")
add_level_handler(logging.ERROR, "miwifi_error.log")
add_level_handler(logging.CRITICAL, "miwifi_critical.log")
add_level_handler(logging.DEBUG, "miwifi_debug.log")  # Se activa si el nivel global es DEBUG

__all__ = ["_LOGGER"]

# Mensaje de inicio
if _LOGGER.isEnabledFor(logging.DEBUG):
    _LOGGER.info("✅ MiWiFi started in DEBUG mode")
else:
    _LOGGER.info("ℹ️ MiWiFi started in non-debug mode (INFO or higher)")
