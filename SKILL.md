---
name: testprune
description: Use when a test suite is bloated, slow, historically red, certifies deprecated or parallel implementations, or can reach paid services from tests that claim to be offline; also when a prior testprune run deferred high-blast-radius findings such as a comment, code, and test that disagree, a config that admits a backend the runtime refuses, a dead transport still wired into a route, or historical-row tests mistaken for deprecated coverage. Repo- and language-agnostic.
when_to_use: Invoke with /testprune when an agent "runs all the tests" and waits minutes to read stale failures. Pass "prompt-first" to only write a curated prompt; pass "followups" to execute the deferred high-blast-radius items.
argument-hint: [direct|prompt-first|followups]
arguments: mode
disable-model-invocation: true
metadata:
  version: "1.2.0"
---

# testprune

Mode: `$mode` (default `direct`). `prompt-first` means: run `references/prompt_creator.md` to write a curated, repo-specific prompt and a follow-up prompt, then stop. `direct` means: execute the checklist below in this session. `followups` means: execute `references/followups_execution.md` for the high-blast-radius items a prior pass deferred; the rules and safety rules below still apply, and no test moves until production authority is proven.

Snapshot at load (files listed as modified or untracked belong to other work unless the user says otherwise):

```
!`git rev-parse --short HEAD 2>/dev/null; git status --short 2>/dev/null | head -40`
```

## Rules

- Only tests that exercise the production path may certify a change. Name deprecated or parallel implementations by file; never write or keep tests for them, never change production to match them.
- Permanently red or vacuous tests are deleted (`git rm`, recoverable) or parked in an ignored archive. Never skip-forever, never a root conftest skip, never xfail-forever.
- Retarget a real invariant at production before deleting the test that carried it.
- Tests over rows in a retired format that prove readability, calm refusal, migration, or stored-row contracts are production coverage; keep them. Only a test that drives the retired implementation to produce output is deprecated-path coverage.
- A backend that configuration admits but every production workflow refuses is not a supported path; adapter and pricing tests may certify it, workflow tests may not.
- When the default test command changes meaning, every CI step, release script, and orchestration test that named the old command is repointed in the same change.
- The fast gate is an explicit file list with zero known failures and runs in seconds.
- Every number comes from tool output. Measure before and after.
- No test that claims to be offline may reach a paid, networked, or credentialed service.
- Time budget: two hours direct, forty-five minutes for follow-ups. Stop at the budget and report.
- Read `references/rationale_and_pitfalls.md` once before starting; do not re-read it.

## Checklist (copy into your todo list)

