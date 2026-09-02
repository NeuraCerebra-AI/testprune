# testprune: prompt-creation prompt

Paste everything below the line into a fresh Claude Code or Codex session opened in the target repository. It produces a curated, repo-specific audit prompt (and a companion follow-up prompt), not the cleanup itself.

---

<role>
You are a senior test-infrastructure engineer. Your job in this session is to study THIS repository and then write a curated prompt that a later agent session will execute to prune its automated test suite. You are producing a prompt, not doing the cleanup. Do not delete, move, or rewrite any test in this session.
</role>

<spirit>
The cleanup you are designing has one principle: a test suite must tell the truth about production, cheaply. Concretely:
- Only tests that exercise the code path real users hit can certify a change. Tests of deprecated, experimental, or parallel implementations must not be able to turn the build green or red.
- Tests that are permanently red for documented historical reasons are noise; they get deleted (recoverable from git history) or parked in an ignored archive, never skipped forever.
- Real invariants hiding inside bad tests are retargeted at the production path, not thrown away with the test.
- An agent that wants to check its work needs a default that finishes in seconds, with zero known failures, so it never has to run a 20-minute suite and read a wall of stale failures to learn whether it broke something.
- Everything is measured before and after. Numbers come from tool output, never from memory.
- No paid, networked, or credentialed call is ever made by a test that claims to be offline.
- The curated prompt must make the later session fast: small time budget, minimal verification loop, one or two subagents for independent items, no ceremony.
</spirit>

<phase_1_reconnaissance budget="about 45 minutes, read-only">
Read the repo's own agent instruction file first (CLAUDE.md, AGENTS.md, or equivalent; read only the one for your tool). If a code wiki exists, read its index and testing page before reading code. Then establish, with file paths and line numbers as evidence:

1. Production authority. What actually runs for real users: the entrypoints, deploy configuration, CI workflow, environment switches, and the resolvers that turn environment variables into effective defaults. Name the one production path. Name every deprecated, experimental, legacy, or parallel implementation that still exists in the tree, and prove whether production routes through it (grep call sites, entrypoints, config flags). Record the effective defaults that matter to tests: provider or backend selection, model or version names, feature flags, timeouts, retry counts, modes.
2. Test topology. Test runner and its config files (pytest.ini, pyproject, jest config, go test tags, Makefile targets, package scripts), test directories, naming conventions, fixtures and conftest-style shared files, custom markers, skip machinery, and any repo-local test runner scripts. Count test modules on disk versus tracked in git. Read the ignore rules: an ignored test file is still collected by the runner if it is on disk, so record which tests exist only on this machine.
3. Hazards. Does the repo load a developer env file with real credentials? Which tests can reach paid APIs, networks, databases, email, or deployment tooling if a stub is missing? Which tests are explicitly live or manual? Which files are currently dirty or untracked in git from other in-progress work (run `git status` and list them; the later session must not edit those)?
4. Baseline measurement, only if safe. Before running anything, check the hazards above. If the whole suite can be run without network or credentials (or with network disabled), run it once and record wall time, pass/fail/skip/error counts, and the slowest tests. If it cannot be run safely, do not run it; say so and record the collection count only.
5. Classification. Sort every test module into exactly one bucket, with a one-line reason and evidence:
   - production coverage (exercises the production path or a shared module it uses)
   - deprecated-path coverage (exercises an implementation production does not route through)
   - historical or stale-intent (pins wording, numbering, pricing, model names, or behavior that no longer exists; permanently red or vacuous)
   - live, paid, or credentialed (must never run in an automatic gate)
   - environment-dependent (passes only with a specific local env value)
   - duplicated (same assertion exists elsewhere; note the canonical copy)
   - untracked ad hoc (exists on disk but not in git; note whether it covers production)
   Also flag: oversized test modules, repeated hand-rolled fakes that should be shared, brittle assertions (exact strings, hard-coded counts, snapshot-of-source tests), slow tests and what they actually wait on, and documentation that describes test commands or coverage inaccurately.
6. Blast radius. For every candidate change, assign low (delete or edit a test only, or fix a stale expectation with conclusive source authority), medium (retarget an invariant, add a gate script, change runner config, shared fixtures), or high (anything touching production code, shared fixtures used by many suites, prompt or schema mirrors, frozen artifacts, files dirty from other work). Low and medium are executed by the later session; high is written up as a separate follow-up prompt.
</phase_1_reconnaissance>

<phase_2_write_the_prompt>
Write two files into the repo's conventional results location (or `docs/` if none exists), then print both in full:

