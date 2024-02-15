# Based off https://gitlab.sikt.no/cnaas/mist-argus

from flask import Flask, request
from promargus.client import handle_alert
from promargus.parser import parse_alerts

import logging


app = Flask(__name__)
app.config.from_envvar("PROM_ARGUS_SETTINGS")


@app.route("/", methods=["POST"])
def webhook():
    req_data = request.get_json()
    app.logger.debug("Payload received: %r", req_data)
    for alert in parse_alerts(req_data["alerts"]):
        handle_alert(alert)

    return {"success": True}, 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True, debug=True)
else:
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
