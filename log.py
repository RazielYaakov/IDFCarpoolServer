import logging


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s.py - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('IDFCarpoolServer.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(name)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger


# c_handler = logging.StreamHandler()
# c_handler.setLevel(logging.DEBUG)
# c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)

# f_handler = logging.FileHandler('file.log')
# f_handler.setLevel(logging.DEBUG)
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# f_handler.setFormatter(f_format)
#
# logger.addHandler(c_handler)
# logger.addHandler(f_handler)