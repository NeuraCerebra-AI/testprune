<div align="center">

<img src="assets/banner.svg" alt="testprune, an Agent Skill for test suite cleanup in Claude Code and Codex CLI: two bars race at the measured 15.4 to 1 ratio, the old 41.90 second routine check still crossing while the 2.72 second fast gate has finished, beside the tagline, the typed slash testprune command, and chips for the fast gate, subsystem gates, broad gate, policy block, and ledger." width="100%">

# testprune

### Agent Skill for test suite cleanup: delete the obsolete tests that no longer describe production, and stop waiting on the check you run after every edit

**The routine check an agent runs after every edit: 41.90 s before, 2.72 s after, in one measured repository. Ten checks: 6m 59s of waiting became 27.2 s.**

Clone it into your agent's Skills folder, open a repo, and run `/testprune`.

Works in Claude Code, Codex CLI, and any client that implements the [Agent Skills open standard](https://github.com/agentskills/agentskills).

[![Released under the MIT license.](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![This is an Agent Skill.](https://img.shields.io/badge/Agent%20Skill-open%20standard-8A63D2.svg)](https://github.com/agentskills/agentskills)
[![The current version is 1.2.0.](https://img.shields.io/badge/version-1.2.0-lightgrey.svg)](SKILL.md)

**Language-agnostic · No paid or networked calls · Every deletion recoverable · Never changes runtime behavior**

</div>

---

> testprune is an Agent Skill that audits a repository's automated test suite, removes the obsolete tests that no longer describe production, retargets the invariants worth keeping at the production code path, and builds layered gates so a routine check finishes in seconds instead of minutes. It ends by writing a test policy into `CLAUDE.md` and `AGENTS.md` so coding agents stop reaching for the full suite. It runs once against a repository rather than continuously in CI, it never changes production runtime behavior, and every deletion is recoverable from the commit hash it records.

## ⏱️ What you get back

It was measured on two private repositories. The first was the heavier cleanup. The second is where the routine check was timed, and one cycle there means one edit followed by that check. Before the run the check took 41.90 s. After it, 2.72 s. That's 39.18 s back per cycle, a 93.5% cut, 15.4x faster.

<img src="assets/time-saved.svg" alt="Test suite cleanup time saved in one measured repository: three tiles read 2.72 seconds where it was 41.90, 15.4x faster as a 93.5 percent cut, and 6 minutes 32 seconds of waiting removed across ten cycles, above a paired bar of 6 minutes 59 seconds against 27.2 seconds. One case, not a benchmark." width="100%">

| Cycles | Before | After | Saved |
| --- | ---: | ---: | ---: |
| One | 41.90 s | 2.72 s | 39.18 s |
| Five | 3m 30s | 13.6 s | 3m 16s |
| Ten | 6m 59s | 27.2 s | 6m 32s |
| Twenty | 13m 58s | 54.4 s | 13m 04s |

The saving is per cycle, so it scales with how often the check runs, and a coding agent runs it after every edit. In the second repository a session of ten cycles, one subsystem check, and one broad check before a push now takes about 2m 24s, less than the ten old checks alone. The broad gate stays at 111 s on purpose: it's the pre-push cost, not the routine one.

The first repository shows the same shape from a worse start: a 24-minute suite carrying 186 stale failures became a 10-second fast gate with zero failures and a 10-minute broad gate with 33 classified pre-existing failures.

Both are single measured cases, not benchmarks, and your numbers will differ. Where the wait comes from doesn't: tests that certify a deprecated implementation, stale failures everyone has learned to scroll past, and gitignored modules the runner still collects all cost their full runtime on every edit while proving less each time.

## ⚡ Install and run

Claude Code reads personal Skills from `~/.claude/skills/`; Codex CLI reads them from `~/.agents/skills/`. Clone into whichever your client uses:

```bash
# Claude Code
git clone https://github.com/NeuraCerebra-AI/testprune.git ~/.claude/skills/testprune

# Codex CLI
git clone https://github.com/NeuraCerebra-AI/testprune.git ~/.agents/skills/testprune
```

Then, in a session opened on the repository you want cleaned:

```
/testprune                 # audit and execute in this session, budget two hours
/testprune prompt-first    # write a curated, repo-specific prompt and stop; changes nothing
/testprune followups       # execute the high-blast-radius items a prior pass deferred, budget forty-five minutes
```

Start with `prompt-first` if you'd rather read the plan before anything is deleted. It writes the audit prompt and a companion follow-up prompt, and it touches no test.

Requirements: a client that supports Agent Skills, `git`, `bash` 3.2 or newer for the gate script, and Python for the one inventory script. The Skill itself is language-agnostic. In Claude Code it's user-invoked only (`disable-model-invocation: true` in `SKILL.md`), so the model can't start it on its own.

## 📋 What a run leaves behind

Three gate commands, a policy block your agent reads first, and a ledger of every deletion with the commit hash that restores it. These are the commands written into the first repository; the run adapts the same template to yours:

```bash
scripts/run_test_gates.sh fast              # explicit file list, zero known failures, seconds
scripts/run_test_gates.sh subsystem api     # one owning boundary
scripts/run_test_gates.sh broad             # everything provider-free, before a push
```

<img src="assets/gates.svg" alt="Layered test gates before and after testprune in the first repository: a before strip of one 24 minute suite with 186 failures, then three gate cards with their commands and measured times, a fast gate at 10 seconds with zero known failures, a subsystem gate for one owning boundary that was never timed on its own, and a broad gate at 10 minutes with 33 classified pre-existing failures." width="100%">

The fast gate is an explicit file list, never a glob or a marker, because a file list can't drift into an ignored, live, or environment-dependent test. The policy block goes into `CLAUDE.md` and `AGENTS.md`, identical except for the self-name, with the gate commands first in any commands list. This is the one the first repository got:

```markdown
## Test suite policy

- Production authority: main/orchestrator.py is the only production path tests may certify.
  main/orchestrator_V2.py is deprecated code retained for history: no tests, no parity tests,
  and production is never changed to match it.
- Default verification: `scripts/run_test_gates.sh fast` (10 s, zero known failures) after every
  edit; the subsystem gate for the boundary you touched; `scripts/run_test_gates.sh broad`
  (10 min, 33 classified pre-existing failures) only before a push.
- Removal standard: no skip markers, no root conftest skip machinery, no xfail-forever.
```

The rest of what changed there, taken from tool output during the run:

| Run | Before | After |
| --- | --- | --- |
| Fast gate | none; the whole 24 min suite was the check | 10 s, 20 files, zero failures |
| Broad gate | 24 min | 10 min |
| Failures an agent has to read | 186 | 0 in the fast gate, 33 classified in the broad gate |
| Slowest two tests | 70 s each | 4 s each |

Twenty-three deprecated and historical test files went with `git rm`, four untracked ones were archived, three invariants were retargeted at the production orchestrator, and no production code changed.

## 🔍 How it decides

The run is an audit, then a set of decisions, then a measurement, following the 13-step checklist in [`SKILL.md`](SKILL.md). Four decisions carry the weight.

**Production authority first.** From entrypoints, deploy config, CI, and config resolvers it names the one path real users hit, and names every deprecated or parallel implementation by file, with proof that production doesn't route through it. Only tests on that path may certify a change, and production is never changed to match a deprecated one.

**One bucket per test module.** Production coverage, deprecated-path coverage, historical or stale-intent, live/paid/credentialed, environment-dependent, duplicated, or untracked ad hoc. Classification is by what a test proves, not by the vocabulary in its fixtures: a test that inserts rows in a retired format and asserts they still open is production coverage, and it stays.

<img src="assets/classify.svg" alt="How testprune classifies every test module into one of seven buckets, production coverage, deprecated-path coverage, historical or stale-intent, live paid credentialed, environment-dependent, duplicated, or untracked ad hoc, then routes each through a production authority check to one of three outcomes: keep, retarget first, or remove recoverably with git rm." width="100%">

**Retarget first, then delete.** A bad test can still be the only thing pinning a real guarantee. Each such invariant gets one focused test against the production path, in the repo's own offline harness and its neighbors' style, before the original goes.

**Remove recoverably, never hide.** Tracked files go with `git rm` and the recovery hash lands in the ledger. Untracked files move to a gitignored archive, because deleting an untracked file can't be undone. Live tests get a marker and a credential self-skip and leave the automatic gates. A red test whose expectation can't be corrected with source authority stays red and gets listed. No skip markers, no root conftest skip machinery, no xfail-forever, because those keep the scrolling going instead of ending it.

Before classification, [`scripts/test_inventory.py`](scripts/test_inventory.py) runs, because ignore rules control commits, not collection: in the first repository, 74 gitignored test modules still ran in every broad run and were invisible to anyone reading `git ls-files`.

Anything with high blast radius (production code, fixtures shared by many suites, prompt or schema mirrors, frozen artifacts, files dirty from other work) isn't executed. It's written into a follow-up prompt naming the claimants that disagree and the decision to make, and `/testprune followups` executes those items once the production authority for each is settled.

## 🚧 What it won't do

These are rules in `SKILL.md`, copied verbatim into any prompt it writes.

- **No runtime changes.** It never edits application logic to make a test pass, and it never deletes the deprecated implementation itself. The one production edit `followups` mode allows is comment-only, when a stale comment is the thing that's wrong, and the report says so.
- **No paid calls.** No test that claims to be offline may reach a paid, networked, or credentialed service. Offline-looking tests that could are stubbed at the seam, and the run proves zero calls afterwards.
- **No destructive git.** It never runs `git restore`, `git checkout --`, `git reset --hard`, or `git stash`, and it doesn't commit unless you ask.
- **No touching other work.** Files already dirty from other work in progress are reported, not edited.
- **No invented numbers.** Every figure in the closing report comes from tool output, measured before and after.

## ⚖️ How it compares

It's a one-time audit, not a service, and it loses two of the six rows below on purpose. If your suite is already fast and honest and you want fewer tests executed per commit, a selection tool fits better, and selection works better on a suite that's been cleaned.

| | testprune | Predictive test selection<br>(Launchable, Nx affected, pytest-testmon, testtrim) | Flaky-test platforms<br>(Trunk.io, BuildPulse, Datadog) | Mutation testing<br>(Stryker, mutmut, PIT) |
| --- | --- | --- | --- | --- |
| **When it runs** | Once, as an audit | Every commit, indefinitely | Continuously across CI history | On demand, often slowly |
| **What it changes** | What the suite contains | Which tests execute | Which tests are quarantined | Nothing, it reports |
| **Decides a test shouldn't exist** | Yes | No | No | Suggests, doesn't decide |
| **Needs CI integration or run history** | No | Yes | Yes, weeks of runs | No |
| **Speeds up a suite that's already clean** | No | Yes | No | No |
| **Measures test strength formally** | No, classification is a judgment call | Not its job | No | Yes, by mutation kill rate |

It isn't test impact analysis, a flaky-test quarantine, a coverage or mutation tool, or an implementation of formal test-suite minimization research.

## 📊 Why this matters

The problem is measured, not anecdotal. CircleCI's analysis of 14,146,319 workflows found a median duration of 2 minutes 43 seconds but workflows running more than 25 minutes at the 95th percentile, against its own recommended 10-minute benchmark ([CircleCI, 2025 State of Software Delivery](https://circleci.com/landing-pages/assets/2025-state-of-software-delivery-report.pdf)). Google reported that of roughly 4.2 million tests on its CI system, about 63,000 had a flaky run over one week, with 14% of its large tests flaky ([Google Testing Blog, 2017](https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html)), and that about 84% of observed pass-to-fail transitions involved a flaky test rather than a real regression ([Google Testing Blog, 2016](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)).

Lost trust is the expensive part, because a suite nobody believes still costs its full runtime. In a survey of 335 developers, 51% reported hitting test flakiness at least weekly, and they ranked lost trust in test results and wasted developer time as worse consequences than the wasted compute ([Gruber and Fraser, IEEE ICST 2022](https://arxiv.org/abs/2203.00483)).

**What the agent research says, and what it doesn't.** On SWE-bench Verified, TDAD measured a 6.08% baseline regression rate for a coding agent, 9.94% when it was told to follow test-driven practices, and 1.82% when it was given a map of which tests actually covered the change ([Alonso, Yovine and Braberman, arXiv, March 2026](https://arxiv.org/abs/2603.17973)). That paper evaluates a dependency-graph tool in the predictive-test-selection category, not this one, so none of those numbers are a result for testprune. testprune has never been evaluated on SWE-bench or measured for its effect on agent regression rate. The only measured results on this page are the two cases above.

## ❓ FAQ

**How do I stop Claude Code from running the entire test suite on every small change?**
Give Claude Code a faster default and say so in the file it reads first. Agents read `CLAUDE.md` or `AGENTS.md` before anything else, so a 10-second gate saves nobody time until that file points at it. testprune builds the fast gate, measures it, and writes the policy block with the gate commands first and the raw full-suite command marked as not a routine check.

**Is it safe to let an AI agent delete tests?**
Deletions are recoverable and the run is auditable, which is the honest version of safe. Tracked tests go with `git rm` and the ledger records the commit hash you restore from. Untracked tests move to a gitignored archive rather than being deleted, because that operation isn't reversible. To read the plan before anything moves, run `/testprune prompt-first`, which changes nothing.

**Which tests does testprune consider safe to delete?**
A test becomes a deletion candidate when it drives an implementation that production doesn't route through, or when it's permanently red or vacuous, and both require naming the production path first with file-level proof. Merely failing isn't enough: a red test whose expectation can't be corrected with cited source authority is left red and listed, and a test proving a retired data format still reads, refuses calmly, or migrates is production coverage and stays.

**Does testprune work with Jest, Go, or Rust, or only pytest?**
testprune is language-agnostic by design: the gate script template wraps whatever test command your repository already runs, and the inventory script covers any language. The worked examples in the reference files are Python and pytest, the stack it was built on, so on other stacks expect to adapt commands rather than concepts.

**What if I disagree with one of its decisions?**
Every deletion is in the ledger with its recovery hash, and every corrected expectation with the source authority behind it. Restoring one file is `git show <hash>:path/to/test.py > path/to/test.py`. Items where the evidence wasn't conclusive are deferred with the competing claimants named, and neither side changes until you decide.

## 📁 What's in the repository

| Path | Purpose |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The rules, the 13-step checklist, the execution model, and the safety rules |
| [`references/rationale_and_pitfalls.md`](references/rationale_and_pitfalls.md) | Why each rule exists, and the failure mode behind it |
| [`references/techniques.md`](references/techniques.md) | Sleep spy, durations, hunk-only staging, cost-ledger scan, archive move, allowlist edits, JSON validation |
| [`references/gate_script_template.sh`](references/gate_script_template.sh) | The fast, subsystem, subsystems, broad, and deprecated gate script, bash 3.2 compatible |
| [`references/agent_instruction_block.md`](references/agent_instruction_block.md) | The `CLAUDE.md` and `AGENTS.md` policy block, in JSON and Markdown forms |
| [`references/prompt_creator.md`](references/prompt_creator.md) | Prompt-first mode |
| [`references/followups_execution.md`](references/followups_execution.md) | Followups mode: the adjudication protocol, the four recurring shapes, the release-pipeline pin, and the red-flags table |
| [`scripts/test_inventory.py`](scripts/test_inventory.py) | On-disk versus tracked versus gitignored test modules, any language |

## 🤝 Contributing and license

It was built from a real cleanup and hardened by a second one, both on private repositories. Every rule in `SKILL.md` traces back to something that went wrong in one of them, and the reasoning is in [`references/rationale_and_pitfalls.md`](references/rationale_and_pitfalls.md) so you can disagree with a rule on the merits rather than guessing at its intent.

Issues and pull requests are welcome, especially reports from stacks other than Python, where the reference examples are thinnest. If a rule fails you in a real repository, the most useful thing you can open is the case that broke it.

Released under the [MIT License](LICENSE).

If it saves you a suite run, a star helps other people find it.
