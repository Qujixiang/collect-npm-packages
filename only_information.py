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

        i=1
        while last_package_published_day >= day and i>0:
            i-=1
            common_logger.info(
                f'Get package information from page {page_num} started.')
            data = get_one_page_package_info(page_num)
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
                time.sleep(1)
                
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


def get_one_page_package_info(page_num: int, retry_times: int = 3, retry_interval: int = 30) -> Any | None:
    """
    Get one page package information from the `libraries.io`.
    :param page_num: The page number to get package information.
    :param retry_times: The retry times when the request failed.
    :param retry_interval: The retry interval when the request failed.
    :return: The package information. If the request failed, return `None`.
    """
    while retry_times > 0:
        response = requests.get('https://libraries.io/api/search', params={
            'platforms': 'NPM',
            'sort': 'latest_release_published_at',
            'languages': 'JavaScript',
            'per_page': 100,
            'page': page_num,
            'api_key': 'a711409c801d5337ce4758cf94153601'
        })
        if response.status_code != 200:
            common_logger.error(
                f'Request failed with: {response.status_code}')
            retry_times -= 1
            time.sleep(retry_interval)
        else:
            break
    return response.json()


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


if __name__ == '__main__':
    # Get packages information
    package_info = get_package_info(goal_day)
    if not package_info:
        common_logger.error(f'Get package information failed.')
        exit(-1)
    export_package_info(package_info, goal_day)
