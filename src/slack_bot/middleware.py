@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    print('middleware')
    return next()