import os
from typing import Dict
from urllib.parse import unquote, urlparse
import requests


def parse_file_name(url: str) -> str:
    parsed_url = urlparse(url)
    clean_path = parsed_url.path  # this excludes query params
    file_name = os.path.basename(clean_path)
    file_name = unquote(file_name)

    return file_name


def download_files(urls: list[str], destination: str) -> list[Dict[str, str]]:
    """Download files from the given URLs and save them to specified destination."""
    if not os.path.exists(destination):
        os.makedirs(destination)

    if not urls:
        raise ValueError("The list of URLs is empty. Please provide valid URLs.")

    downloaded_files_paths = []

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()

            file_name = os.path.join(destination, parse_file_name(url))
            with open(file_name, "wb") as file:
                file.write(response.content)

            downloaded_files_paths.append(
                {"url": url, "success": True, "file_path": file_name}
            )
        except Exception as e:
            downloaded_files_paths.append(
                {"url": url, "success": False, "error": str(e)}
            )
    return downloaded_files_paths


def cleanup_files(path: str):
    # Delete files that has image
    pass
