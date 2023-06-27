import os
from datetime import date
import logging


def get_logger(name: str, log_file: str, level: int = logging.INFO):
    """
    Get logger.
    :param name: The name of logger.
    :param log_file: The log file path.
    :param level: The level of logger.
    :return: The logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh = logging.FileHandler(log_file, mode='w')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def split_file(file_path: str, number: int) -> None:
    """
    Split the document into multiple parts
    :param file_path: file path
    :param number: number of parts
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    file_line = len(lines) // number
    for i in range(number):
        with open(file_path + str(i + 1), 'w', encoding='utf-8') as f:
            if i != number - 1:
                f.writelines(lines[i * file_line:(i + 1) * file_line])
            else:
                f.writelines(lines[i * file_line:])

def get_requirements_path(day: date) -> str:
    """
    Get the path to the requirements file
    :param day: date
    :return: path to the requirements file
    """
    path = f'requirements/{day.year}-{day.month}-{day.day}'
    os.makedirs(path, exist_ok=True)
    return f'{path}/requirements.txt'

def get_common_log_path(day: date) -> str:
    """
    Get the path of the common log file
    :param day: date
    :return: path of the common log file
    """
    path = f'logs/{day.year}-{day.month}-{day.day}'
    os.makedirs(path, exist_ok=True)
    return f'{path}/common.log'

def get_pip_download_log_path(day: date) -> str:
    """
    Get the path of the pip download log file
    :param day: date
    :return: path to pip download log file
    """
    path = f'logs/{day.year}-{day.month}-{day.day}'
    os.makedirs(path, exist_ok=True)
    return f'{path}/pip_download.log'

def get_packages_path(day: date) -> str:
    """
    Get the path to the directory of packages file
    :param day: date
    :return: path to the directory of the packages file
    """
    path = f'packages/{day.year}-{day.month}-{day.day}'
    os.makedirs(path, exist_ok=True)
    return path

def get_package_info_path(day: date) -> str:
    """
    Get the path to the directory of the package information file
    :param day: date
    :return: path to the directory of the package information file
    """
    path = f'data/package_info/{day.year}-{day.month}-{day.day}'
    os.makedirs(path, exist_ok=True)
    return path