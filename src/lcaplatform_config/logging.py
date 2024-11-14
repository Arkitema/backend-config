import logging
from lcaplatform_config.monitoring import EndpointFilter
from logging import Logger

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from lcaplatform_config import config

    settings = config.Settings()

LOGGING_CONFIG = None


def _set_configuration() -> str:
    """Uploads, sets logging configuration file based on telemetry parameter

    Returns:
        str: telemetry or default
    """
    if settings.ENABLE_TELEMETRY:
        # adding trace id for logging
        logging.config.fileConfig("logging_traces.conf", disable_existing_loggers=False)
        return "telemetry"
    else:
        # default configuration without metrics
        logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
        return "default"


def config_logging(logger_name: str) -> Logger:
    """
    Return Logger based on telemetry parameters
    Args:
        logger_name (str): __name__ parameter

    Returns:
        Logger: 'uvicorn.access' logger with traces or 'defaut' with __name__
    """
    global LOGGING_CONFIG
    if not LOGGING_CONFIG:
        LOGGING_CONFIG = _set_configuration()

    if settings.ENABLE_TELEMETRY:
        logger = logging.getLogger("uvicorn.access")
        logger.addFilter(EndpointFilter())
    else:
        logger = logging.getLogger(logger_name)

    return logger
