# prometheus-argus-glue

## developement/testing

Install conda env and activate:
```
make install
conda activate ./conda_env
```

Copy settings example and make changes:
```
cd promargus
cp example_settings.py local_settings.py
vi local_settings.py
```

Running dev server:
```
export PROM_ARGUS_SETTINGS=local_settings.py
python -m promargus.webhook
```

Format code:
```
black promargus
```

Lint:
```
flake8 promargus --max-line-length 88
```
