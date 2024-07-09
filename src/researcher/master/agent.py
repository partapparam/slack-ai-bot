import asyncio
import time
from researcher.master.functions import *
from researcher.config import Config
from datetime import datetime
from typing import Union

class Researcher:
    """
        Our Research Agent
    """
    def __init(
            self,
            query: str,
            agent = None,
            role = None,
            subqueries: list = [],
            source_urls: list[str] = [],
            request_id: Union[str, None] = None):
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
        self.subqueries: list = []  # NOTE: kyle edit
        self.retriever = get_retriever(self.cfg.retriever)
        self.context = []
        self.cfg = Config(config_path)
    


    async def conduct_research(self):
        """
        Runs the GPT Researcher to conduct research
        """
        print(f"Research started on '{self.query}")
        # Generate Agent
        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(query=self.query, self.cfg)
        ##
        # Get search by using the URLs provided
        ##
        # If specified, the researcher will use the given urls as the context for the research.
        # if self.source_urls:
        #     self.context = await self.get_context_by_urls(self.source_urls)
        # else:
        #     self.context = await self.get_context_by_search(self.query)
        
        #
        #  Setup to search based on query
        self.context = await self.get_context_by_search(self.query)
        return self
