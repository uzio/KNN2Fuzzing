import logging


class ICSLogger(object):
    logger = None
    log_file = 'fuzz.log'

    @classmethod
    def get_logger(cls):
        if cls.logger is None:
            logger = logging.getLogger('ics-fuzzer')
            logger.setLevel(logging.INFO)

            console_handler = logging.StreamHandler()
            console_format = logging.Formatter('[%(levelname)-8s][%(module)s.%(funcName)s] %(message)s')
            console_handler.setFormatter(console_format)

            file_handler = logging.FileHandler(cls.log_file)
            file_format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] -> %(message)s')
            file_handler.setFormatter(file_format)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            cls.logger = logger
        return cls.logger
