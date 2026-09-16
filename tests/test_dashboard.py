from tokenomics.dashboard import create_app


def test_dashboard_is_read_only_and_local(tmp_path):
    from fastapi.testclient import TestClient

    client = TestClient(create_app(tmp_path / "tokenomics.db"))
    summary = client.get("/api/summary")
    assert summary.status_code == 200
    assert summary.json()["usage"]["events"] == 0
    assert summary.json()["savings"] == {
        "estimated_tokens": 0,
        "actual_tokens_saved": 0,
    }
    assert client.get("/").status_code == 200
