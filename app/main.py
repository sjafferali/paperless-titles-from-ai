#!/usr/bin/env python3
import json
import logging
import os
import sys
from datetime import datetime

import requests
from openai import OpenAI

from cfg import (CHARACTER_LIMIT, OPENAI_API_KEY, OPENAPI_MODEL, PAPERLESS_API_KEY, PAPERLESS_URL, PROMPT, TIMEOUT)
from helpers import make_request


def check_args(doc_pk):
    required_args = [PAPERLESS_API_KEY, PAPERLESS_URL, OPENAI_API_KEY,
                     OPENAPI_MODEL, doc_pk, CHARACTER_LIMIT, PROMPT,
                     TIMEOUT]

    for arg in required_args:
        if not arg:
            logging.error("Missing required argument")
            sys.exit(1)


def generate_title(content):
    now = datetime.now()
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": now.strftime("%m/%d/%Y") + " ".join(content[:CHARACTER_LIMIT].split())}
    ]
    response = query_openai(model=OPENAPI_MODEL, messages=messages, mock=False)
    try:
        answer = response.choices[0].message.content
    except:
        return None
    return answer


def query_openai(model, messages, **kwargs):
    client = OpenAI(api_key=OPENAI_API_KEY)
    args_to_remove = ['mock', 'completion_tokens']

    for arg in args_to_remove:
        if arg in kwargs:
            del kwargs[arg]

    return client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        **kwargs)


def _set_auth_tokens(session: requests.Session):
    session.headers.update(
        {"Authorization": f"Token {PAPERLESS_API_KEY}"}
    )


def parse_response(response):
    try:
        data = json.loads(response)
    except:
        return None, None
    return data['title'], data.get('explanation', "")


def update_document_title(sess, doc_pk, title):
    url = PAPERLESS_URL + f"/api/documents/{doc_pk}/"
    body = {"title": title}
    resp = make_request(sess, url, "PATCH", body=body)
    if not resp:
        logging.error(f"could not update document {doc_pk} title to {title}")
        return
    logging.info(f"updated document {doc_pk} title to {title}")


def run_for_document(doc_pk):
    check_args(doc_pk)

    with requests.Session() as sess:
        _set_auth_tokens(sess)

        # Query the API for the document info
        info_url = PAPERLESS_URL + f"/api/documents/{doc_pk}/"
        doc_info = make_request(sess, info_url, "GET")
        if not isinstance(doc_info, dict):
            logging.error(f"could not retrieve document info for document {doc_pk}")
            return

        doc_contents = doc_info["content"]
        doc_title = doc_info["title"]

        response = generate_title(doc_contents)
        if not response:
            logging.error(f"could not generate title for document {doc_pk}")
            return
        title, explain = parse_response(response)
        if not title:
            logging.error(f"could not parse response for document {doc_pk}: {response}")
            return
        logging.info(f"will update document {doc_pk} title from {doc_title} to: {title} because {explain}")

        # Update the document
        update_document_title(sess, doc_pk, title)


if __name__ == '__main__':
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=LOGLEVEL)
    run_for_document(os.getenv("DOCUMENT_ID"))
