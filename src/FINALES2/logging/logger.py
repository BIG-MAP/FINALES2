import logging

# Define through declarative class for mypy segmantic pass
from sqlalchemy.ext.declarative import DeclarativeMeta

from FINALES2.config import get_configuration

LoggerBase: DeclarativeMeta = logging.getLoggerClass()


class LoggerExtension(LoggerBase):
    def __init__(self, name):
        super().__init__(name)

    def raise_value_error(self, logger, msg):
        logger.error("ValueError", stack_info=True)
        raise ValueError(msg)


class loggerConfig:
    def __init__(self):
        logging.setLoggerClass(LoggerExtension)
        config = get_configuration()
        FINALES_LOG_PATH = config.safeget_logpath()

        logger = logging.getLogger("FINALES")

        # Add information to log beyond  sys.stderr
        stream = logging.StreamHandler()
        logging.root.setLevel(logging.NOTSET)

        # Formatting
        formatter = "%(asctime)s. %(name)s|%(levelname)s| %(message)s"
        dateFormat = "%d/%m/%Y %I:%M:%S %p %Z"

        logging.basicConfig(
            format=formatter, datefmt=dateFormat, filename=FINALES_LOG_PATH
        )

        formatter = logging.Formatter(formatter, dateFormat)
        stream.setFormatter(formatter)
        logger.addHandler(stream)

        self.logger = logger

    def get_logger(self):
        return self.logger


def raise_value_error(logger, msg):
    logger.error("ValueError", stack_info=True)
    raise ValueError(msg)
