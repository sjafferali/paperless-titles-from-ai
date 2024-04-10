# paperless-titles-from-ai

This is a project to generate meaningful titles for ingested paperless documents using AI.

## Setup

### Clone Repository
```bash
git clone https://github.com/sjafferali/paperless-titles-from-ai.git
```

### Create .env file
```bash
cp -av paperless-titles-from-ai/.env.example paperless-titles-from-ai/.env
# Update .env file with the correct values
```

### Update docker-compose.yml file
Update docker compose file with the correct path to the project directory.

```yaml
services:
  # ...
  paperless-webserver:
    # ...
    volumes:
      - /path/to/paperless-titles-from-ai:/usr/src/paperless/scripts
      - /path/to/paperless-titles-from-ai/init:/custom-cont-init.d:ro
  environment:
    # ...
    PAPERLESS_POST_CONSUME_SCRIPT: /usr/src/paperless/scripts/app/main.py
```