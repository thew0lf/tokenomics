from __future__ import annotations

import argparse
import json
from pathlib import Path

from .detectors import detect_ai_polling, detect_hidden_errors
from .models import UsageEvent
from .storage import EventStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tokenomics",
        description="Local-first AI token observability and optimization.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize a local Tokenomics store.")
    init.add_argument("--path", default=".tokenomics/tokenomics.db")

    record = sub.add_parser("record", help="Record token usage without storing conversation content.")
    record.add_argument("--provider", required=True)
    record.add_argument("--model", required=True)
    record.add_argument("--input", type=int, required=True, dest="input_tokens")
    record.add_argument("--output", type=int, required=True, dest="output_tokens")
    record.add_argument("--cache-read", type=int, default=0)
    record.add_argument("--cache-write", type=int, default=0)
    record.add_argument("--session")
    record.add_argument("--path", default=".tokenomics/tokenomics.db")

    report = sub.add_parser("report", help="Show local token totals.")
    report.add_argument("--path", default=".tokenomics/tokenomics.db")

    analyze = sub.add_parser("analyze", help="Run deterministic waste detectors against supplied text.")
    analyze.add_argument("text")
    analyze.add_argument("--calls-per-minute", type=float)

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "init":
        EventStore(args.path)
        print(f"Initialized Tokenomics at {Path(args.path).parent}")
        return

    if args.command == "record":
        store = EventStore(args.path)
        store.add(
            UsageEvent(
                provider=args.provider,
                model=args.model,
                input_tokens=args.input_tokens,
                output_tokens=args.output_tokens,
                cache_read_tokens=args.cache_read,
                cache_write_tokens=args.cache_write,
                session_id=args.session,
            )
        )
        print("Recorded usage event. Conversation content was not stored.")
        return

    if args.command == "report":
        store = EventStore(args.path)
        print(json.dumps({"events": store.count(), **store.totals()}, indent=2))
        return

    if args.command == "analyze":
        findings = detect_hidden_errors(args.text) + detect_ai_polling(
            args.text, args.calls_per_minute
        )
        print(
            json.dumps(
                [
                    {
                        "rule_id": f.rule_id,
                        "severity": f.severity,
                        "message": f.message,
                        "evidence": f.evidence,
                        "estimated_avoidable_tokens": f.estimated_avoidable_tokens,
                    }
                    for f in findings
                ],
                indent=2,
            )
        )
