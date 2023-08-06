import logging

from FINALES2.config import get_configuration


class loggerConfig:
    def __init__(self):
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
