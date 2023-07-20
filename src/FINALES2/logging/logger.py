import logging
import pathlib


class loggerConfig:
    def __init__(self):
        # logging.config.fileConfig('logging.conf')

        DIRPATH_THIS = pathlib.Path(__file__).parent.resolve()
        FINALES_LOG_PATH = f"{DIRPATH_THIS}/sql_log.log"

        logger = logging.getLogger("CIRE")

        ch = logging.StreamHandler()
        logging.root.setLevel(logging.NOTSET)

        formatter = "%(asctime)s. %(name)s|%(levelname)s| %(message)s"
        dateFormat = "%m/%d/%Y %I:%M:%S %p"
        logging.basicConfig(
            format=formatter, datefmt=dateFormat, filename=FINALES_LOG_PATH
        )

        formatter = logging.Formatter(formatter, dateFormat)

        ch.setFormatter(formatter)
        logger.addHandler(ch)

        self.logger = logger

    def get_logger(self):
        return self.logger
