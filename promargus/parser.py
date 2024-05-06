from dateutil import parser
from flask import current_app

import re


def parse_alert(alert):
    start_time = parser.parse(alert["startsAt"])
    source_incident_id = "%s_%d" % (
        alert["fingerprint"],
        int(start_time.timestamp()),
    )

    tags = {}
    severity = None

    if isinstance(alert["labels"], dict):
        current_app.logger.debug("Converting labels to tags for alert")
        tags = process_tags(alert["labels"].items())
        current_app.logger.debug("Determining severity")
        severity = get_severity(tags)
        alertname = tags.get('alertname', 'Alert')
        tags = prune_tags(tags)
    if severity is None:
        severity = current_app.config.get("ARGUS_SEVERITY_DEFAULT", 5)
        current_app.logger.debug(
            "No match for severity, applying default severity %s", severity
        )

    description = alert["annotations"]["summary"]

    parsed_alert = {
        "status": alert["status"],
        "level": severity,
        "description": f'{alertname}: {description}',
        "tags": tags,
        "details_url": alert["generatorURL"],
        "source_incident_id": source_incident_id,
        "start_time": start_time,
        "end_time": (
            "infinity" if alert["status"] == "firing" else parser.parse(alert["endsAt"])
        ),
    }

    current_app.logger.debug("Parsed alert: %s", parsed_alert["description"])
    return parsed_alert


# Argus will not allows tags with a camelCase key name.
# process_tags(tags) converts the key names to snake_case which Argus allows.
def process_tags(tags):
    clean_tags = {}

    for key, value in tags:
        new_key = re.sub("([a-z0-9])([A-Z])", r"\1_\2", key).lower()
        clean_tags[new_key] = value

    return clean_tags


def get_severity(tags):
    severity_config = current_app.config.get("ARGUS_SEVERITY_CONFIG")

    if not severity_config:
        return None

    if not isinstance(severity_config, dict):
        current_app.logger.error("ARGUS_SEVERITY_CONFIG is configured incorrectly")
        return None

    for key_tuple, severity in severity_config.items():
        if tags.get(key_tuple[0]) == key_tuple[1]:
            current_app.logger.debug(
                "Severity set to %s by tag %r", severity, key_tuple
            )
            return severity

    return None


def prune_tags(tags):
    pruned_tags = {}

    exclude_labels = current_app.config.get("ARGUS_EXCLUDE_TAGS")

    if exclude_labels is None:
        return tags

    for key, value in tags.items():
        if key not in exclude_labels:
            pruned_tags[key] = value

    return pruned_tags
