import pytest


def test_dashboard_requires_optional_dependency(monkeypatch):
    import builtins
    from tokenomics import dashboard

    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "fastapi":
            raise ImportError("blocked for test")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(RuntimeError, match="tokenomics\[dashboard\]"):
        dashboard.create_app()
