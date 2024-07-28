from pydantic import BaseModel
from typing import Union, List
from slack_bolt.async_app import AsyncApp
from fastapi import FastAPI, HTTPException, Request
from slack_bolt import (Say, Respond, Ack)
from typing import (Dict, Any)
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from dotenv import load_dotenv
import os
import json
import logging
from src.researcher.master import Researcher
# logging.basicConfig(level=logging.DEBUG)
load_dotenv()

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

class ResearchResult(BaseModel):
    """Represents the result of a research job conducted by a GPTResearcher instance.

    Attributes:
        request_id(Union[str, None]): The unique identifier for the research request.
        query (str): The original query string.
        research_start_timestamp (datetime): The timestamp when the research started, in UTC.
        research_end_timestamp (datetime): The timestamp when the research ended, in UTC.
        results (List[dict]): A list of dictionaries, each representing a source used in the research. Each dict should contain keys corresponding to the basic JSON representation of a source model.
    """

    request_id: Union[str, None] = None
    query: str
    research_start_timestamp: str
    research_end_timestamp: str
    results: List[dict]

SLACK_BOT_TOKEN = os.getenv(key='SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET=os.getenv(key='SLACK_SIGNING_SECRET')


app = AsyncApp(token=SLACK_BOT_TOKEN,
          signing_secret=SLACK_SIGNING_SECRET)
app_handler = AsyncSlackRequestHandler(app)

@app.event("app_mention")
async def app_mentioned(body, say):
    await say("Starting research for")
    print('body of slack', body)
    researcher = Researcher(query='who is lebron  james')
    await researcher.conduct_research()
    await say('Research is done')
    report = await researcher.write_report()
    print(report)
    return report



api = FastAPI()

@api.post("/slack/events")
async def endpoint(req: Request):
    results = await app_handler.handle(req)
    print('request results', results)
    return results