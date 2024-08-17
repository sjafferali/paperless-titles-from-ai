#!/usr/bin/env python3
import argparse
import logging
import requests
import sys

from main import set_auth_tokens, make_request, process_single_document, get_single_document
from cfg import PAPERLESS_URL, PAPERLESS_API_KEY, OPENAI_API_KEY, OPENAPI_MODEL, OPENAI_BASEURL


def get_all_documents(sess, paperless_url, advanced_filter=None):
    url = paperless_url + "/api/documents/"
    if advanced_filter:
        url += f"?{advanced_filter}"
    response = make_request(sess, url, "GET")
    if not response or not isinstance(response, dict):
        logging.error("could not retrieve documents")
        return []

    documents = response.get("results", [])

    while response["next"]:
        response = make_request(sess, response["next"], "GET")
        if not response or not isinstance(response, dict):
            logging.error("could not retrieve documents")
            return []

        documents.extend(response.get("results", []))

    return documents


def run_single_document(args):
    if args.dry:
        logging.info("Running in dry mode")
    logging.info(f"Running for document {args.document_id}")
    with requests.Session() as sess:
        set_auth_tokens(sess, args.paperlesskey)
        doc_info = get_single_document(sess, args.document_id, args.paperlessurl)
        if not isinstance(doc_info, dict):
            logging.error(f"could not retrieve document info for document {args.document_id}")
            return

        doc_contents = doc_info["content"]
        doc_title = doc_info["title"]

        process_single_document(sess, args.document_id, doc_title, doc_contents, args.paperlessurl,
                                args.openaimodel, args.openaikey, args.openaibaseurl, args.dry)


def run_all_documents(args):
    if args.dry:
        logging.info("Running in dryrun mode")

    logging.info("Running on all documents")
    with requests.Session() as sess:
        set_auth_tokens(sess, args.paperlesskey)

        all_docs = get_all_documents(sess, args.paperlessurl, args.filterstr)
        if not all_docs or not isinstance(all_docs, list):
            logging.error("could not retrieve documents")
            return

        logging.info(f"found {len(all_docs)} documents")

        for doc in all_docs:
            doc_id = doc["id"]
            doc_title = doc["title"]
            doc_content = doc["content"]

            if args.exclude and doc_id in args.exclude:
                logging.info(f"skipping document {doc_id}")
                continue

            logging.info(f"running for document {doc_id}")
            process_single_document(sess, doc_id, doc_title, doc_content, args.paperlessurl,
                                    args.openaimodel, args.openaikey, args.openaibaseurl, args.dry)
            logging.info(f"finished running for document {doc_id}")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--loglevel", dest="loglevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default="INFO", type=lambda s: s.upper(), help="Set the logging level")
    parser.add_argument('--dry', action='store_true', help="Run without making any changes")
    parser.add_argument('--paperlessurl', type=str, default=PAPERLESS_URL, help="URL for the paperless instance")
    parser.add_argument('--paperlesskey',
                        type=str, default=PAPERLESS_API_KEY,
                        help="API key for the paperless instance")
    parser.add_argument('--openaimodel', type=str, default=OPENAPI_MODEL, help="OpenAI model to use")
    parser.add_argument('--openaikey', type=str, default=OPENAI_API_KEY, help="OpenAI key to use")
    parser.add_argument('--openaibaseurl', type=str, default=OPENAI_BASEURL,
                        help="Endpoint for OpenAI compatible API to use when generating titles")
    subparsers = parser.add_subparsers()

    parser_all = subparsers.add_parser("all", description="Run on all documents")
    parser_all.add_argument('--exclude', action='append', type=int, help="Document ID to skip")
    parser_all.add_argument('--filterstr', type=str, help='Pass in url query parameters to filter document filter request by')
    parser_all.set_defaults(func=run_all_documents)

    parser_single = subparsers.add_parser("single", description="Run on a single document")
    parser_single.add_argument('document_id', type=int)
    parser_single.set_defaults(func=run_single_document)

    parsed_args = parser.parse_args(args)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=parsed_args.loglevel)

    try:
        parsed_args.func(parsed_args)
    except AttributeError:
        parser.print_help()


if __name__ == '__main__':
    parse_args(sys.argv[1:])
