from typing import Any
import json
from datetime import datetime, date, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

import requests

from utils import get_logger, split_file, get_requirements_path, get_common_log_path, get_download_log_path, get_packages_path, get_package_info_path


# Load api keys from `data/settings.json`.
with open('data/settings.json', 'r') as f:
    settings = json.load(f)
    api_keys = settings['api_keys']
api_keys_counter = 0
api_keys_length = len(api_keys)
api_key = api_keys[api_keys_counter]

def get_next_api_key() -> str:
    """
    Get next api key from the `api_keys` list.
    """
    global api_keys_counter
    global api_keys_length

    api_keys_counter += 1
    if api_keys_counter == api_keys_length:
        api_keys_counter = 0
    _api_key = api_keys[api_keys_counter]
    common_logger.info(f'Use api key: {_api_key}')
    return _api_key

goal_day = date.today() - timedelta(days=1)
common_logger = get_logger('common_logger', get_common_log_path(goal_day))
npm_download_logger = get_logger(
    'npm_download_logger', get_download_log_path(goal_day))

def get_package_info(day: date) -> list or None:
    """
    Get package information from the `libraries.io`.
    :param day: The day to get package information.
    """
    try:
        package_metadatas = []
        last_package_published_day = day
        package_info_path = get_package_info_path(day)
        page_num = 1

        while last_package_published_day >= day:
            common_logger.info(
                f'Get package information from page {page_num} started.')
            data = get_one_page_package_info(page_num, retry_interval=60)
            if not data:
                raise Exception(
                    f'Get package information from page {page_num} failed.')
            with open(f'{package_info_path}/page_{page_num}.json', 'w') as f:
                json.dump(data, f)
            first_package_metadata = data[0]
            last_package_metadata = data[-1]

            common_logger.info(
                f'First package in page {page_num} published at {first_package_metadata["latest_release_published_at"]}.')
            common_logger.info(
                f'Last package in page {page_num} published at {last_package_metadata["latest_release_published_at"]}.')
            common_logger.info(
                f'Get package information from page {page_num} finished.')

            last_package_published_day = datetime.strptime(
                last_package_metadata['latest_release_published_at'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
            
            if last_package_published_day > day:
                page_num += 1
                common_logger.info(
                f'NOT the goal day.')
                time.sleep(60)
            elif last_package_published_day == day:
                for package_metadata in data:
                    d = datetime.strptime(
                        package_metadata['latest_release_published_at'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                    if d == day:
                        package_metadatas.append(package_metadata)
                    else:
                        break
                page_num += 1
                time.sleep(1)
            else:
                for package_metadata in data:
                    d = datetime.strptime(
                        package_metadata['latest_release_published_at'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                    if d == day:
                        package_metadatas.append(package_metadata)
                    else:
                        break
                    
        common_logger.info(
            f'Get {len(package_metadatas)} packages information.')
        return package_metadatas
    
    except Exception as e:
        common_logger.error(e)
        return None


def get_one_page_package_info(page_num: int, retry_times: int = 10, retry_interval: int = 60) -> Any | None:
    """
    Get one page package information from the `libraries.io`.
    :param page_num: The page number to get package information.
    :param retry_times: The retry times when the request failed.
    :param retry_interval: The retry interval when the request failed.
    :return: The package information. If the request failed, return `None`.
    """
    global api_key
    total_retry_times = retry_times
    while retry_times > 0:
        response = requests.get('https://libraries.io/api/search', params={
            'platforms': 'NPM',
            'sort': 'latest_release_published_at',
            'languages': 'JavaScript',
            'per_page': 100,
            'page': page_num,
            'api_key': api_key
        })
        if response.status_code != 200:
            common_logger.error(
                f'Request failed with: {response.status_code}')
            retry_times -= 1
            api_key = get_next_api_key()
            time.sleep(retry_interval * (total_retry_times - retry_times))
        else:
            break
    return response.json() if response else None

def export_package_info(package_info: list, day: date) -> None:
    """
    Export package information to the `requirements.txt` file.
    :param package_info: The package information to export.
    """
    with open(get_requirements_path(day), 'w') as f:
        for package_metadata in package_info:
            if package_metadata['latest_release_number']:
                f.write('{}@{}\n'.format(
                    package_metadata['name'], package_metadata['latest_release_number']))

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
    cmd_install = f'./download.sh {destination_path} {requirements_file_path}'
    npm_download_logger.info(cmd_install)
    p = subprocess.Popen(
        cmd_install, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    npm_download_logger.info(output.decode())
    npm_download_logger.error(error.decode())

if __name__ == '__main__':
    # Get packages information
    package_info = get_package_info(goal_day)
    if not package_info:
        common_logger.error(f'Get package information failed.')
        exit(-1)
    export_package_info(package_info, goal_day)

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