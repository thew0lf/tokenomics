# Tokenomics Policy

This is the working policy for teams that build software with AI agents and want
to ship at cost. It is generic: it names no vendor, project or team, and it is
written from waste that was observed, measured and then prevented.

Quality is never traded for tokens. Every rule below removes spending that buys
nothing: work redone because a check failed silently, output carried through a
whole session after it was read once, and findings relayed without being
verified. A saving that narrows coverage is a smaller job reported at the same
price, and it is not a saving.

The machine readable form of this policy lives in
[`knowledge/pack.json`](../knowledge/pack.json) and
[`knowledge/patterns/`](../knowledge/patterns/). This document is the narrative
form; when the two disagree, fix whichever is wrong in the same change.

## Terms

- **Tier.** A class of model chosen by the judgment the work needs. The four
  tiers are light, standard, working and top. Rules name tiers, never models.
- **Delegating session.** The session that plans the work and dispatches it.
  It is usually the session talking to the human.
- **Brief.** The full instruction a delegated agent receives. The agent knows
  nothing the brief does not carry.
- **Hand back.** The signal a delegated agent returns when the work is beyond
  its tier or a fact is missing. This policy writes it as `ESCALATE`.
- **Settling check.** The one check that confirms or refutes one finding.
- **State file.** A file that carries the live state of a piece of work across
  a context reset or a hand off.

## 1. Tiers by judgment

Pick the tier the work needs, up or down, not the tier that happens to be
running. Quality first, cost second: when it is unclear whether a cheaper tier
would do worse, use the stronger one.

| Tier | Work it gets |
| --- | --- |
| Light | Edits whose shape is already decided, mechanical sweeps, lookups that copy fields into a fixed table, batched writes whose content is already written |
| Standard | Bulk reading, research and data gathering, drafting from a brief that carries the facts, style review, routine features and fixes |
| Working | Planning, security review, verifying another agent's output, judgment heavy work, drafts that must match code or a live system. The normal tier for the delegating session |
| Top | Only work the working tier handed back, or work a human assigns to it directly. Never the default |

Each team keeps one table that maps tiers to models, and that table is the only
place a model name appears. When the lineup changes, only that table changes.
An illustrative mapping:

| Tier | Example model class | Allowed |
| --- | --- | --- |
| Light | Smallest, fastest model in the lineup | yes |
| Standard | Mid sized general model | yes |
| Working | Strongest model the team uses daily | yes |
| Top | Newest or most expensive model | on request |

Allowed values:

- **yes.** The delegating session may dispatch to it on its own judgment.
- **on request.** Never dispatched on the session's own judgment. A hand back
  that would reach it goes to the human with the reason.
- **no.** Never used.

A model added to the lineup starts at **on request** until a human changes it.

Rules for choosing:

- **Importance is not judgment.** A one line security fix covered by a test is
  cheap work. A brand color decision is expensive. Conflating the two pushes
  everything onto the most expensive tier.
- **Coupling justifies a strong tier; breadth alone never does.** Six
  independent near identical edits are light work in any number of files. Six
  edits that must land consistently or the product breaks are not.
- **The delegator chooses at assignment.** A delegated stage that finds the
  work beyond its tier hands back. It never upgrades itself.
- **Every dispatch names its tier.** An agent that does not name one inherits
  the session's tier, which is usually working, whatever the work. A dispatch
  without a named tier is refused before it runs.
- **A copy of the session never takes bulk reading.** A forked session always
  runs on the session's own tier.
- **The light tier is limited by briefing cost.** The brief is written on the
  delegating tier, so a two line edit costs more to brief than to do. Light work
  pays off when its output is large next to the brief, or when several decided
  edits ride in one brief. Track it as a share of delegated tasks, not of cost.
- **Reviews run on the tier their definition pins.** Override only to move a
  gating review up.

## 2. Plan, delegate, review

The strong tier earns its cost deciding what to do and judging whether it was
done right, not executing a written plan. Non trivial work runs in three
stages: facts and plan on the working tier, execution on a cheaper capable tier
with the method rules in its brief, and review on the working tier before
anything ships.

- **Every plan step names its executor.** Inline, or delegated with its tier
  and what it returns. Staying inline is a choice written into the plan, never a
  default. It fits only steps whose next command depends on the content, or
  edits of a few lines whose brief would cost more than the edit.
- **Settle inputs before dispatching work that consumes them.** A summary or
  review started while its source is still under decision is redone when the
  decision lands.
- **Delegate when the answer is a verdict.** If the intermediate output will not
  be read twice, a lower tier reads it and returns the conclusion. Research and
  data gathering (API, metric and log queries, documentation lookups) are bulk
  reading. The delegating session re-runs only the settling check.
- **Keep the delegating session available to the human.** Lookups, sweeps,
  builds and drafts go to background agents. The delegating session keeps
  planning, decisions, settling checks and the conversation.
- **Cap concurrency.** Set a ceiling on agents running at once that fits the
  machine and the rate limits, and hold to it.
