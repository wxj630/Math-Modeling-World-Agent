from __future__ import annotations

import json
import re


_JSON_CODE_BLOCK_RE = re.compile(r"^```(?:json)?|```$", re.MULTILINE)


def clean_json_text(text: str) -> str:
    cleaned = _JSON_CODE_BLOCK_RE.sub("", text or "").strip()
    cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)
    return cleaned


def parse_json_strict(text: str) -> dict:
    cleaned = clean_json_text(text)
    if not cleaned:
        raise ValueError("Empty JSON payload")
    return json.loads(cleaned)


def repair_json(text: str) -> dict | None:
    cleaned = clean_json_text(text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    try:
        fixed = re.sub(
            r'(?<=: ")(.*?)(?=",\s*\n\s*"|"\s*\n\s*})',
            lambda m: m.group(0).replace('"', '\\"'),
            cleaned,
            flags=re.DOTALL,
        )
        return json.loads(fixed)
    except (json.JSONDecodeError, re.error):
        pass

    try:
        pattern = r'"(\w+)"\s*:\s*"((?:[^"\\]|\\.|"(?!,\s*\n)|"(?!\s*\n\s*}))*)"'
        matches = re.findall(pattern, cleaned, re.DOTALL)
        if matches:
            return {k: v.replace('\\"', '"') for k, v in matches}
    except re.error:
        pass

    return None
