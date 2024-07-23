import asyncio
import time
from src.researcher.context.compression import ContextCompressor
from src.researcher.master.functions import *
from src.researcher.memory import Memory
from src.researcher.config import Config
from datetime import datetime
from typing import Union

class Researcher:
    """
        Our Research Agent
    """
    def __init__(
            self,
            query: str,
            agent = None,
            role = None,
            subqueries: list = [],
            source_urls: list[str] = [],
            request_id: Union[str, None] = None
            ):
        """
        Initialize the Researcher class.
        Args:
            query: str
            agent
            role
            subqueries: list
            source_urls: set
            request_id: Union[str, None]
        """
        self.query = query
        self.agent = agent
        self.role = role
        self.source_urls = source_urls
        self.request_id = request_id
        self.subqueries: list = [] 
        self.cfg = Config()
        self.retriever = get_retriever(self.cfg.retriever)
        self.context = []   


    async def conduct_research(self):
        """
        Runs the Researcher to conduct research
        """
        print(f"Research started on {self.query}")
        # Generate Agent
        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(query=self.query, cfg=self.cfg)
        self.context = await self.get_context_by_search(self.query)
        return self


    async def get_context_by_search(self, query):
        """
           Generates the context for the research query.
           Creates subqueries using decomposition.
           Searches and scrapes for each query
        Returns:
            context: List of context
        """
        context = []

        # error handling in the event decomposition fails
        try:
            # Generate Sub-Queries including original query
            self.subqueries = await get_sub_queries(
                query, self.role, self.cfg, self.parent_query, self.report_type
            )
        except Exception as e:
            print(f"Error in get_sub_queries: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            self.subqueries = [query]

        print(f"I will conduct my research based on the following queries: {self.subqueries}...")

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(
            *[self.process_sub_query(sub_query) 
              for sub_query in self.subqueries]
        )

        return context
    

    async def process_sub_query(self, sub_query: str):
        """Finds and scrapes urls based on the subquery and gathers context.
        Args:
            sub_query (str): The sub-query generated from the original query

        Returns:
            str: The context gathered from search
        """
        print(f'Running research for {sub_query}..."')

        scraped_sites = await self.scrape_sites_by_query(sub_query)
        # get similar content from the compressor
        content = await self.get_similar_content_by_query(sub_query, scraped_sites)

        if content:
            print(f'LOGS: {content}')
        else:
            print(f'LOGS: No content was found for {sub_query}')
        return content


    async def get_new_urls(self, url_set_input):
        """Gets the new urls from the given url set.
        Args: url_set_input (set[str]): The url set to get the new urls from
        Returns: list[str]: The new urls from the given url set
        """

        new_urls = []
        for url in url_set_input:
            if url not in self.source_urls:
                print(f'LOGS: Adding source url to research: {url}\n"')
                self.source_urls.add(url)
                new_urls.append(url)
        return new_urls
    

    async def scrape_sites_by_query(self, sub_query):
        """
        Searches and scrapes a sub-query
        Args:
            sub_query:

        Returns:
            Summary
        """
        # Get Urls 
        retriever = self.retriever(sub_query)
        search_results = retriever.search(
            max_results=self.cfg.max_search_results_per_query
        )
        new_search_urls = await self.get_new_urls(
            [url.get("href") for url in search_results]
        )

        # Scrape Urls
        print(f'LOGS: Scraping URLS {new_search_urls}...\n')
        sources = scrape_urls(new_search_urls, sub_query, self.cfg)

        scraped_content_results = [
            {"url": source.url, "raw_content": source.parsed_text}
            for source in sources
        ]

        return scraped_content_results

# create context compressor
    async def get_similar_content_by_query(self, query, pages):
        print(f'LOGS: Getting relevant content based on query: {query}...\n')
        # Summarize Raw Data
        context_compressor = ContextCompressor(
            documents=pages, embeddings=self.memory.get_embeddings()
        )
        # # Run Tasks
        return context_compressor.get_context(query, max_results=8)

    ########################################################################################
