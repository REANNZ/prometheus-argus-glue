# == Required ==
# Argus api endpoint
# https://argus-server.readthedocs.io/en/latest/api.html
ARGUS_API_URL = "https://example.com/api/v1"

# == Required ==
# Api token for promargus user generated in Argus.
# https://argus-server.readthedocs.io/en/latest/integrations/index.html
ARGUS_API_TOKEN = "secret"

# Default severity for all incidents generated through promargus.
# If not set, defaults to ARGUS_SEVERITY_DEFAULT = 5
# ARGUS_SEVERITY_DEFAULT = 4

# == Optional ==
# Allows promargus to set severity of the incident based on alert labels.
# e.g. `"labels": {"pagepolicy": "always"}`.
# ARGUS_SEVERITY_CONFIG = {
#     ("foo", "bar"): 3,
#     ("bizz", "buzz"): 1,
# }
#
# Allows promargus to exclude alert labels from the tags supplied
# to argus.
# ARGUS_EXCLUDE_TAGS = [
#     "foo",
#     "bar",
#     "bizz",
#     "buzz",
# ]


#### argus-sync settings ####
# == Required ==
# URL for the alertmanager that feeds promargus
ARGUS_SYNC_ALERTMANAGER_URL = "https://example.com/api/v2"

# == Optional ==
# Name of the source assigned to promargus
# Default: "prometheus"
# ARGUS_SYNC_SOURCE_NAME = "prometheus"

# == Optional ==
# Minimum age of incidents to resolve when syncing, in minutes
# Default: 10 (minutes)
# ARGUS_SYNC_RESOLVE_MIN_AGE = 10
