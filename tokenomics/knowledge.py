"""Versioned public knowledge packs with explicit integrity checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_PACK_BYTES = 2 * 1024 * 1024
ALLOWED_HOSTS = frozenset({"raw.githubusercontent.com", "github.com"})


def validate_pack(data: bytes) -> dict[str, object]:
    if len(data) > MAX_PACK_BYTES:
        raise ValueError("knowledge pack exceeds size limit")
    try:
        parsed = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("knowledge pack must be valid UTF-8 JSON") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("version"), str):
        raise ValueError("knowledge pack must contain a string version")
    if not isinstance(parsed.get("rules", []), list):
        raise ValueError("knowledge pack rules must be a list")
    return parsed


def load_pack(path: str | Path) -> dict[str, object]:
    return validate_pack(Path(path).read_bytes())


def fetch_pack(url: str, expected_sha256: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("knowledge updates require HTTPS from an approved GitHub host")
    if len(expected_sha256) != 64 or any(char not in "0123456789abcdefABCDEF" for char in expected_sha256):
        raise ValueError("expected_sha256 must be a SHA-256 hex digest")
    request = Request(url, headers={"User-Agent": "tokenomics-knowledge-updater/1"})
    with urlopen(request, timeout=10) as response:
        data = response.read(MAX_PACK_BYTES + 1)
    validate_pack(data)
    if hashlib.sha256(data).hexdigest().lower() != expected_sha256.lower():
        raise ValueError("knowledge pack integrity check failed")
    return data


def install_pack(data: bytes, destination: str | Path) -> dict[str, object]:
    parsed = validate_pack(data)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return parsed
