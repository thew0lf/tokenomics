import io
import json
import sys

import pytest

from tokenomics.cli import build_parser, main


def test_parser_exposes_all_phase_commands():
    parser = build_parser()
    assert parser.parse_args(["init"]).command == "init"
    assert parser.parse_args(["capture", "--provider", "anthropic", "--model", "claude"]).command == "capture"
    assert (
        parser.parse_args(
            [
                "knowledge",
                "install",
                "--url",
                "https://raw.githubusercontent.com/x/y/main/p.json",
                "--sha256",
                "0" * 64,
            ]
        ).command
        == "knowledge"
    )


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


def test_outcome_reports_expected_errors_without_traceback(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tokenomics",
            "outcome",
            "missing",
            "--actual-tokens-saved",
            "1",
            "--accepted",
            "--path",
            str(tmp_path / "db"),
        ],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "loss event not found" in capsys.readouterr().err


def test_plan_savings_emits_a_recommendation(tmp_path, monkeypatch, capsys):
    profiles = {
        "models": [
            {
                "name": "planner",
                "provider": "test",
                "input_per_million": 15,
                "output_per_million": 75,
                "capabilities": ["implementation"],
                "max_complexity": "high",
            },
            {
                "name": "executor",
                "provider": "test",
                "input_per_million": 3,
                "output_per_million": 15,
                "capabilities": ["implementation"],
                "max_complexity": "medium",
            },
        ]
    }
    profile_path = tmp_path / "profiles.json"
    profile_path.write_text(json.dumps(profiles), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tokenomics",
            "plan-savings",
            "--profiles",
            str(profile_path),
            "--planner",
            "planner",
            "--task-class",
            "implementation",
            "--complexity",
            "medium",
            "--input",
            "12000",
            "--output",
            "2000",
        ],
    )
    main()
    assert json.loads(capsys.readouterr().out)["recommended_executor"] == "executor"
