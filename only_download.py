from typing import Any
import json
from datetime import datetime, date, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import requests
from utils import get_logger, split_file, get_requirements_path, get_common_log_path, get_pip_download_log_path, get_packages_path, get_package_info_path


goal_day = date.today() - timedelta(days=1)
common_logger = get_logger('common_logger', get_common_log_path(goal_day))
npm_download_logger = get_logger(
    'npm_download_logger', get_pip_download_log_path(goal_day))


def download_packages(day: date, piece_number: int = 0) -> None:
    """
    Download packages from the `NPM`.
    :param day: The day to download packages.
    :param piece_number: The piece number of the `requirements.txt` file.
    """
    destination_path = get_packages_path(day)
    requirements_file_path = get_requirements_path(day)
    if piece_number > 0:
        requirements_file_path += str(piece_number)
        npm_download_logger.info(
            f'Download packages from {requirements_file_path} started.')
    cmd_install = f'./npm_download.sh {destination_path} {requirements_file_path}'
    npm_download_logger.info(cmd_install)
    p = subprocess.Popen(
        cmd_install, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()

    npm_download_logger.info(output.decode())
    npm_download_logger.error(error.decode())


if __name__ == '__main__':
    # Download packages
    piece_number = 8
    common_logger.info(
        f'Split requirements.txt file into {piece_number} pieces.')
    split_file(get_requirements_path(goal_day), piece_number)

    with ThreadPoolExecutor(max_workers=piece_number) as executor:
        common_logger.info(f'Download packages started.')
        all_tasks = [executor.submit(
            download_packages, goal_day, i + 1) for i in range(piece_number)]
        for future in as_completed(all_tasks):
            future.result()
        common_logger.info(f'Download packages finished.')

        # pre = subprocess.Popen(
        #     './pre_process.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # output, error = pre.communicate()
        # npm_download_logger.info(output.decode())
        # npm_download_logger.error(error.decode())
