from pyargus.client import Client
from pyargus.models import Incident, Event

from datetime import datetime
from flask import current_app


def handle_alert(alert):
    client = Client(
        api_root_url=current_app.config.get("ARGUS_API_URL"),
        token=current_app.config.get("ARGUS_API_TOKEN"),
    )
    current_app.logger.debug(
        "Check if incident with source incident id: %s already exists in Argus",
        alert["source_incident_id"],
    )
    incident = get_incident(client, alert["source_incident_id"])
    if alert["status"] == "resolved":
        resolve_incident(client, incident, alert)
    elif incident:
        update_incident(client, incident, alert)
    else:
        create_incident(client, alert)


def get_incident(client, id):
    incident = next((client.get_incidents(source_incident_id=id)), None)
    return incident


def resolve_incident(client, incident, alert):
    if not incident:
        current_app.logger.error(
            "Incident not found. Cannot resolve for incident with source id: %s",
            alert["source_incident_id"],
        )
        return
    if not incident.open:
        current_app.logger.error(
            "Incident already resolved for incident with source id: %s",
            alert["source_incident_id"],
        )
        return
    current_app.logger.debug("Resolving incident: %s", alert["description"])
    client.resolve_incident(incident=incident.pk, timestamp=alert["end_time"])


def update_incident(client, incident, alert):
    current_app.logger.debug(
        "Create update event for incident: %s", alert["description"]
    )
    event = Event(
        description=alert["description"],
        timestamp=datetime.now(),
        type="OTH",
    )
    client.post_incident_event(incident, event)

    current_app.logger.debug("Updating tags for incident: %s", alert["description"])
    incident = Incident(
        pk=incident.pk,
        tags=alert["tags"],
    )
    client.update_incident(incident)


def create_incident(client, alert):
    current_app.logger.debug(
        "Creating new incident for incident: %s", alert["description"]
    )
    incident = Incident(
        description=alert["description"],
        start_time=alert["start_time"],
        details_url=alert["details_url"],
        tags=alert["tags"],
        level=alert["level"],
        source_incident_id=alert["source_incident_id"],
    )

    client.post_incident(incident)