- **Scope reviews to the work, never drop them.** Code wants a senior developer,
  infrastructure wants operations and architecture, anything a stranger reads
  wants an editor, new behavior wants test coverage. Fewer reviews because the
  work does not need them is scoping. Fewer because the budget is short is
  gambling.
- **When the budget is tight, cut execution, never review.** A failed execution
  is visible and recoverable. A skipped review is invisible until the defect
  ships.
- **Let reviewers write their own reports.** A reviewer that cannot write a file
  forces the delegating session to retype its findings, paying for them twice on
  the most expensive tier. Give review agents permission to write their report
  to a named path, and have the delegating session read only the verdict.
- **Review findings are suggestions.** Judge each one against the code, fix every
  accepted finding, and say which were rejected and why.

Every plan ends with a planning note derived from that plan:

```text
Planning note
Potential handoff: 4 of 6 steps, bounded, commands written, test verified.
Suggested executor: standard tier.
Estimated net savings: about 40% of this plan's execution tokens, after briefing and review.
Required gates: tests and senior software review. No deployment or trust boundary change.
```

A savings band printed on every plan is decoration. Bound the figure to the
execution tokens that can move; bounded, test verified work typically saves a
third to a half of them. Tests and a senior software review are the floor.
Operations, security and technical writing passes are added only when the change
touches deployment, a trust boundary or public documentation.

## 3. Briefs

A delegated agent inherits the task but not the lessons. The brief is the only
place the lessons can travel. Every brief, even for a small task, writes out:

- **Goal and shape.** What is wanted, whether the shape is decided or needs
  judgment, and what has already been ruled out.
- **Named files.** Reading three named files costs a fraction of working out how
  something functions.
- **The canonical source.** For any value a canonical document defines, the
  brief names the document instead of restating the value. On disagreement the
  document wins and the agent hands back with both values.
- **Stop condition.** The result that ends the work early, stated for this task.
  For example: "If the search returns no matches, run the positive control
  through the same filter, then stop and report the zero."
- **Hand back rule.** If a step needs more judgment than the assigned tier should
  exercise, or a fact the brief does not carry, the agent stops and returns
  `ESCALATE` with the reason. It never guesses and never pushes on. Log every
  hand back.
- **Turn budget.** A budget matched to the task. An agent that exhausts its turns
  mid investigation returns nothing, and every token it spent is lost.
- **Write early.** The agent writes its output file as soon as it has a first
  result and updates it as it goes, so a run that hits its limit still leaves
  something usable. The brief names the output path.
- **Allowed commands.** The commands and tools the agent may run, listed. A
  review agent once ran a command its brief never allowed; anything not on the
  list is out of scope and is a hand back, not a judgment call.
- **Approval boundary.** What needs a human decision. Production changes, commits
  and pushes stay with the session that holds human approval. Approval names the
  action, not the executor: any other approved write with a decided shape can go
  to a lower tier with the approval and its exact scope in the brief, and the
  approving session keeps the read back check.
- **Word budget and return shape.** How long the answer may be, and what it must
  contain.
- **Which findings get re-checked on return.** Decided before dispatch, not after.

## 4. Context ceilings and hand off

A context window is a budget, not a container. Everything read in is paid once on
the way in and again on every later turn.

- **Establish a fact once.** Refer to the conclusion. Re-reading to confirm what
  is already established is the same leak as rediscovering it next session. If
  it deserves doubt, say why.
- **One session per topic.** A small question late in a long session pays for
  every earlier topic.
- **Large output never lands in the delegating session.** A call likely to return
  more than about 10K characters runs inside an agent that returns only the
  answer, or is trimmed before it lands. The settling check is the exception.
- **Waiting is a shell loop, not a model.** A pipeline or job is watched by a
  background loop that exits on the state that matters. An agent that watches
  pays a model turn per check.
- **A ceiling triggers a hand off, not a reminder.** Set a hard context ceiling
  per session (for example 200K tokens per turn). Past it, the session writes a
  state file and the work moves to a fresh session. A reminder alone does not
  work: one long session grew to nearly twice its ceiling, and the working and
  top tiers ended up carrying almost 80 percent of weighted usage against a 55 to
  60 percent target, because every turn re-read the whole history on the most
  expensive tier.
- **Write the state file early.** Past a lower threshold (for example 150K), before
  compacting, and before switching topics, write a file that holds only state:
  what is live with exact identifiers, what is staged but not live, each decision
  waiting on a human with its default, the next three steps, every running agent
  and what it returns, and pointers to existing records. No credentials and no
  personal data; name where they live instead.
- **Test the state file.** A fresh standard tier agent given only the file must
  answer what is live, what waits on a human, and what must not ship without
  approval. Any question it cannot answer exactly is a gap to fix before the
  hand off.
- **Standing text has a budget.** Instruction files, memory indexes, agent and
  skill catalogs, tool names and hook text are paid on every call of every
  session. Give each standing file a budget from a measured baseline, measure it
  with a script (silent under budget), and trim over budget catalogs by archiving,
  never by deleting. Installing anything is checked against the budget first.
- **Resume for continuation, start fresh for a new batch.** Resuming an agent
  replays its whole context.

