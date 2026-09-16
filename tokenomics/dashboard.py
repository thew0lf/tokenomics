"""Local-only HTTP dashboard. Requires the optional dashboard dependency."""

from __future__ import annotations

from .storage import EventStore


def create_app(db_path: str = ".tokenomics/tokenomics.db"):
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError("Install tokenomics[dashboard] to use the dashboard") from exc

    store = EventStore(db_path)
    app = FastAPI(title="Tokenomics", docs_url=None, redoc_url=None)

    @app.get("/api/summary")
    def summary() -> dict[str, object]:
        return {"usage": {"events": store.count(), **store.totals()}, "savings": store.savings()}

    @app.get("/api/findings")
    def findings(limit: int = 20) -> list[dict[str, object]]:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=422, detail="limit must be between 1 and 100")
        return store.losses(limit)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return """<!doctype html><html><head><title>Tokenomics</title></head>
<body><h1>Tokenomics</h1><p>Local read-only dashboard.</p>
<pre id='summary'>Loading...</pre><script>
fetch('/api/summary').then(r=>r.json()).then(x=>document.getElementById('summary').textContent=JSON.stringify(x,null,2));
</script></body></html>"""

    return app


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Install tokenomics[dashboard] to use the dashboard") from exc
    uvicorn.run(create_app(), host="127.0.0.1", port=8765)
