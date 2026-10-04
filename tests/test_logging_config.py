"""Tests for package-wide logging configuration."""

import io
import logging
import sys

from wavhost.logging_config import PACKAGE_LOGGER_NAME, get_logger, setup_logger


def test_setup_module_logger_uses_package_handler(monkeypatch):
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    module_logger = logging.getLogger("wavhost.test_logging_child")

    old_package_handlers = list(package_logger.handlers)
    old_package_level = package_logger.level
    old_package_propagate = package_logger.propagate
    old_module_handlers = list(module_logger.handlers)
    old_module_level = module_logger.level
    old_module_propagate = module_logger.propagate
    stream = io.StringIO()
    try:
        package_logger.handlers.clear()
        module_logger.handlers.clear()
        monkeypatch.setattr(sys, "stdout", stream)

        configured = setup_logger(module_logger.name, level=logging.INFO)
        get_logger("wavhost.backends").info("backend logging visible")

        assert configured is module_logger
        assert len(package_logger.handlers) == 1
        assert package_logger.level == logging.INFO
        assert package_logger.propagate is False
        assert module_logger.handlers == []
        assert module_logger.level == logging.NOTSET
        assert module_logger.propagate is True
        assert module_logger.getEffectiveLevel() == logging.INFO
        assert "backend logging visible" in stream.getvalue()
    finally:
        package_logger.handlers[:] = old_package_handlers
        package_logger.setLevel(old_package_level)
        package_logger.propagate = old_package_propagate
        module_logger.handlers[:] = old_module_handlers
        module_logger.setLevel(old_module_level)
        module_logger.propagate = old_module_propagate
