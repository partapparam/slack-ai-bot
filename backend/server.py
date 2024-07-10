from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union, List
from gpt_researcher.master.agent import GPTResearcher
from gpt_researcher.master.source import Source
import json
import datetime

app = FastAPI()

class Body(BaseModel):
    """Represents the body of a POST request

    Attributes:
        query(str): The query to search
        request_id(Union[str, None]): The unique identifier for the research request.
        max_resources(Union[int, None]): The number of scraped resources to return - Optional
    """

    query: str
    request_id: Union[str, None] = None
    max_resources: Union[int, None] = None
