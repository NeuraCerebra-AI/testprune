# Techniques

Copy-ready snippets for the steps in SKILL.md. Python and pytest examples are shown; adapt the runner command for other stacks.

## Find where a slow test really waits (sleep spy)

Run the slow test with a spy that records every `time.sleep` caller, then read the top frames. Do not guess from the test name.

```bash
python - <<'EOF'
import time, traceback, collections, subprocess, sys
calls = collections.Counter()
real = time.sleep
def spy(seconds):
    frame = traceback.extract_stack(limit=3)[0]
    calls[(frame.filename, frame.lineno, round(float(seconds), 2))] += 1
    real(0)
time.sleep = spy
import pytest
pytest.main(["-q", "-p", "no:cacheprovider", "tests/test_slow_module.py::test_slow_case"])
for (f, line, secs), n in calls.most_common(10):
    print(f"{n:4d} x {secs:6.2f}s  {f}:{line}")
EOF
```

Then, in the test only, neutralize that wait while keeping every retry-budget and fallback assertion:

```python
def _neutralize_offline_retry_backoff_sleeps(monkeypatch):
    real_sleep = time.sleep
    def _zero_sleep(_seconds=0):
        real_sleep(0)          # yields the GIL so polled worker threads still run
    monkeypatch.setattr(time, "sleep", _zero_sleep)
```

## Measure

```bash
python -m pytest -q -p no:cacheprovider --durations=0 tests/  2>&1 | tail -40   # slowest tests + summary
python -m pytest --collect-only -q -p no:cacheprovider tests/ | tail -1          # collected count
/usr/bin/time -p scripts/run_test_gates.sh fast                                  # gate wall time
```

## Prove an "offline" run made no provider call

After a run, scan for new cost or request ledgers in the job or temp directories the code writes to (include hidden directories; `glob` skips them by default):

```bash
python - <<'EOF'
import os, time
recent = []
for root, _dirs, files in os.walk("."):
    for name in files:
        if name.endswith((".jsonl", ".json")) and "cost" in name.lower():
            path = os.path.join(root, name)
            if time.time() - os.path.getmtime(path) < 1800:
                recent.append(path)
print("\n".join(recent) or "no cost ledgers written in the last 30 minutes")
EOF
```

If the harness has a shared "disable paid lanes" helper, every end-to-end test calls it; if it does not, create one in the harness module and use it from every such test.

## Park untracked tests instead of deleting them

Untracked files take a plain `mv`, not `git mv`.

```bash
mkdir -p deprecated_tests_archive
mv tests/test_old_thing.py deprecated_tests_archive/
printf 'Parked tests. Not collected (see norecursedirs / ignore patterns), not tracked. Delete when confident.\n' > deprecated_tests_archive/README.md
echo 'deprecated_tests_archive/' >> .gitignore
```

Fence it from collection: pytest `norecursedirs` in `pytest.ini` / `pyproject.toml`; Jest `testPathIgnorePatterns`; Go build tags; add archives, backups, scratch, and results directories to the same list.

## Allowlist a new test file when tests are ignored by default

```bash
grep -n '^!tests/' .gitignore | tail -3          # find the allowlist block
printf '!tests/test_new_production_invariants.py\n' >> .gitignore
git status --short tests/test_new_production_invariants.py   # must show ?? not nothing
```

## Stage only your hunks in a file shared with other in-progress work

Build the index version from HEAD plus your change, leave the working tree alone:

```bash
python - <<'EOF'
import subprocess, pathlib
path = "CLAUDE.md"
head = subprocess.check_output(["git", "show", f"HEAD:{path}"]).decode()
def apply_my_change(text):
    return text.replace("OLD", "NEW", 1)     # the same edit you made to the working tree
staged = apply_my_change(head)
blob = subprocess.check_output(["git", "hash-object", "-w", "--stdin"], input=staged.encode()).decode().strip()
subprocess.check_call(["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}"])
EOF
git diff --cached --stat        # confirm only your hunk is staged
```

## Validate an instruction file after editing it

```bash
python -c "import json,sys; json.load(open('CLAUDE.md')); print('valid JSON')"   # only if the file is JSON
diff CLAUDE.md AGENTS.md          # expect only the self-name line
```

## Recover a deleted test later

```bash
git show <recovery-hash>:tests/test_removed.py > tests/test_removed.py
```

## Date a claim before trusting it

Find the commit that wrote a comment, a code branch, or a test title; then read what that commit actually changed and what it left alone.

```bash
git log --format='%h %ad %s' --date=short -S"never silently downgraded" -- src/lib/config.ts
git show --stat --format='%H%n%ad%n%B' <hash> | head -60      # body + files touched
git show <hash> -- src/engine/provider.ts | head -40           # empty output = untouched
```

## Registry sweep after de-certifying a module

Run after excluding a module from certification; every hit is a manifest, matrix, allowlist, union, or doc list that may still present it as live.

```bash
grep -rn "importTitle\|shortenImportTitleWithLuna\|import_title" src tests scripts docs wiki README.md 2>/dev/null
```

Classify each hit as caller, type-union member, test registry row, or doc row. Shared union members stay when another writer uses them (`grep -rn 'scope: "import"' src`).

## Scrub credentials and mode variables at the runner setup seam

Stub-at-the-seam catches known calls; scrubbing the environment in the runner's setup file makes an unknown path fail instead of paying. Skip the scrub only for an explicit live collection.

```python
# conftest.py
import os, pytest

SCRUB_PREFIXES = ("LIVE_", "RAILWAY_", "APP_")
SCRUB_EXACT = {"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}

@pytest.fixture(autouse=True, scope="session")
def _hermetic_environment():
    if os.environ.get("TEST_COLLECTION") == "live":
        yield
        return
    for key in list(os.environ):
        if key in SCRUB_EXACT or key.startswith(SCRUB_PREFIXES):
            os.environ.pop(key, None)
    os.environ["APP_PROVIDER"] = "stub"
    yield
```

Vitest and Jest: the same logic in a `setupFiles` module. Operator scripts that intentionally run live tests must set the live collection for the child they spawn.

## Prove the release pipeline still runs the broad gate

```bash
grep -rn "npm test\|test:broad\|pytest tests/" .github/workflows scripts/verify-release* tests/release-gates*   # every place the old command lived
grep -n "GITHUB_ACTIONS\|CI ===\|strict" scripts/verify-release*.mjs   # trusted CI must force the strict profile
npx vitest run tests/release-gates.test.ts                              # or the repo's orchestration test; record the count
```

## Find design documents that name a test title

```bash
grep -rn "falls back to the honest stub when no key is configured" docs wiki README.md
```

A hit means the test title is part of a documented contract: update the document in the same change, or leave the title alone.

## Prove a legacy environment variable is inert before removing it from a test

```bash
grep -rn "COPILOT_INGEST_MODE" src        # comments only = inert
npx vitest run tests/observational-backfill.test.ts   # before and after; counts must match
```
