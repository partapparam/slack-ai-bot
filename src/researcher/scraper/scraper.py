from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

import requests

from src.researcher.scraper.beautiful_soup.beautiful_soup import (
    BeautifulSoupScraper,
)


class Scraper:
    """
    Scraper class to extract the content from the links
    """

    def __init__(self, urls, query, user_agent, scraper):
        """
        Initialize the Scraper class.
        Args:
            urls: list[str] - The list of URLs to scrape
        """
        self.urls = urls
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.scraper = scraper
        self.query = query

    