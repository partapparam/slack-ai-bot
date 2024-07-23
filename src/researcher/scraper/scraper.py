from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
import requests

from src.researcher.scraper import BeautifulSoupScraper



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

    def run(self) -> list:
        """
        Extracts the content from the URLs using the specified scraper,
        creates a Source object for each URL, and returns a list of Source objects
        with non-empty parsed text.
        """
        # partial_extract = partial(self.extract_data_from_link, session=self.session)
        # with ThreadPoolExecutor(max_workers=20) as executor:
        #     contents = executor.map(partial_extract, self.urls)
        # res = [content for content in contents if content["raw_content"] is not None]
        # return res

        partial_extract = partial(self.extract_data_from_link, session=self.session)
        with ThreadPoolExecutor(max_workers=20) as executor:
            sources = executor.map(partial_extract, self.urls)

        # The return value from extract_data_from_link is either source or None
        return [source for source in sources if source is not None]
        # return sources
    