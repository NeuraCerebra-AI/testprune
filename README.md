<div align="center">

<img src="assets/banner.svg" alt="testprune: an Agent Skill for test suite optimization that makes a bloated suite fast, honest and small. In the repository it was built on the routine check an agent runs after every edit went from 24 minutes to 10 seconds, 144x faster, shown as two progress bars running the same check. Type slash testprune to run it." width="100%">

# testprune

### Agent Skill for test suite optimization: cut a bloated suite down to a check that finishes in seconds, without thinning the coverage that matters

**In the repository it was built on, the check an agent runs after every edit went from 24 minutes to 10 seconds, and the 186 failures everyone had learned to scroll past went to zero. The whole suite still runs before a push.**

Clone it into your agent's Skills folder, open a repo, and run `/testprune`.

Works in Claude Code and Codex CLI, and in other clients that implement the [Agent Skills open standard](https://github.com/agentskills/agentskills).

[![Released under the MIT license.](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![This is an Agent Skill.](https://img.shields.io/badge/Agent%20Skill-open%20standard-8A63D2.svg)](https://github.com/agentskills/agentskills)
[![The current version is 1.2.0.](https://img.shields.io/badge/version-1.2.0-lightgrey.svg)](SKILL.md)

**Language-agnostic · No paid or networked calls · Every deletion recoverable · Never changes runtime behavior**

</div>

---

> testprune is an Agent Skill that optimizes a repository's automated test suite: it finds the one code path real users hit, retargets the invariants worth keeping at that path, makes slow tests fast without dropping their assertions, builds layered gates so a routine check finishes in seconds, and removes only the tests that no longer describe production. It ends by writing a test policy into `CLAUDE.md` and `AGENTS.md` so coding agents stop reaching for the full suite. It runs once against a repository rather than continuously in CI, it never changes production runtime behavior, and every deletion is recoverable from the commit hash it records.

## 🧹 The problem

- **Slow suites get skipped.** A check nobody runs protects nothing, and you pay the wait again on every edit.
- **Green stops meaning anything.** A suite that certifies a deprecated or parallel implementation is worse than no suite, because passing tells you nothing about what users run.
- **Red stops meaning anything.** Once a wall of stale failures is normal, everyone learns to scroll past it, and the real regression scrolls past too.
- **Agents pay the worst price.** A coding agent re-runs the suite on every iteration, reads the same stale failures every time, and burns its context window on output that never changes.

## ⏱️ What it changes

<img src="assets/time-saved.svg" alt="What the optimization pass changed in one repository: the routine check after an edit dropped from 24 minutes to 10 seconds, 144 times faster, and the failures an agent must read dropped from 186 to zero, while the whole suite still runs before a push in 10 minutes instead of 24. Two 70-second tests became 4 seconds with every assertion intact." width="100%">

The saving is paid out per check, so it scales with how often you run one, and an agent runs one constantly. Four checks in a single task cost 96 minutes of waiting before and 40 seconds after. That figure is arithmetic on the measured before and after, not a separate measurement.

| What changed | Before | After |
| --- | ---: | ---: |
| Routine check after an edit | 24 min | 10 s |
| Whole suite, before a push | 24 min | 10 min |
| Failures an agent must read | 186 | 0 in the fast gate, 33 classified in the broad gate |
| The two slowest tests | 70 s each | 4 s each |

**Deleting tests cannot explain that, and here is the proof: the whole suite still runs.** The broad gate executes everything that is left, and it still takes 10 minutes. The routine check reached 10 seconds because the fast gate is an explicit list of 20 provider-free files with zero known failures, which is a selection, not a smaller suite. The whole-suite run did drop from 24 minutes to 10, but that pass removed 23 files, fenced stray directories out of collection, and cut two 70-second tests to 4 seconds, so no single cause can be isolated from one before and one after measurement. The suite got smaller. It got fast because it got organized.

These numbers are one repository, measured before and after with tool output. They are not a benchmark, and your suite will differ.

## 📋 What a run leaves behind

<img src="assets/gates.svg" alt="The three test gates testprune builds: a fast gate run after every edit, an explicit file list with zero known failures at 10 seconds; a subsystem gate for one owning boundary, not separately measured; and a broad gate run before a push, everything provider-free, at 10 minutes with 33 classified pre-existing failures. Measured on one repository." width="100%">

Three commands, a policy your agent reads, and a ledger of every change.

```bash
scripts/run_test_gates.sh fast              # explicit file list, zero known failures, seconds
scripts/run_test_gates.sh subsystem api     # one owning boundary
scripts/run_test_gates.sh broad             # everything provider-free, before a push
```

Here are three of the seven lines it wrote into `CLAUDE.md` and `AGENTS.md`, so the next agent session reaches for the fast gate instead of the whole suite:

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

## ⚡ Install and run

Claude Code reads personal Skills from `~/.claude/skills/`, and Codex reads them from `~/.agents/skills/`. Clone into whichever your client uses:

```bash
# Claude Code
git clone https://github.com/NeuraCerebra-AI/testprune.git ~/.claude/skills/testprune

# Codex CLI
git clone https://github.com/NeuraCerebra-AI/testprune.git ~/.agents/skills/testprune
```

Then, in a session opened on the repository you want cleaned:

```
/testprune                 # audit and execute in this session, budget about two hours
/testprune prompt-first    # only write a curated, repo-specific prompt
/testprune followups       # execute the items a prior pass deferred, budget about forty-five minutes
```

Start with `prompt-first` if you'd rather read the plan before anything changes. It writes a repo-specific audit prompt and a companion follow-up prompt, runs the suite once for a baseline only if that is safe offline, and touches no test.

Requirements: a client that supports Agent Skills (Claude Code or Codex CLI, for example), `git`, `bash` 3.2 or newer for the gate script, and Python 3.7 or newer for the inventory script, which uses the standard library and the `git` CLI only.

## 🔍 How it works

A run is an audit, then five kinds of fix, then a measurement. It follows a 13-step checklist in [`SKILL.md`](SKILL.md). Removal is one of those five, and the least clever one.

**First, production authority.** From entrypoints, deploy config, CI, and config resolvers it names the one path real users hit, and names every deprecated or parallel implementation by file with proof that production doesn't route through it. Everything after this hangs on that answer, which is why it happens before a single test is read. It also runs [`scripts/test_inventory.py`](scripts/test_inventory.py) early, because git ignore rules control commits, not collection: in this repository 74 gitignored test modules were still running in every full run, invisible to anyone reading `git ls-files`.

<img src="assets/classify.svg" alt="How testprune classifies tests: seven buckets, production coverage, deprecated-path coverage, historical or stale-intent, live paid credentialed, environment-dependent, duplicated and untracked ad hoc, pass through a production authority check and route to one of three outcomes: keep, retarget first, or remove, recoverable. A permanently red test with no source authority is left red and listed." width="100%">

**Then it classifies every test module into exactly one bucket**, by what the test proves rather than by the vocabulary in its fixtures. A test that inserts rows in a retired format and asserts they still open is production coverage, not deprecated-path coverage, and it stays.

Then the five fixes:

- **Retarget invariants.** A bad test can still be the only thing pinning a real guarantee. Each one gets a new focused test against the production path first, written in the repo's own offline harness and its neighbors' style. This step adds tests.
- **Build the gates.** The fast, subsystem and broad layers, plus fencing archives, backups, scratch and results directories out of collection so the broad run can't wander. This is where the routine check gets its speed.
- **Make slow tests fast.** A `time.sleep` spy finds where a slow test actually waits, which is rarely where its name suggests. Two tests labeled "vector-store attach failures" were really waiting on retry backoff in an upload helper two modules away plus a hard-coded 2-second poll. Patching the wait test-side took them from 70 seconds to 4 with every retry-budget and fallback assertion intact.
- **Make offline tests actually offline.** Provider seams get stubbed, credential and mode variables get scrubbed at the runner setup seam so an unknown path fails instead of paying, and a cost-ledger scan afterwards proves zero calls were made.
- **Remove what no longer describes production.** Tracked files go with `git rm` and the recovery hash lands in the ledger. Untracked files move to a gitignored archive, because deleting an untracked file can't be undone. No skip markers, no root conftest skip machinery, no xfail-forever, because those preserve the scrolling instead of ending it.

Two habits run through all of it. Before any test is renamed or deleted, the design documents are grepped for its exact title, because a document that names a test as an invariant's certification is a contract. And when the default test command changes meaning, every CI step, release script and orchestration test that named the old command is repointed in the same change, because switching `npm test` from the whole suite to the fast gate silently changes what the release verifier runs.

## 🚧 What it won't do

These are rules in `SKILL.md`, copied verbatim into any prompt the Skill writes. Two of them are checked after the fact rather than taken on trust: the zero-call proof scans for cost ledgers written during the run, and every deletion's recovery hash lands in the ledger.

- **No runtime changes.** It never changes application logic to make a test pass, and it never deletes the deprecated implementation itself. In `followups` mode a comment-only edit to a production file is possible when a stale comment is the thing that's wrong, and the report says so explicitly.
- **No paid calls.** No test that claims to be offline may reach a paid, networked, or credentialed service, and the run proves zero calls afterwards rather than assuming them.
- **No destructive git.** It never runs `git restore`, `git checkout --`, `git reset --hard`, or `git stash`, and it doesn't commit unless you ask.
- **No touching other people's work.** Files already dirty from other work in progress get reported, not edited.
- **No invented numbers.** Every figure in the closing report comes from tool output, measured before and after.

## ⚖️ How it compares

Different tools, different jobs, and testprune loses two of these six rows on purpose. If your suite is already fast and honest and you just want fewer tests executed per commit, one of the tools below fits better.

| | testprune | Predictive test selection<br>(Launchable, Nx affected, pytest-testmon, testtrim) | Flaky-test platforms<br>(Trunk.io, BuildPulse, Datadog) | Mutation testing<br>(Stryker, mutmut, PIT) |
| --- | --- | --- | --- | --- |
| **When it runs** | Once, as an audit | Every commit, indefinitely | Continuously across CI history | On demand, often slowly |
| **What it changes** | The suite's shape, speed and honesty | Which tests execute | Which tests are quarantined | Nothing, it reports |
| **Decides a test shouldn't exist** | Yes | No | No | Suggests, doesn't decide |
| **Needs CI integration or run history** | No | Yes | Yes, weeks of runs | No |
| **Speeds up a suite that's already clean** | No | Yes | No | No |
| **Measures test strength formally** | No, classification is a judgment call | Not its job | No | Yes, by mutation kill rate |

In plain terms: it isn't test impact analysis or predictive test selection, it isn't a flaky-test detector or quarantine system, it isn't a coverage or mutation-testing tool, and it isn't an implementation of formal test-suite minimization research.

## 📊 Why this matters

Slow and untrustworthy suites are measured, not anecdotal. CircleCI's analysis of 14,146,319 workflows found a median duration of 2 minutes 43 seconds but workflows running more than 25 minutes at the 95th percentile, against its own recommended 10-minute benchmark ([CircleCI, 2025 State of Software Delivery](https://circleci.com/landing-pages/assets/2025-state-of-software-delivery-report.pdf)). Google reported that of roughly 4.2 million tests on its CI system, about 63,000 had a flaky run over one week, with 14% of its large tests flaky ([Google Testing Blog, 2017](https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html)), and that about 84% of observed pass-to-fail transitions involved a flaky test rather than a real regression ([Google Testing Blog, 2016](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)).

Lost trust is the expensive part, because a suite nobody believes still costs the full runtime. In a survey of 335 developers, 51% reported hitting test flakiness at least weekly, and they ranked lost trust in test results and wasted developer time as more severe consequences than the wasted compute ([Gruber and Fraser, IEEE ICST 2022](https://arxiv.org/abs/2203.00483)).

### Related research, and what it does not say

Telling an agent to run tests isn't the same as telling it which tests mean something, and one study found the generic instruction measured worse than no instruction at all. TDAD, evaluated on SWE-bench Verified, measured a 6.08% baseline regression rate for a coding agent given no special testing instructions. Adding procedural instructions to follow test-driven practices raised regressions to 9.94%, while giving the agent a map of which tests actually covered the change dropped them to 1.82% ([Alonso, Yovine and Braberman, arXiv, March 2026](https://arxiv.org/abs/2603.17973)).

Two caveats. That paper evaluates a dependency-graph tool in the predictive-test-selection category, which is a different category from this one, so none of those numbers are a result for testprune. And testprune has never been evaluated on SWE-bench or measured for its effect on agent regression rate. The only measured result on this page is the single-repository before and after above.

## ❓ FAQ

**Doesn't it just delete tests?**
No, and the proof is that the whole suite still runs. The broad gate executes everything that is left, in 10 minutes. The routine check reached 10 seconds because the fast gate is an explicit selection of 20 files, not because the suite shrank, and the two slowest tests reached 4 seconds because their real wait was found and patched with every assertion intact. A run also writes new tests, since every invariant worth keeping is retargeted at the production path before the test carrying it is removed.

**How do I make my test suite fast enough for a coding agent to run it on every change?**
Make the routine check a short, explicit list of files with zero known failures, and write that command into `CLAUDE.md` or `AGENTS.md` as the default. testprune builds that list, measures it, and writes the policy. The fast gate is an explicit file list rather than a glob or a marker, because a glob drifts and can wander into an ignored, live, or environment-dependent test.

**Is it safe to let an AI delete my tests?**
Deletions are recoverable and the run is auditable, which is the honest version of "safe". Tracked tests go with `git rm` and the ledger records the commit hash you restore from. Untracked tests move to a gitignored archive rather than being deleted, because that operation isn't reversible. In Claude Code it is user-invoked only (`disable-model-invocation: true` in `SKILL.md`), so Claude can't start it on its own. To read the plan before anything changes, run `/testprune prompt-first`.

**How do I know which tests are safe to delete?**
A test becomes a candidate when it exercises an implementation that production doesn't route through, or when it pins wording, numbering, pricing, or model names that the source is expected to keep changing. Both require naming the production path first, with file-level proof. A test that is merely failing is not a candidate: a permanently red test whose expectation can't be corrected with source authority is left red and listed rather than quietly removed.

**Does it work with Jest, Vitest, Go, or Rust, or only pytest?**
testprune is language-agnostic in design. The gate script template takes any runner (`npx jest --`, `go test`, `cargo test --`, `python -m pytest`), and the inventory script recognizes pytest, Jest, Vitest, Go, Rust, and Ruby naming conventions out of the box. The reference snippets are pytest and Vitest, so on a third stack expect to adapt commands rather than concepts.

**How is this different from Launchable or pytest-testmon?**
Those tools decide which of your existing tests to run for a given commit, every commit, forever. testprune changes what the suite contains and how fast it runs, once. A selection tool treats a deprecated-path test as an equally legitimate candidate to run; it has no opinion about whether that test deserves to be in the repository. The two are complementary, and a selection tool works better on a suite that's already been cleaned.

**What if I disagree with one of its decisions?**
Every deletion is listed in the ledger with its recovery hash, and every corrected expectation is listed with the source authority that justified it. Restoring one file is `git show <hash>:path/to/test.py > path/to/test.py`. Items where the evidence wasn't conclusive are written as `Confirm needed` with the competing authorities quoted, and neither side is changed.

## 📁 What's in the repository

| Path | Purpose |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The rules, the 13-step checklist, the execution model, and the safety rules |
| [`references/rationale_and_pitfalls.md`](references/rationale_and_pitfalls.md) | Why each rule exists, and the failure mode behind it |
| [`references/techniques.md`](references/techniques.md) | Sleep spy, measurement, zero-call proof, credential scrub, archive move, registry sweep, hunk-only staging |
| [`references/gate_script_template.sh`](references/gate_script_template.sh) | The gate script: `fast`, `subsystem`, `subsystems`, `broad`, `deprecated`, bash 3.2 compatible |
| [`references/agent_instruction_block.md`](references/agent_instruction_block.md) | The `CLAUDE.md` and `AGENTS.md` policy block, in JSON and Markdown forms |
| [`references/final_report.md`](references/final_report.md) | The closing report format and both visualization templates |
| [`references/prompt_creator.md`](references/prompt_creator.md) | Prompt-first mode: writes a curated, repo-specific prompt |
| [`references/followups_execution.md`](references/followups_execution.md) | Followups mode: adjudicating production authority before any test moves |
| [`scripts/test_inventory.py`](scripts/test_inventory.py) | On-disk versus tracked versus gitignored test modules, any language |

Every rule in `SKILL.md` traces back to something that went wrong in a real repository, and the reasoning is written down in [`references/rationale_and_pitfalls.md`](references/rationale_and_pitfalls.md), so you can disagree with a rule on the merits rather than guessing at its intent.

## 🤝 Contributing and license

Issues and pull requests are welcome, particularly reports from stacks other than Python and JavaScript, since that's where the reference examples are thinnest. If a rule fails you in a real repository, the most useful thing you can open is the case that broke it.

Released under the [MIT License](LICENSE).

If it saves you a suite run, a star helps other people find it.
