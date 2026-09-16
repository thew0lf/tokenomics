import io
import json
import sys

from tokenomics.cli import build_parser, main


def test_parser_exposes_all_phase_commands():
    parser = build_parser()
    assert parser.parse_args(["init"]).command == "init"
    assert parser.parse_args(
        ["capture", "--provider", "anthropic", "--model", "claude"]
    ).command == "capture"
    assert parser.parse_args(
        [
            "knowledge",
            "install",
            "--url",
            "https://raw.githubusercontent.com/x/y/main/p.json",
            "--sha256",
            "0" * 64,
        ]
    ).command == "knowledge"


def test_capture_persists_only_usage(tmp_path, monkeypatch, capsys):
    payload = {"usage": {"input_tokens": 10, "output_tokens": 5}, "content": [{"text": "private"}]}
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(payload).encode())))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tokenomics",
            "capture",
            "--provider",
            "anthropic",
            "--model",
            "claude",
            "--path",
            str(tmp_path / "db"),
        ],
    )
    main()
    assert "private" not in capsys.readouterr().out
