import os
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path('/usr/src/paperless/scripts/paperless-titles-from-ai/.env')
load_dotenv(dotenv_path=dotenv_path)

PROMPT = """You are a AI model that is responsible for analyzing OCR text from scanned documents and generating titles 
for those documents that can be used in our digital archiving system. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

===Response Guidelines 
1. If the provided ocr data has content that can be interpreted, please generate a valid title that best describes the document without providing an explaination. Otherwise provide an explanation and generate a random title using the current date.
2. Format the query before responding.
3. Always respond with a valid well-formed JSON object without any additional information or formatting.
4. Generated title should all be lowercase. 
5. Generated title should not contain spaces.
6. Generated title should not contain special characters.
8. Generated title should not contain slashes.
9. The maximum length of the title should be 32 characters.
10. For any documents that is a tax related document, ensure to include the year in the title.
11. No additional formatting should be applied to the response.

===Input
The current date can always going to be the first date in the context. The rest of the context is the truncated OCR text from the scanned document.


===Response Format
{"title": "A valid title.", "explanation": ""}
"""

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAPI_MODEL = os.getenv("OPENAPI_MODEL", "gpt-4-turbo")

CHARACTER_LIMIT = 45000
if 'gpt-4' in OPENAPI_MODEL:
    CHARACTER_LIMIT = 200000

PAPERLESS_URL = os.getenv("PAPERLESS_URL", "http://localhost:8000")
PAPERLESS_API_KEY = os.getenv("PAPERLESS_API_KEY")
TIMEOUT = 10
