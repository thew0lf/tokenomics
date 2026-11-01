import hashlib
import os
from pathlib import Path

import pytest

from tokenomics.knowledge import fetch_pack, install_pack, load_pack


def test_load_pack_validates_schema(tmp_path):
    path = tmp_path / "pack.json"
    path.write_text('{"version":"1.0.0","rules":[]}', encoding="utf-8")
    assert load_pack(path)["version"] == "1.0.0"


def test_fetch_pack_rejects_non_github_urls():
    with pytest.raises(ValueError, match="approved GitHub host"):
        fetch_pack("https://example.com/pack.json", "0" * 64)


def test_install_pack_writes_verified_json(tmp_path):
    data = b'{"version":"1.1.0","rules":[]}'
    assert hashlib.sha256(data).hexdigest()
    result = install_pack(data, tmp_path / "pack.json")
    assert result["version"] == "1.1.0"


def test_install_pack_keeps_previous_pack_for_rollback(tmp_path):
    path = tmp_path / "pack.json"
    original = b'{"version":"1.0.0","rules":[]}'
    updated = b'{"version":"1.1.0","rules":[]}'
    install_pack(original, path)
    install_pack(updated, path)
    assert path.read_bytes() == updated
    assert path.with_suffix(".json.previous").read_bytes() == original


@pytest.mark.skipif(os.name != "posix", reason="POSIX permissions are not available")
def test_installed_pack_is_private_on_posix(tmp_path):
    path = tmp_path / "pack.json"
    install_pack(b'{"version":"1.1.0","rules":[]}', path)
    assert path.stat().st_mode & 0o777 == 0o600


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_bundled_pack_loads_and_every_rule_has_a_pattern_file():
    pack = load_pack(REPO_ROOT / "knowledge" / "pack.json")
    rules = pack["rules"]
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))
    for rule in rules:
        assert rule["severity"] in {"high", "medium", "low"}
        pattern_file = REPO_ROOT / "knowledge" / "patterns" / f"{rule['id']}.yml"
        assert pattern_file.is_file(), rule["id"]
        text = pattern_file.read_text(encoding="utf-8")
        assert f"id: {rule['id']}\n" in text
        assert "requires_raw_conversation: false" in text


def test_bundled_policy_document_exists():
    pack = load_pack(REPO_ROOT / "knowledge" / "pack.json")
    assert (REPO_ROOT / pack["policy"]).is_file()
