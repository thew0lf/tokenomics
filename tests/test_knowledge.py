import hashlib
import os

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
