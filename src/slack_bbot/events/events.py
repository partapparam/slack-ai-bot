@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")