from pyargus.client import Client
from pyargus.models import Incident, Event

from datetime import datetime, UTC
from flask import current_app

import promargus.parser


def handle_alert(alert):
    parsed_alert = promargus.parser.parse_alert(alert)
    client = Client(
        api_root_url=current_app.config.get("ARGUS_API_URL"),
        token=current_app.config.get("ARGUS_API_TOKEN"),
    )
    current_app.logger.debug(
        "Check if incident with source incident id: %s already exists in Argus",
        parsed_alert["source_incident_id"],
    )
    incident = get_incident(client, parsed_alert["source_incident_id"])
    if parsed_alert["status"] == "resolved":
        resolve_incident(client, incident, parsed_alert)
    if parsed_alert["status"] == "firing":
        if incident:
            update_incident(client, incident, parsed_alert)
        else:
            create_incident(client, parsed_alert)


def get_incident(client, id_):
    incident = next((client.get_incidents(source_incident_id=id_)), None)
    if incident is not None:
        return incident

    # In the case of multiple monitoring systems, if an alert comes from
    # one but is resolved by another, the start time might be different
    # so the source_incident_id won't match. We can safely assume if an
    # incident is open with the same prefix on the source_incident_id,
    # that this is the incident we want to make changes to.
    current_app.logger.debug(
        "Incident not found with source id: %s. Checking open incidents",
        id_,
    )
    id_prefix = id_.split("_")[0]
    incidents = client.get_incidents(open=True)
    for incident in incidents:
        if id_prefix in incident.source_incident_id:
            return incident
    return None


def resolve_incident(client, incident, parsed_alert):
    if not incident:
        current_app.logger.error(
            "Incident not found. Cannot resolve for incident with source id: %s",
            parsed_alert["source_incident_id"],
        )
        return
    if not incident.open:
        current_app.logger.error(
            "Incident already resolved for incident with source id: %s",
            parsed_alert["source_incident_id"],
        )
        return
    current_app.logger.debug("Resolving incident: %s", parsed_alert["description"])
    client.resolve_incident(incident=incident.pk, timestamp=parsed_alert["end_time"])


def update_incident(client, incident, parsed_alert):
    current_app.logger.debug(
        "Create update event for incident: %s", parsed_alert["description"]
    )
    event = Event(
        description=parsed_alert["description"],
        timestamp=datetime.now(UTC),
        type="OTH",
    )
    client.post_incident_event(incident, event)

    current_app.logger.debug(
        "Updating tags for incident: %s", parsed_alert["description"]
    )
    incident = Incident(
        pk=incident.pk,
        tags=parsed_alert["tags"],
    )
    client.update_incident(incident)


def create_incident(client, parsed_alert):
    current_app.logger.debug(
        "Creating new incident for incident: %s", parsed_alert["description"]
    )
    incident = Incident(
        description=parsed_alert["description"],
        start_time=parsed_alert["start_time"],
        details_url=parsed_alert["details_url"],
        tags=parsed_alert["tags"],
        level=parsed_alert["level"],
        source_incident_id=parsed_alert["source_incident_id"],
    )

    client.post_incident(incident)
