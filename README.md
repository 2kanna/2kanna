# 2kanna

# installation

```bash
uvicorn twok.api:app --host 0.0.0.0 --port 8000
```

Default admin password:

```
admin
password
```

# containers

There is a `Dockerfile` and a `docker-compose.yml` file in this repository. You can use them to run 2k in a container, or use the image for a kubernetes deployment.

# configuration

You can configure 2kanna by setting environment variables. Look in `.env` for the default values.

# dev

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```
