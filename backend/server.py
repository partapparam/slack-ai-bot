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
    raw_query = body['event']['text']
    cleaned_query = raw_query.split(' ')[1:]
    query = ' '.join(cleaned_query)
    user = body['event']['user']
    print(user)
    researcher = Researcher(query=query)
    await say(f"Hey <@{user}>, I'm starting research on the following topic:  {query}")
    await researcher.conduct_research()
    await say("Research is done, we're writing up a report to summarize our findings.")
    report = await researcher.write_report()
    await say(report)



api = FastAPI()

@api.post("/slack/events")
async def endpoint(req: Request):
    results = await app_handler.handle(req)
    return results