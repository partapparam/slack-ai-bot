import logging
logging.basicConfig(level=logging.DEBUG)
from slack_bolt import App
from slack_bolt import (Say, Respond, Ack)
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore
from typing import (Dict, Any)
from slack_sdk.web import WebClient, SlackResponse
from flask import Flask, request, make_response
import json
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
load_dotenv()
import os

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


from flask import Flask, request

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    print('events hit')
    return handler.handle(request)

@flask_app.route('/slack/install')
def slack_install():
    print('getting slack install')
    return


# Issue and consume state parameter value on the server-side.
state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
# Persist installation data and lookup it by IDs.
installation_store = FileInstallationStore(base_dir="./data")

@flask_app.route('/slack/oauth_redirect')
def slack_oauth():
    # Retrieve the auth code and state from the request params
    if request.args['code']:
        # Verify the state parameter
        # if state_store.consume(request.args["state"]):
        if request.args['code']:
            client = WebClient()  # no prepared token needed for this
            # Complete the installation by calling oauth.v2.access API method
            oauth_response = client.oauth_v2_access(
                client_id=SLACK_CLIENT_ID,
                client_secret=SLACK_CLIENT_SECRET,
                code=request.args["code"]
            )
            installed_enterprise = oauth_response.get("enterprise") or {}
            is_enterprise_install = oauth_response.get("is_enterprise_install")
            installed_team = oauth_response.get("team") or {}
            installer = oauth_response.get("authed_user") or {}
            incoming_webhook = oauth_response.get("incoming_webhook") or {}
            bot_token = oauth_response.get("access_token")
            # NOTE: oauth.v2.access doesn't include bot_id in response
            bot_id = None
            enterprise_url = None
            if bot_token is not None:
                auth_test = client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]
                if is_enterprise_install is True:
                    enterprise_url = auth_test.get("url")

            installation = Installation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=installed_enterprise.get("id"),
                enterprise_name=installed_enterprise.get("name"),
                enterprise_url=enterprise_url,
                team_id=installed_team.get("id"),
                team_name=installed_team.get("name"),
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=oauth_response.get("bot_user_id"),
                bot_scopes=oauth_response.get("scope"),  # comma-separated string
                user_id=installer.get("id"),
                user_token=installer.get("access_token"),
                user_scopes=installer.get("scope"),  # comma-separated string
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel=incoming_webhook.get("channel"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
                is_enterprise_install=is_enterprise_install,
                token_type=oauth_response.get("token_type"),
            )
            print(installation)
            breakpoint()
            # Store the installation
            installation_store.save(installation)

            return "Thanks for installing this app!"
        else:
            return make_response(f"Try the installation again (the state value is already expired)", 400)

    error = request.args["error"] if "error" in request.args else ""
    return make_response(f'asdfsdaf {error}', 400)


@flask_app.route('/slack/success')
def success():
    return 'it wroked'