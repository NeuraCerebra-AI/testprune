# Why the rules exist, and what went wrong before

Read once at the start of a run. Everything here is the reasoning behind the terse rules in SKILL.md; the rules stand on their own.

## The principle

A test suite must tell the truth about production, cheaply. Both halves matter. A suite that is truthful but takes 24 minutes gets skipped. A suite that is fast but certifies a deprecated implementation is worse than no suite, because green means nothing and red gets ignored.

## Why only production-path tests certify

In the repo this skill was built on, an experimental orchestrator that never shipped had a fan club of "parity" and "swap readiness" tests. They passed and failed on their own schedule, unrelated to what users ran, and agents spent time keeping them green. Deleting them lost nothing; the few real invariants they encoded (checkpoint resume forwarding, provider relabel after fallback, a dedicated vector-store path) were retargeted at the production entrypoint in one focused test each. Name deprecated paths by file in every prompt and doc, because names collide: a test called `test_..._v2.py` there meant the production chain version, while `orchestrator_V2.py` was the deprecated module.

## Why delete instead of skip

Eighteen files pinned the exact wording of prompt drafts from a 27-stage era; 79 of their 279 tests were permanently red and everyone had learned to scroll past them. A skip marker would have preserved the scrolling. `git rm` keeps them recoverable from the commit hash written in the ledger, and the archive directory (ignored, fenced from collection) holds untracked ones because deleting an untracked file cannot be undone.

## Why ignored is not uncollected

Git ignore rules control commits, not collection. The runner reads the directory. In that repo, 74 gitignored test modules still ran in every broad run; several covered production code and were invisible to anyone reading `git ls-files`. The inventory script exists to surface this in the first ten minutes.

## Why the fast gate is an explicit list

A glob or a marker can drift; an explicit list cannot wander into an ignored, live, or environment-dependent test. Zero known failures is the point: an agent must be able to read "N passed" and move on. Add a file only when it is provider-free, environment-free, and fast, and add it to the matching subsystem list at the same time.

## Why "no paid calls" is a rule and not a hope

`config.py` loaded a developer `.env` with real keys. Two tests that looked offline reached paid providers: a boundary test whose harness stubbed the main chain but not the Excel, QC, and capsule lanes, and an admission test whose job-control fake let the real orchestrator run. Total damage was under a dollar, but only because the runs were short. Stub at the seam, disable paid lanes in the shared harness helper, and prove zero calls afterwards with a cost-ledger or network-log scan.

## Why the slow test's wait is usually somewhere else

Two 70-second tests were labeled "vector-store attach failures". The attach fake raised immediately. A `time.sleep` spy showed the time was retry backoff in a Gemini upload helper two modules away, plus a hard-coded 2-second stream poll. Patching the wait test-side cut them to 4 seconds with every assertion intact. Measure with the spy; do not guess from the test name.

## Why the instruction file gets a block

The wiki testing page documented the gates, but agents read CLAUDE.md or AGENTS.md first, and that file still led with "run all backend tests". The 10-second gate did not save anyone time until the instruction file pointed at it. Keep the two files identical except for the self-name; validate JSON if the file is JSON.

## Why measure everything

Before and after numbers (wall time, failure count, slowest tests, collected tests) are what let the user answer "are we finished?" and "did this help?". Numbers come from `--durations`, run summaries, and `wc`, never from memory.

## Why the report has three piles

Every earlier report ended with a list of optional extras, and the user could not tell whether the job was done. Done / Optional / Parked, with "optional does not slow anything down" stated when true, removes the ambiguity.

## Other pitfalls seen

- A subagent reported a fix; the diff showed it had also changed an assertion. Read the diff.
- `set -u` with an empty bash array fails on macOS bash 3.2; the gate template uses the `${arr[@]+"${arr[@]}"}` idiom.
- A test file that imports helpers from a sibling test module works under pytest's default rootdir import mode only when both sit in the same directory without `__init__.py`; check before relying on it.
- An order-dependent async teardown failure that passes in isolation is a flake, not a regression; record it as such rather than chasing it inside the time budget.
- When two tasks share a file (instruction files, wiki log), stage only your hunks; otherwise your commit carries someone else's half-finished work.

## Why authority is adjudicated before a test moves

A follow-up item is usually two truthful-looking claims that disagree. In one repo a config comment said the provider was "never silently downgraded", the factory returned the labeled offline provider when a named backend lacked its key, and a fast-gate test asserted that fallback. The cheap fix was to make the factory throw so the comment became true; it would also have stopped two hosted services from starting. `git log -S` showed the comment's commit had scoped its refusal to a different case and had never touched the factory, and the design document named the fallback test as the invariant's certification. The comment was the defect. The protocol in `followups_execution.md` exists so the executor ranks authorities before choosing what to edit, and writes `Confirm needed` when the ranking is not conclusive.

## Why a config-admitted option is not a supported path

The same repo accepted a second provider in configuration and built its adapter in the factory, while every real workflow checked the provider name and refused before any call. Tests for the adapter passed, so it looked supported. Nothing that a user could trigger completed on it. Record the position explicitly (supported partial transport, retained adapter with no reachable workflow, or missing support) and add a boundary test per entry point proving the refusal happens before any call, so no future test can quietly make the alternate option certify a real workflow.

## Why historical rows are production coverage

After a pipeline was retired, its rows stayed in customer databases. Tests that inserted rows in the retired format and asserted they were readable, refused with the calm retired message, or migrated correctly looked like deprecated-path coverage because their fixtures used the old vocabulary. They were the only tests proving a customer's database still opened. Classify by what the test proves; only a test that drives the retired implementation to produce output goes.

## Why the release pipeline must be repointed

Changing `npm test` from "the whole suite" to an eight-file fast gate silently changed what the release verifier ran, because the verifier invoked `npm test` by name. Its own orchestration test pinned that command, so the pin had to move too, and the trusted-CI branch had to be re-checked to confirm it still forced the strict profile. The companion trap: fencing live tests out of default collection also fenced them out of the operator scripts that were supposed to run them on purpose, until those scripts opted into the live collection explicitly.

## Why design documents that name test titles are a contract

An invariant manifest in the design document listed exact test titles as the certification of each invariant. Renaming or deleting one of those tests would have broken the contract with no runner output to say so. Grep the docs for a test's title before touching it.

## Why registries need a sweep, not a memory

Excluding a dead module from two scanner tests left a purpose-matrix row in a third test and three wiki key-file lists still presenting it as live. Each was found by grepping for the module name and its step names across tests, scripts, and docs, not by remembering where it had been registered.