## 5. Verification

Rework is the invisible leak: no log that records only what was produced shows
it. Work built on an unverified assumption is paid for twice.

- **Positive control every zero.** Before reporting an empty or zero result, run
  the same probe through the same filter, shaped to return something it must
  match. A control that only proves the command runs is not a control. Say which
  zeros were controlled.
- **A truncated result looks complete.** A capped listing, clipped output or a
  transfer stopped at a size limit raises no error. Compare what was received
  with what should exist (row count, byte count, the service's own total) before
  reasoning from it.
- **An implausible number is a failed check.** Too round, too large, too small or
  exactly zero is evidence about the measurement before it is evidence about the
  world. A count that contradicts one already observed is a parsing bug until
  proven otherwise.
- **Re-measure after the thing measured changes.** A stale number quoted with
  confidence is worse than none.
- **Never suppress stderr on a reported result.** Capture output, check the exit
  status, then format. A pipe returns the formatter's status, so a failing check
  can report success.
- **A commit is not a deploy, and a deploy is not a verification.** Written,
  merged to a branch, merged to mainline, released and running in production are
  five different states. Fetch what a stranger receives and assert on it.
- **Failed scheduled and deploy runs alert someone.** A deleted deploy credential
  once made every deploy fail silently for months, because a scheduled job that
  fails with no alert looks exactly like one that is not needed. Every scheduled
  job and every deploy pipeline sends a failure notice to a channel a human reads,
  and a red run is fixed or consciously retired within a day.
- **Verify before relaying.** A finding from another reviewer or agent is a
  hypothesis. Re-run the settling check, not the sweep, and say which findings
  were verified and which were not. A readiness verdict ("ready to merge") is a
  finding too.
- **Say which unit a count is in.** One issue in three packages is three findings
  and one identifier. Before comparing two measurements, confirm the same tool
  version and the same reference data.
- **Prove a multi file change landed whole.** Staging tools can accept some paths
  and silently skip others. In one shell, a variable holding a list of paths did
  not split into separate arguments, and a commit took 2 of 11 files. Never hold
  a path list or command options in a single string variable; pass paths
  explicitly or through an array, then compare the staged file count with the
  intended count before committing.
- **Only one skip is free.** Skipping what provably cannot have changed is free,
  and the skip says so. Scoping to a diff, sampling, or checking some surfaces is
  a coverage trade with a reason, named in the finding. Verified against the diff
  and verified against the file are different claims.
- **Copy the last instance.** For anything produced repeatedly, open the most
  recent one and match its shape.

## 6. Shared resources, one user at a time

A shared stateful resource (a test database, a preview environment, a deploy
target) takes one user at a time. Parallel builders split code, never the
resource, and the delegating session serializes test runs and ships.

- Before any push, list the unpushed range and confirm every commit in it was
  reviewed, because parallel builders may commit to the same branch.
- Before editing a shared document, keep a dated backup and edit the current
  file, never a copy read earlier.
- When undoing a change, read its record first. An empty search proves only that
  the filter did not match. Record hand made changes at the time, with the exact
  identifier needed to reverse them.

## 7. Credentials are never printed

The rule is not "mask before printing". It is: never emit bytes from a file that
holds a credential, by any route. No formatter, no substitution, no listing of
key names.

A masking expression is written against an assumed file shape. When the shape
differs, the expression matches nothing and the raw contents print. That failure
is silent and total.

- Learn a credential file's shape from its size, permissions and match counts.
- Use its values by piping them into the consuming command inside one
  invocation, so they never reach output.
- Anything that did reach output is treated as disclosed and rotated.
- Briefs for agents that touch production facts say which reads are allowed, and
  forbid reading environment dumps or credential files unless a human named that
  read.

## 8. Measurement

- **Judge tier share per agent or kind of work, not as one global number.** An
  agent doing infrastructure and security work legitimately runs more working
  tier than one doing reviews. Each team sets its own targets; a reasonable
  starting point is a working tier share of 50 to 65 percent of cost depending
  on the agent, with any top tier spend flagged.
- **Judge a change after at least three calendar days under it,** not against
  windows that predate it.
- **Compare cost share with targets; token share shows volume.**
- **A nudge must be rare to be read.** A hook that pushes toward delegation stays
  silent on settling checks and fires on a run of consecutive inline lookups,
  for example the third. A hook that fires on every command is ignored.
- **Log observed waste and the rule that generalizes from it,** plus one line per
  hand back. A rule earns a place in this policy once it holds on any machine.
- **Estimated savings are not realized savings.** Record the measured outcome
  and subtract the cost of measuring. See the
  [Token Loss Ledger](../README.md#token-loss-ledger).

## 9. What gets automated

Automate a check only if it is mechanically decidable, stable, guards a violation
that matters, and would survive deadline pressure. Everything else stays a
written convention. A check that has not fired in a long time states its purpose
in its header, or it is deleted.

## 10. Documents state facts

Policy and reference documents state what is true. They carry no proposed owners,
sequencing or speculative future work. Know it or ask; do not guess and publish.
