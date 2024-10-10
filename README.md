# prometheus-argus-glue

A service that receives alerts from Alertmanager (Prometheus) via webhooks and pushes events into Argus.

Some components and implementation is based off https://gitlab.sikt.no/cnaas/mist-argus

## production deployment

`gunicorn` is recommended for production deployment:
```
$ gunicorn --bind 127.0.0.1:5000 promargus.webhook:app
```
Debug logging from the app is available if gunicorn is called with
`--log-level=debug`.

## configuration

See `example_settings.py` for configuration params.

`ARGUS_SEVERITY_CONFIG` is a dictionary with keys being a key, value tuple of the alert label, and value being the severity level. If set it enables the glue service to determine incident severity based of the alert labels. e.g. `"labels": {"pagepolicy": "always"}` could be mapped to severity 1 (Critical) like this:
```
ARGUS_SEVERITY_CONFIG = {
    ("pagepolicy", "always"): 1,
}
```
Note that the service will set the severity based on the first match, so order matters. For example, an event has the labels `{"pagepolicy": "always"}` and `{"location": "WLG"}`, if `ARGUS_SEVERITY_CONFIG` is:
```
ARGUS_SEVERITY_CONFIG = {
    ("pagepolicy", "always"): 1,
    ("location", "WLG"): 3,
}
```
The severity will be 1, whereas:
```
ARGUS_SEVERITY_CONFIG = {
    ("location", "WLG"): 3,
    ("pagepolicy", "always"): 1,
}
```
The severity will be 3.

## developement/testing

Install conda env and activate:
```
$ make install
$ conda activate ./conda_env
```

Copy settings example and make changes:
```
$ cd promargus
$ cp example_settings.py local_settings.py
$ vi local_settings.py
```

Running dev server:
```
$ export PROM_ARGUS_SETTINGS=local_settings.py
$ python -m promargus.webhook
```

Format code:
```
$ black promargus
```

Lint:
```
$ flake8 promargus --max-line-length 88
```

