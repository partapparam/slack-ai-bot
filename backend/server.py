from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union, List
from researcher.master.agent import Researcher
import json
import datetime
from slack_bolt import App
from slack_bolt import (Say, Respond, Ack)
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.state_store import FileOAuthStateStore
from typing import (Dict, Any)
from slack_sdk.web import WebClient, SlackResponse
from flask import Flask, request, make_response
import json
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level=logging.DEBUG)
import os
import json
import yaml
import html


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

# 
