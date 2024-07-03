import asyncio
import time
from researcher.master.functions import *
from datetime import datetime
from typing import Union

class Researcher:
    """
        Our Research Agent
    """
    def __init(self):
        pass


    async def conduct_research(self):
        """
        Runs the GPT Researcher to conduct research
        """
        print(f"🔎 Running research for '{self.query}'...")

        # Generate Agent
        if not (self.agent and self.role):
            self.agent, self.role = await choose_agent(query=self.query, self.cfg)

        # If specified, the researcher will use the given urls as the context for the research.
        if self.source_urls:
            self.context = await self.get_context_by_urls(self.source_urls)
        else:
            self.context = await self.get_context_by_search(self.query)

        time.sleep(2)
        return self
