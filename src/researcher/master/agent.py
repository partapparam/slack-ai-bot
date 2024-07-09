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
        Runs the Researcher to conduct research
        """
        print(f"Research started on '{self.query}")
        # Generate Agent
        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(query=self.query, self.cfg)
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
            *[self.process_sub_query(sub_query) for sub_query in self.sub_queries]
        )

        return context