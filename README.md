# paperless-titles-from-ai

This is a project to generate meaningful titles for ingested [paperless](https://docs.paperless-ngx.com/) documents using AI. Sends the OCR text of the document to the OpenAI API and generates a title for the document. The title is then saved to the document's metadata.

## Examples of Generated Titles
- taxreturntranscript2022
- aigclaims_check_20230313
- prosharesultrabloombergtax2023

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

The init folder (used to ensure open package is installed) must be owned by root.

## Back-filling Titles on Existing Documents
To back-fill titles on existing documents, run the helper cli from the project directory:

```bash
docker run --rm -v ./app:/app python:3 /app/scripts/backfill.sh [args] [single|all]
```

**Arguments**

| Option                | Required | Default                      | Description                                                           |
|-----------------------|----------|------------------------------|-----------------------------------------------------------------------|
| --paperlessurl [URL]  | Yes      | https://paperless.local:8080 | Sets the URL of the paperless API endpoint.                           |
| --paperlesskey [KEY]  | Yes      |                              | Sets the API key to use when authenticating to paperless.             |
| --openaimodel [MODEL] | No       | gpt-4-turbo                  | Sets the OpenAI model used to generate title. Full list of supported models available at [models](https://platform.openai.com/docs/models).                         |
| --openaibaseurl [API Endpoint] | No      |                              | Sets the OpenAI compatible endpoint to generate the title from.                           |
| --openaikey [KEY]     | Yes      |                              | Sets the OpenAI key used to generate title.                           |
| --dry                 | No       | False                        | Enables dry run which only prints out the changes that would be made. |
| --loglevel [LEVEL]    | No       | INFO                         | Loglevel sets the desired loglevel.                                   |

### To run on all documents
```bash
docker run --rm -v ./app:/app python:3 /app/scripts/backfill.sh [args] all [filter_args]
```

**Arguments**

| Option         | Required | Default | Description                                                                                           |
|----------------|----------|---------|-------------------------------------------------------------------------------------------------------|
| --exclude [ID] | No       |         | Excludes the document ID specified from being updated. This argument may be specified multiple times. |

### To run on a single document
```bash
docker run --rm -v ./app:/app python:3 /app/scripts/backfill.sh [args] single (document_id)
```

## Additional Notes
- The default OpenAI model used for generation is gpt-4-turbo. For a slightly less accurate title generation, but drastically reduced cost, use a GPT 3.5 model.
- The number of characters of the OCR text that is sent varies depending on the model being used. We try to send the maximum number the model supports to get the best generation we can.

# Privacy Concerns
Although the [OpenAI API privacy document](https://openai.com/enterprise-privacy/) states that data sent to the OpenAI API is not used for training, other OpenAI compatible API endpoints are also supported by this post-consume script, which allows you to use a locally hosted LLM to generate titles.


## Contact, Support and Contributions
- Create a GitHub issue for bug reports, feature requests, or questions.
- Add a ⭐️ star on GitHub.
- PRs are welcome
