from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .detectors import detect_ai_polling, detect_context_repetition, detect_hidden_errors
from .knowledge import fetch_pack, install_pack
from .ledger import LossEvent, LossType
from .models import UsageEvent
from .planning import profiles_from_data, recommend_handoff
from .providers import AnthropicUsageAdapter
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

    capture = sub.add_parser("capture", help="Capture API usage JSON without storing response content.")
    capture.add_argument("--provider", choices=["anthropic"], required=True)
    capture.add_argument("--model", required=True)
    capture.add_argument("--path", default=".tokenomics/tokenomics.db")

    report = sub.add_parser("report", help="Show local token totals.")
    report.add_argument("--path", default=".tokenomics/tokenomics.db")

    analyze = sub.add_parser("analyze", help="Run deterministic waste detectors against supplied text.")
    analyze.add_argument("text")
    analyze.add_argument("--calls-per-minute", type=float)
    analyze.add_argument("--repeated-tokens", type=int, default=0)
    analyze.add_argument("--total-input-tokens", type=int, default=0)
    analyze.add_argument("--record-losses", action="store_true")
    analyze.add_argument("--path", default=".tokenomics/tokenomics.db")

    outcome = sub.add_parser("outcome", help="Record the measured result of a loss recommendation.")
    outcome.add_argument("loss_id")
    outcome.add_argument("--actual-tokens-saved", type=int, required=True)
    acceptance = outcome.add_mutually_exclusive_group(required=True)
    acceptance.add_argument("--accepted", action="store_true")
    acceptance.add_argument("--rejected", action="store_true")
    outcome.add_argument("--path", default=".tokenomics/tokenomics.db")

    plan_savings = sub.add_parser(
        "plan-savings", help="Recommend a lower-cost declared-capable executor without dispatching work."
    )
    plan_savings.add_argument("--profiles", required=True, help="Path to caller-supplied model profile JSON.")
    plan_savings.add_argument("--planner", required=True, help="Name of the planning model in the profile file.")
    plan_savings.add_argument(
        "--task-class", required=True, help="Declared task class, such as implementation or docs."
    )
    plan_savings.add_argument("--complexity", choices=["low", "medium", "high"], required=True)
    plan_savings.add_argument("--input", type=int, required=True, dest="input_tokens")
    plan_savings.add_argument("--output", type=int, required=True, dest="output_tokens")
    plan_savings.add_argument("--handoff-overhead", type=int, default=0)
    plan_savings.add_argument(
        "--minimum-net-savings",
        type=float,
        default=0.0,
        help="Only recommend a handoff when estimated savings meet this currency threshold.",
    )

    knowledge = sub.add_parser("knowledge", help="Manage the local public knowledge pack.")
    knowledge_sub = knowledge.add_subparsers(dest="knowledge_command", required=True)
    install = knowledge_sub.add_parser("install", help="Install a verified knowledge pack.")
    install.add_argument("--url", required=True)
    install.add_argument("--sha256", required=True)
    install.add_argument("--path", default=".tokenomics/knowledge.json")
    return parser


def _confidence(severity: str) -> float:
    return {"high": 0.9, "medium": 0.75, "low": 0.5}.get(severity, 0.5)


def _finding_json(finding) -> dict[str, object]:
    return {
        "rule_id": finding.rule_id,
        "severity": finding.severity,
        "message": finding.message,
        "evidence": finding.evidence,
        "estimated_avoidable_tokens": finding.estimated_avoidable_tokens,
    }


def _main() -> None:
    args = build_parser().parse_args()

    if args.command == "init":
        EventStore(args.path)
        print(f"Initialized Tokenomics at {Path(args.path).parent}")
        return

    if args.command == "record":
        event = UsageEvent(
            provider=args.provider,
            model=args.model,
            input_tokens=args.input_tokens,
            output_tokens=args.output_tokens,
            cache_read_tokens=args.cache_read,
            cache_write_tokens=args.cache_write,
            session_id=args.session,
        )
        EventStore(args.path).add(event)
        print("Recorded usage event. Conversation content was not stored.")
        return

    if args.command == "capture":
        raw = sys.stdin.buffer.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("API response exceeds 2 MiB limit")
        response = json.loads(raw.decode("utf-8"))
        event = AnthropicUsageAdapter().from_response(response, model=args.model)
        EventStore(args.path).add(event)
        print(json.dumps({"event_id": event.event_id, "tokens": event.total_tokens}, indent=2))
        return

    if args.command == "report":
        store = EventStore(args.path)
        print(json.dumps({"events": store.count(), **store.totals()}, indent=2))
        return

    if args.command == "outcome":
        store = EventStore(args.path)
        store.update_loss_outcome(args.loss_id, args.actual_tokens_saved, args.accepted)
        print(
            json.dumps(
                {
                    "loss_id": args.loss_id,
                    "actual_tokens_saved": args.actual_tokens_saved,
                    "recommendation_accepted": args.accepted,
                },
                indent=2,
            )
        )
        return

    if args.command == "knowledge":
        data = fetch_pack(args.url, args.sha256)
        installed = install_pack(data, args.path)
        print(json.dumps({"version": installed["version"], "path": str(args.path)}, indent=2))
        return

    if args.command == "plan-savings":
        profile_data = json.loads(Path(args.profiles).read_text(encoding="utf-8"))
        profiles = profiles_from_data(profile_data)
        planner = next((profile for profile in profiles if profile.name == args.planner), None)
        if planner is None:
            raise ValueError(f"planning model not found in profile file: {args.planner}")
        recommendation = recommend_handoff(
            planner=planner,
            candidates=profiles,
            task_class=args.task_class,
            complexity=args.complexity,
            input_tokens=args.input_tokens,
            output_tokens=args.output_tokens,
            handoff_overhead_tokens=args.handoff_overhead,
            minimum_net_savings=args.minimum_net_savings,
        )
        print(json.dumps(recommendation.as_dict(), indent=2))
        return

    findings = detect_hidden_errors(args.text) + detect_ai_polling(args.text, args.calls_per_minute)
    if args.repeated_tokens or args.total_input_tokens:
        findings += detect_context_repetition(args.repeated_tokens, args.total_input_tokens)

    if args.record_losses:
        store = EventStore(args.path)
        for finding in findings:
            store.add_loss(
                LossEvent(
                    loss_type=_FINDING_TO_LOSS.get(finding.rule_id, LossType.UNKNOWN),
                    estimated_tokens=finding.estimated_avoidable_tokens,
                    description=finding.message,
                    confidence=_confidence(finding.severity),
                    source=finding.rule_id,
                )
            )

    output = {
        "findings": [_finding_json(finding) for finding in findings],
        "recommendations": [
            {
                "rule_id": recommendation.rule_id,
                "action": recommendation.action,
                "rationale": recommendation.rationale,
                "estimated_savings_tokens": recommendation.estimated_savings_tokens,
            }
            for recommendation in recommend(findings)
        ],
    }
    print(json.dumps(output, indent=2))


def main() -> None:
    """Run the CLI without exposing implementation tracebacks for expected input errors."""
    try:
        _main()
    except (json.JSONDecodeError, KeyError, OSError, RuntimeError, TypeError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
