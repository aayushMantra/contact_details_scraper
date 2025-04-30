# classification_service/downloader.py
import requests
from config import USER_AGENT

def download_page(url):
    """
    Download the HTML content of a given URL.
    Args:
        url (str): The URL to download.
    Returns:
        str: The HTML content, or None if the download fails.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        return response.text
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None