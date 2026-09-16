"""Versioned public knowledge packs with explicit integrity checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_PACK_BYTES = 2 * 1024 * 1024
ALLOWED_HOSTS = frozenset({"raw.githubusercontent.com", "github.com"})


def load_pack(path: str | Path) -> dict[str, object]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("version"), str):
        raise ValueError("knowledge pack must contain a string version")
    if not isinstance(data.get("rules", []), list):
        raise ValueError("knowledge pack rules must be a list")
    return data


def fetch_pack(url: str, expected_sha256: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("knowledge updates require HTTPS from an approved GitHub host")
    request = Request(url, headers={"User-Agent": "tokenomics-knowledge-updater/1"})
    with urlopen(request, timeout=10) as response:
        data = response.read(MAX_PACK_BYTES + 1)
    if len(data) > MAX_PACK_BYTES:
        raise ValueError("knowledge pack exceeds size limit")
    digest = hashlib.sha256(data).hexdigest()
    if digest.lower() != expected_sha256.lower():
        raise ValueError("knowledge pack integrity check failed")
    return data


def install_pack(data: bytes, destination: str | Path) -> dict[str, object]:
    destination = Path(destination)
    parsed = json.loads(data.decode("utf-8"))
    if not isinstance(parsed, dict) or not isinstance(parsed.get("version"), str):
        raise ValueError("invalid knowledge pack")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return parsed
