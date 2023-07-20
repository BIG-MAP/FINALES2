import logging
import pathlib


class loggerConfig:
    def __init__(self):
        # logging.config.fileConfig('logging.conf')

        DIRPATH_THIS = pathlib.Path(__file__).parent.resolve()
        FINALES_LOG_PATH = f"{DIRPATH_THIS}/finales_log.log"

        logger = logging.getLogger("FINALES")

        # Add information to log beyond  sys.stderr
        stream = logging.StreamHandler()
        logging.root.setLevel(logging.NOTSET)

        # Formatting
        formatter = "%(asctime)s. %(name)s|%(levelname)s| %(message)s"
        dateFormat = "%m/%d/%Y %I:%M:%S %p"
        logging.basicConfig(
            format=formatter, datefmt=dateFormat, filename=FINALES_LOG_PATH
        )

        formatter = logging.Formatter(formatter, dateFormat)
        stream.setFormatter(formatter)
        logger.addHandler(stream)

        self.logger = logger

    def get_logger(self):
        return self.logger
