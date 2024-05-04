import logging
import requests
import json
import traceback
from cfg import TIMEOUT


def make_request(sess, url, method, body=None, params=None, headers=None):
    if body is not None:
        body = json.dumps(body)
    if headers is None:
        headers = {}

    headers["Content-Type"] = "application/json"

    try:
        r = sess.request(method, headers=headers, url=url, params=params, data=body, timeout=TIMEOUT, verify=True)
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Error connecting to {url}: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout calling {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling {url}: {e}")
        return None

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(f"Http error calling {url}: {e}")
        logging.error(f"Response: {r.text}")
        return None

    try:
        json_response = r.json()
    except Exception as e:
        logging.error(f"Error occurred converting response to json {e}")
        traceback.print_exc()
        return r.text
    return json_response
