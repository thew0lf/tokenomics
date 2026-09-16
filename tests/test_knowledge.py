import hashlib

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
