"""JSON extractor."""

import json
import re

import orjson
from json_repair import repair_json


def extract_json_from_text(text: str) -> str | None:
    """Extract a JSON object from text, such as an LLM response.

    This function attempts multiple strategies to extract valid JSON:
    1. Direct parsing
    2. Extracting JSON from markdown code blocks
    3. Handling partial/incomplete JSON

    Parameters
    ----------
    text : str
        Text containing JSON, such as an LLM response

    Returns
    -------
    str
        Extracted JSON.
    None
        If extraction fails.

    """
    text = text.strip()

    # Try direct parsing
    try:
        json_str = repair_json(text, skip_json_loads=True)
        return orjson.dumps(orjson.loads(json_str)).decode('utf-8')
    except (orjson.JSONDecodeError, UnicodeDecodeError):
        pass

    # Try extracting from markdown code blocks
    json_markdown_re = re.compile(r'```(?:json)?(.*?)```', re.DOTALL)
    match = json_markdown_re.search(text)
    if match:
        json_str = match.group(1).strip()
        try:
            json_str = repair_json(text, skip_json_loads=True)
            return orjson.dumps(orjson.loads(json_str)).decode('utf-8')
        except (orjson.JSONDecodeError, UnicodeDecodeError):
            pass

    # Try extracting partial/incomplete JSON
    try:
        from langchain_core.utils.json import parse_partial_json

        return orjson.dumps(parse_partial_json(text)).decode('utf-8')
    except (ImportError, json.decoder.JSONDecodeError, UnicodeDecodeError):
        pass

    return None
