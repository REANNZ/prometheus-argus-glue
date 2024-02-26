# Based off https://gitlab.sikt.no/cnaas/mist-argus

from flask import Flask, request

import logging
import os
import promargus.client
import traceback


app = Flask(__name__)
app.config.from_pyfile(os.environ['PROM_ARGUS_SETTINGS'])


@app.route("/", methods=["POST"])
def webhook():
    req_data = request.get_json()
    app.logger.debug("Payload received: %r", req_data)
    try:
        for alert in req_data["alerts"]:
            promargus.client.handle_alert(alert)
    except Exception as error:
        error_type = type(error).__name__
        if error_type == 'ClientConnectionError':
            return {"success": False}, 503, {"Content-Type": "application/json"}
        elif error_type == 'AuthError':
            return {"success": False}, 401, {"Content-Type": "application/json"}
        else:
            traceback.print_exc()
            return {"success": False}, 500, {"Content-Type": "application/json"}

    return {"success": True}, 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True, debug=True)
else:
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
