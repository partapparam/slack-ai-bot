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

    def extract_data_from_link(self, link, session):  # FIXME
        """
        Extracts the data from the link
        """
        source = ""
        try:
            Scraper_to_use = BeautifulSoupScraper
            scraper = Scraper_to_use(link, session)

            source = scraper.scrape()  # returns a source object
            source.query = self.query
            return source

        except Exception as e:
            print('error on extract data = ', e)
            return None
    
    def get_scraper(self, link):
        """
        The function `get_scraper` determines the appropriate scraper class based on the provided link
        or a default scraper if none matches.

        Args:
          link: The `get_scraper` method takes a `link` parameter which is a URL link to a webpage or a
        PDF file. Based on the type of content the link points to, the method determines the appropriate
        scraper class to use for extracting data from that content.

        Returns:
          The `get_scraper` method returns the scraper class based on the provided link. The method
        checks the link to determine the appropriate scraper class to use based on predefined mappings
        in the `SCRAPER_CLASSES` dictionary.
        """

        SCRAPER_CLASSES = {
            "bs": BeautifulSoupScraper,
        }

        scraper_key = None

        # if link.endswith(".pdf"):
        #     scraper_key = "pdf"
        # elif "arxiv.org" in link:
        #     scraper_key = "arxiv"
        # else:
        scraper_key = self.scraper

        scraper_class = SCRAPER_CLASSES.get(scraper_key)
        if scraper_class is None:
            raise Exception("Scraper not found.")

        return scraper_class