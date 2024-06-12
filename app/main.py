#!/usr/bin/env python3
import json
import logging
import os
import sys
from datetime import datetime

import requests
from openai import OpenAI

from cfg import (OPENAI_API_KEY, OPENAPI_MODEL, PAPERLESS_API_KEY, PAPERLESS_URL, PROMPT, OPENAI_BASEURL, TIMEOUT)
from helpers import make_request, strtobool, get_character_limit


def check_args(doc_pk):
    if not PAPERLESS_API_KEY:
        logging.error("Missing PAPERLESS_API_KEY")
        sys.exit(1)
    if not PAPERLESS_URL:
        logging.error("Missing PAPERLESS_URL")
        sys.exit(1)
    if not OPENAI_API_KEY:
        logging.error("Missing OPENAI_API_KEY")
        sys.exit(1)
    if not OPENAPI_MODEL:
        logging.error("Missing OPENAPI_MODEL")
        sys.exit(1)
    if not doc_pk:
        logging.error("Missing DOCUMENT_ID")
        sys.exit(1)
    if not PROMPT:
        logging.error("Missing PROMPT")
        sys.exit(1)
    if not TIMEOUT:
        logging.error("Missing TIMEOUT")
        sys.exit(1)


def generate_title(content, openai_model, openai_key, openai_base_url):
    character_limit = get_character_limit(openai_model)
    now = datetime.now()
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": now.strftime("%m/%d/%Y") + " ".join(content[:character_limit].split())}
    ]
    response = query_openai(model=openai_model,
                            messages=messages,
                            openai_key=openai_key,
                            openai_base_url=openai_base_url,
                            mock=False)
    try:
        answer = response.choices[0].message.content
    except:
        return None
    return answer


def query_openai(model, messages, openai_key, openai_base_url, **kwargs):
    client = OpenAI(api_key=openai_key, base_url=openai_base_url)
    args_to_remove = ['mock', 'completion_tokens']

    for arg in args_to_remove:
        if arg in kwargs:
            del kwargs[arg]

    return client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        **kwargs)


def set_auth_tokens(session: requests.Session, api_key):
    session.headers.update(
        {"Authorization": f"Token {api_key}"}
    )


def parse_response(response):
    try:
        data = json.loads(response)
    except:
        return None, None
    return data['title'], data.get('explanation', "")


def update_document_title(sess, doc_pk, title, paperless_url):
    url = paperless_url + f"/api/documents/{doc_pk}/"
    body = {"title": title}
    resp = make_request(sess, url, "PATCH", body=body)
    if not resp:
        logging.error(f"could not update document {doc_pk} title to {title}")
        return
    logging.info(f"updated document {doc_pk} title to {title}")


def process_single_document(
        sess,
        doc_pk,
        doc_title,
        doc_contents,
        paperless_url,
        openai_model,
        openai_key,
        openai_base_url,
        dry_run=False):
    response = generate_title(doc_contents, openai_model, openai_key, openai_base_url)
    if not response:
        logging.error(f"could not generate title for document {doc_pk}")
        return
    title, explain = parse_response(response)
    if not title:
        logging.error(f"could not parse response for document {doc_pk}: {response}")
        return
    logging.info(f"will update document {doc_pk} title from {doc_title} to: {title} because {explain}")

    # Update the document
    if not dry_run:
        update_document_title(sess, doc_pk, title, paperless_url)


def get_single_document(sess, doc_pk, paperless_url):
    url = paperless_url + f"/api/documents/{doc_pk}/"
    return make_request(sess, url, "GET")


def run_for_document(doc_pk):
    check_args(doc_pk)

    with requests.Session() as sess:
        set_auth_tokens(sess, PAPERLESS_API_KEY)

        doc_info = get_single_document(sess, doc_pk, PAPERLESS_URL)
        if not isinstance(doc_info, dict):
            logging.error(f"could not retrieve document info for document {doc_pk}")
            return

        doc_contents = doc_info["content"]
        doc_title = doc_info["title"]

        process_single_document(
            sess,
            doc_pk,
            doc_title,
            doc_contents,
            PAPERLESS_URL,
            OPENAPI_MODEL,
            OPENAI_API_KEY,
            OPENAI_BASEURL,
            DRY_RUN)


if __name__ == '__main__':
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=LOGLEVEL)
    DRY_RUN = strtobool(os.getenv("DRY_RUN", "false"))
    if DRY_RUN:
        logging.info("DRY_RUN ENABLED")
    run_for_document(os.getenv("DOCUMENT_ID"))
