from __future__ import annotations

import argparse
import json
from pathlib import Path

from .detectors import detect_ai_polling, detect_context_repetition, detect_hidden_errors
from .ledger import LossEvent, LossType
from .models import UsageEvent
from .recommendations import recommend
from .storage import EventStore


_FINDING_TO_LOSS = {
    "hidden-errors": LossType.HIDDEN_ERROR,
    "pipeline-status": LossType.VERIFICATION,
    "ai-polling": LossType.POLLING,
    "repeated-context": LossType.REPEATED_CONTEXT,
}


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
    analyze.add_argument("--repeated-tokens", type=int, default=0)
    analyze.add_argument("--total-input-tokens", type=int, default=0)
    analyze.add_argument("--record-losses", action="store_true")
    analyze.add_argument("--path", default=".tokenomics/tokenomics.db")

    return parser


def _confidence(severity: str) -> float:
    return {"high": 0.9, "medium": 0.75, "low": 0.5}.get(severity, 0.5)


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
        if args.repeated_tokens or args.total_input_tokens:
            findings += detect_context_repetition(args.repeated_tokens, args.total_input_tokens)

        if args.record_losses and findings:
            store = EventStore(args.path)
            for finding in findings:
                loss_type = _FINDING_TO_LOSS.get(finding.rule_id, LossType.UNKNOWN)
                store.add_loss(
                    LossEvent(
                        loss_type=loss_type,
                        estimated_tokens=finding.estimated_avoidable_tokens,
                        description=finding.message,
                        confidence=_confidence(finding.severity),
                        source=finding.rule_id,
                    )
                )

        output = {
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "message": f.message,
                    "evidence": f.evidence,
                    "estimated_avoidable_tokens": f.estimated_avoidable_tokens,
                }
                for f in findings
            ],
            "recommendations": [
                {
                    "rule_id": r.rule_id,
                    "action": r.action,
                    "rationale": r.rationale,
                    "estimated_savings_tokens": r.estimated_savings_tokens,
                }
                for r in recommend(findings)
            ],
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
