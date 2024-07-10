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
import json
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level=logging.DEBUG)
import os
import json
import yaml
import html

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


TOKEN = os.getenv('TOKEN')
AUTH = os.getenv('AUTH')
URL = os.getenv(key='URL')
SLACK_BOT_TOKEN = os.getenv(key='SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET=os.getenv(key='SLACK_SIGNING_SECRET')
SLACK_CLIENT_SECRET = os.getenv(key='SLACK_CLIENT_SECRET')
SLACK_CLIENT_ID = os.getenv(key='SLACK_CLIENT_ID')
oauth_settings = OAuthSettings(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    install_path="/slack/install",
)
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    oauth_settings=oauth_settings
)


with open('../manifest.yaml', mode='r') as file:
    config = yaml.safe_load(file)
    
scopes = config['oauth_config']['scopes']['bot']
# Build https://slack.com/oauth/v2/authorize with sufficient query parameters
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=SLACK_CLIENT_ID,
    scopes=scopes,
)


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    print('middleware')
    return next()

@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")

@app.command(command='/modify')
def handle_modify_bot(ack: Ack, body: Dict[str, Any], respond: Respond, context, client, payload, command) -> None:
    """
    Handle the /modify-bot command
    This function modifies the Bots scope and access for questions
    """
    ack()
    channel_id = body['channel_id']
    trigger_id = body['trigger_id']
    print(channel_id, trigger_id)
     # Load modify_bot_template.json payload
    with open(f'./src/templates/file_upload_template.json', 'r') as f:
        view = json.load(f)
    respond(f"{command['text']}")
    client.views_open(trigger_id=trigger_id, view=view)
    breakpoint()


api = FastAPI()

@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)