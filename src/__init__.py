from flask import Flask, request

def create_app():
    flask_app = Flask(__name__)
    handler = SlackRequestHandler(app)
    # Issue and consume state parameter value on the server-side.
    state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
    # Persist installation data and lookup it by IDs.
    installation_store = FileInstallationStore(base_dir="./data")

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        print('events hit')
        return handler.handle(request)

    @flask_app.route('/slack/install')
    def slack_install():
        print('getting slack install')
        # Generate a random value and store it on the server-side
        state = state_store.issue()
        # https://slack.com/oauth/v2/authorize?state=(generated value)&client_id={client_id}&scope=app_mentions:read,chat:write&user_scope=search:read
        url = authorize_url_generator.generate(state)
        return f'<a href="{html.escape(url)}">' \
            f'<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'


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
    
    return flask_app