1. **Preflight.** Read the repo instruction file (CLAUDE.md or AGENTS.md, only the one for your tool) and the wiki testing page if one exists. List dirty and untracked files from the snapshot; do not edit them. Find env files the code loads and whether they hold real credentials. Identify tests that could reach paid APIs, networks, databases, email, or deploy tooling if a stub were missing.
2. **Production authority.** From entrypoints, deploy config, CI, and config resolvers: name the one production path, the effective defaults tests must assume (with file references), and every deprecated or parallel implementation with proof production does not route through it.
3. **Inventory.** Run `python scripts/test_inventory.py` (from this skill's directory) for on-disk versus tracked versus gitignored test modules. Record runner config, fixtures, markers, skip machinery, runner scripts. Ignored files on disk are still collected.
4. **Baseline, only if safe.** If the whole suite can run without network or credentials, run it once with `--durations=0` and record wall time, pass/fail/skip/error counts, and the slowest tests. Otherwise record the collection count and say why.
5. **Classify** every test module into one bucket: production coverage, deprecated-path coverage, historical or stale-intent, live/paid/credentialed, environment-dependent, duplicated, untracked ad hoc. Flag oversized modules, repeated hand-rolled fakes, brittle assertions, slow tests and their real wait, and inaccurate testing docs. A module that inserts retired-format rows and asserts they are readable, refused, or migrated is production coverage, not deprecated-path coverage; classify by what the test proves, not by the vocabulary in its fixtures.
6. **Blast radius.** Low: delete or edit a test, correct a stale expectation with cited source authority. Medium: retarget an invariant, add the gate script, change runner config, shared fixtures. High: production code, fixtures used by many suites, prompt or schema mirrors, frozen artifacts, dirty files. Execute low and medium; write high into a follow-up prompt (phase 2B format in `references/prompt_creator.md`), naming per item the claimants that disagree and the decision the executor must make. For every deprecated module you exclude from certification but keep, write a retention record: callers, registrations, shared unions that must stay, and removal prerequisites.
7. **Retarget invariants.** One focused production-path test per invariant, using the repo's offline harness and its neighbors' style. No giant fixtures, no new frameworks.
8. **Remove.** Tracked: `git rm`, note the recovery commit hash. Untracked: move to the ignored archive directory with a README. Live: marker plus credential self-skip, excluded from automatic gates. Stale expectations without source authority: leave red, list them. After excluding a module from certification, run the registry sweep in `references/techniques.md` so no manifest, purpose matrix, allowlist, or doc key-file list still presents it as live.
9. **Gates.** Adapt `references/gate_script_template.sh`: fast, subsystem, subsystems, broad, deprecated. Fence archives, backups, scratch and results directories out of collection in the runner config. Scrub credential and mode variables at the runner setup seam unless the collection is explicitly live. If the default test command now means the fast gate, grep CI workflows, release scripts, and their orchestration tests for the old command, repoint them to the broad gate, update the expected-order pin, and confirm the trusted CI profile stays strict; operator scripts that intentionally run live tests must opt into the live collection explicitly. Measure each gate.
10. **Speed and safety fixes.** For slow tests find the real wait with the sleep spy in `references/techniques.md`, patch the wait test-side, keep every retry-budget and fallback assertion. For offline-looking tests that can reach providers, stub at the seam and prove zero calls afterwards.
11. **Docs and instruction files.** Update the testing doc (layers, commands, measured runtimes, remaining failures classified). Add the block from `references/agent_instruction_block.md` to CLAUDE.md and AGENTS.md; keep both identical except the self-name; validate JSON if the file is JSON; put gate commands first in any commands list. Dirty instruction files: stage only your hunks (technique in `references/techniques.md`) and say so. Before renaming or deleting any test, grep the design documents for its exact title; a document that names a test title as certification is a contract.
12. **Ledger** in the repo's results location: every deletion with recovery hash, every corrected expectation with its source authority, before and after numbers, deferred items, remaining failures classified.
13. **Final response** per `references/final_report.md`: outcome first, Done / Optional / Parked, numbers, files changed, both visualizations; a `followups` run uses that file's "Follow-up run variant" instead.

## Execution

- Subagents: at most two, for independent items, each given exact file and line pointers and the no-paid-call rule. Two agents never edit the same file. Read a subagent's diff before trusting its report.
- Verification loop: run the file you touched, then the fast gate; one subsystem gate after related items land; the broad gate once at the end. No re-audits, no compile or lint rituals, no repeated broad runs.
- Follow-ups: give each subagent the decision, not the question; adjudication stays with the lead. A comment-only edit to a production file still triggers the repo's living-documentation protocol.
- Commit only when asked. When asked, commit only this work; split shared files by hunk.

## Safety rules (copy verbatim into any prompt you write)

Use the interpreter or toolchain first on PATH. Do not install or upgrade dependencies unless essential and justified. Make no paid, networked, or credentialed external call; keep every validation offline. Never run `git restore`, `git checkout --`, `git reset --hard`, or `git stash`. Preserve every pre-existing tracked and untracked change. Do not edit files dirty from other work; report them. Do not commit unless explicitly asked. Use targeted patches, not whole-file rewrites. Do not modify frozen historical artifacts. Do not delete the deprecated implementation itself.

## Example

Request: `/testprune` in a repo where `pytest tests/` takes 24 minutes with 186 failures and a deprecated `orchestrator_V2.py` still has parity tests.

Result: 23 deprecated and historical test files removed with `git rm`, four untracked ones archived, three invariants retargeted at the production orchestrator, a fast gate of 20 files at 10 seconds with zero failures, a broad gate at 10 minutes with 33 classified pre-existing failures, two 70-second tests cut to 4 seconds, a `test_suite_policy` block in CLAUDE.md and AGENTS.md, a ledger, and a Done / Optional / Parked report with the two charts.

## Files

- `references/rationale_and_pitfalls.md`: why each rule exists and the failure modes seen in practice.
- `references/techniques.md`: sleep spy, durations, hunk-only staging, cost-ledger scan, archive move, allowlist edits, JSON validation.
- `references/gate_script_template.sh`: layered gate script, bash 3.2 compatible.
- `references/agent_instruction_block.md`: the CLAUDE.md/AGENTS.md policy block in JSON and Markdown forms.
- `references/final_report.md`: the closing report format and both visualization templates.
- `references/prompt_creator.md`: the prompt-first mode.
- `references/followups_execution.md`: the followups mode; the adjudication protocol, the four recurring shapes, the release-pipeline pin, and the red-flags table.
- `scripts/test_inventory.py`: on-disk versus tracked versus ignored test modules for any language.
