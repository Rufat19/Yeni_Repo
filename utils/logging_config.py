"""Logging configuration for Alien_BiBOT.

Bu modul layihə üçün mərkəzləşdirilmiş loglama qurğusunu təmin edir.
- Fayllara yazma: logs/bot.log (RotatingFileHandler)
- Konsola da (StreamHandler) çıxış verir

Istifadə:
    from utils.logging_config import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Bot başladı")
"""
import logging
from logging.handlers import RotatingFileHandler
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "bot.log")


def setup_logging(level=logging.INFO, max_bytes=5 * 1024 * 1024, backup_count=3):
    """Setup root logger with rotating file handler and console handler.

    - level: default INFO
    - max_bytes: rotate after ~5MB
    - backup_count: keep few rotated files
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = logging.Formatter(fmt)

    # File handler (rotating)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers on repeated setup calls
    handlers_paths = set()
    for h in list(root.handlers):
        try:
            handlers_paths.add(getattr(h, "baseFilename", None))
        except Exception:
            pass

    if os.path.abspath(LOG_FILE) not in handlers_paths:
        root.addHandler(file_handler)

    # add console handler if not present
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(console_handler)

    # Add a noise-suppression filter to reduce benign but noisy errors
    class NoiseFilter(logging.Filter):
        """Filter out known noisy messages that are not actionable for the bot.

        Examples suppressed:
        - pydantic InlineKeyboardMarkup ValidationError stack traces when empty inline_keyboard is used
        - Other known benign validation messages
        """
        def filter(self, record: logging.LogRecord) -> bool:
            # Only apply aggressive suppression to specific noisy loggers to avoid hiding
            # unrelated messages. Check logger name prefixes first.
            logger_name = getattr(record, "name", "") or ""
            noisy_prefixes = ("pydantic", "aiogram")
            if not any(logger_name.startswith(p) for p in noisy_prefixes):
                return True

            # Only for those loggers apply regex-based suppression of the specific
            # InlineKeyboardMarkup validation messages.
            try:
                msg = record.getMessage()
            except Exception:
                return True

            import re

            # Pattern 1: pydantic InlineKeyboardMarkup validation header
            if re.search(r"ValidationError:\s*1 validation error for InlineKeyboardMarkup", msg):
                return False

            # Pattern 2: missing inline_keyboard field mention
            if re.search(r"Field required.*inline_keyboard", msg, re.IGNORECASE):
                return False

            return True

    # Attach filter to root logger so it applies to handlers
    root.addFilter(NoiseFilter())


def get_logger(name=None):
    return logging.getLogger(name)
