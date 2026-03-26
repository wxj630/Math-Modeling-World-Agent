from __future__ import annotations

import json
import re

try:
    import json_repair
except Exception as e:  # pragma: no cover - optional dependency
    raise ImportError(
        "json_repair is required for advanced JSON repair functionality. "
        "Please install it with 'pip install json-repair'."
    ) from e


_JSON_CODE_BLOCK_RE = re.compile(r"^```(?:json)?|```$", re.MULTILINE)


def clean_json_text(text: str) -> str:
    cleaned = _JSON_CODE_BLOCK_RE.sub("", text or "").strip()
    cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)
    return cleaned


def _candidate_json_payloads(cleaned: str) -> list[str]:
    candidates: list[str] = []
    if cleaned:
        candidates.append(cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if 0 <= start < end:
        obj_slice = cleaned[start : end + 1].strip()
        if obj_slice and obj_slice not in candidates:
            candidates.append(obj_slice)

    return candidates


def _loads_with_repair(payload: str) -> object:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as first_exc:
        if json_repair is None:
            raise first_exc
        return json_repair.loads(payload)


def parse_json_strict(text: str) -> dict:
    cleaned = clean_json_text(text)
    if not cleaned:
        raise ValueError("Empty JSON payload")

    last_error: Exception | None = None
    for payload in _candidate_json_payloads(cleaned):
        try:
            obj = _loads_with_repair(payload)
            if isinstance(obj, dict):
                return obj
            last_error = TypeError(f"JSON root must be object, got {type(obj).__name__}")
        except Exception as exc:
            last_error = exc
            continue

    raise ValueError(f"Invalid JSON payload: {last_error}")


def repair_json(text: str) -> dict | None:
    cleaned = clean_json_text(text)
    if not cleaned:
        return None

    for payload in _candidate_json_payloads(cleaned):
        try:
            obj = _loads_with_repair(payload)
            if isinstance(obj, dict):
                return obj
        except Exception:
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
        pattern = r'"([^"\\]+)"\s*:\s*"((?:\\.|[^"\\])*)"\s*(?=,|})'
        matches = re.findall(pattern, cleaned, re.DOTALL)
        if matches:
            return {k: v.replace('\\"', '"') for k, v in matches}
    except re.error:
        pass

    return None
