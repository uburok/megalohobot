import logging

from settings import LOG_PATH, LOG_LEVEL


def get_logger(name, logpath=None, loglevel=None):
    # Имя лога и уровень логгирования по умолчанию берутся из файла settings.py, если не указаны прямо
    logger = logging.getLogger(name)

    if loglevel:
        logger.setLevel(loglevel)
    else:
        logger.setLevel(LOG_LEVEL)

    fh = logging.FileHandler(logpath) if logpath else logging.FileHandler(LOG_PATH)
    fm = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    fh.setFormatter(fm)
    logger.addHandler(fh)

    return logger