A. `testprune_prompt.md`, the curated prompt. It must contain these sections, filled with the concrete names, paths, commands, counts, and numbers you found. No placeholders, no "for example". Anything you could not verify is marked "Confirm needed" inside the prompt.
   1. Role and mission (three sentences).
   2. Production authority: the one production path, the deprecated paths by file name, and the rule that nothing may change production to match a deprecated implementation.
   3. Effective-default map: the source-backed values tests must assume, with file references.
   4. Current state: on-disk versus tracked test counts, the baseline runtime and failure counts (or why there is none), the currently dirty files that must not be edited, and the hazards.
   5. Required audits: one numbered item per problem family you actually found, each naming the files involved and the expected outcome.
   6. Removal standard: tracked deprecated or historical tests are removed with `git rm` (recoverable from the current commit hash, which you write in); untracked ones are moved to an ignored, never-collected archive directory; live tests are marked and excluded from automatic gates; invariants worth keeping are retargeted at production first, with one focused test each; stale expectations are corrected only with conclusive source authority, otherwise left red and listed.
   7. Layered gates to build: a fast gate that is an explicit list of named files with zero known failures, subsystem gates by owning boundary, a broad provider-free gate, an archive gate that runs only if the archive exists, and a documented-only live layer. The runner config must fence archives, backups, scratch and results directories out of collection. Each gate's runtime is measured and written into the testing docs.
   8. Safety rules, verbatim: use the interpreter or toolchain first on PATH; never install or upgrade dependencies unless essential and justified; make no paid, networked, or credentialed external call and keep every validation offline; never run `git restore`, `git checkout --`, `git reset --hard`, or `git stash`; preserve every pre-existing tracked and untracked change; do not edit files dirty from other work, report them instead; do not commit unless explicitly asked; use targeted patches, not whole-file rewrites; do not modify frozen historical artifacts; do not delete the deprecated implementation itself.
   9. Execution model: a total time budget (state it), priority order, permission to launch one or two subagents for independent items with the exact file pointers each needs and a rule that two agents never edit the same file, and a verification loop limited to "run the file you touched, then the fast gate; run one subsystem gate after related items land; run the broad gate once at the end." Forbid re-auditing, py_compile or lint rituals, and repeated broad runs.
   10. Deliverables: the gate script, the archive directory with a README, corrected tests, updated testing docs, a ledger in the results location recording every change with before and after numbers, and a final report.
   11. Final report format: outcome first; then three labeled piles, Done, Optional, Parked, so the reader never wonders whether the job is finished; measured times before and after; files changed; anything left, with the reason. If the `testprune` skill is installed, require its `references/final_report.md` format, including both visualizations.
   12. Stop rule: stop at the time budget and report; a partial result with truthful numbers beats a complete result that was never measured.

B. `testprune_followups_prompt.md`, a shorter prompt for the high-blast-radius items you deferred, in the same style: exact file and line pointers, the same safety rules, a 45-minute budget, one or two subagents allowed, minimal verification. It must also:
   1. Open with the rule "prove the current production boundary before changing tests; do not change production merely to make an alternate provider, dead helper, or historical row pass", and require the executor to run the `testprune` skill in `followups` mode if it is installed.
   2. For every deferred item, name the claimants that disagree (comment, code branch, test title, design-document line, CI step) with `file:line`, state the decision the executor must make, and state the expected outcome if authority is conclusive and the exact words to write if it is not (`Confirm needed`, no runtime change).
   3. Require one production-path regression before the smallest fix, and forbid deleting a deprecated module; require instead a retention record (callers, registrations, shared unions that stay, removal prerequisites) and a separate production-removal plan.
   4. Require the historical-compatibility versus deprecated-path split for any legacy-row tests, with a per-test table, and forbid deleting schema, migrations, refusal paths, or their tests.
   5. Require the release-pipeline pin: prove the release verifier and CI still run the broad gate under the strict trusted profile, and update the orchestration test's expected command list if the default test command changed meaning.
   6. Require the report in the "Follow-up run" variant of `references/final_report.md`.

Quality bar for both prompts: every file name, command, count, and number is something you saw in this session; the prompt is under 2,000 words; sentence case; no jargon the later agent could misread; deprecated paths are named so a "v2" in a test name is never confused with a "v2" production mode or vice versa.
</phase_2_write_the_prompt>

<final_message>
In under 200 words: where the two prompt files are, the production path you identified and the deprecated paths you found, the baseline numbers (or why none), the bucket counts from the classification, and the three or four highest-value items the curated prompt will execute.
</final_message>
