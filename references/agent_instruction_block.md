# Instruction-file policy block

Add this to the repository's agent instruction files (CLAUDE.md and AGENTS.md, or whichever exist) after the gates are built and measured. If neither file exists, create `CLAUDE.md` containing only a one-line purpose statement and this block in Markdown form. After editing, validate (`json.loads` for JSON files; `diff CLAUDE.md AGENTS.md` must show only the self-name line) and re-run the fast gate once, since nothing else changed. Fill every `{{placeholder}}` with a value you measured or read in this repo; delete a line rather than leave a placeholder. Keep the two files identical except for the self-name line. If the file is JSON, insert the JSON form as a top-level key. If it is Markdown, use the Markdown form. In both cases, move the gate commands to the top of any test-commands list.

## JSON form

```json
"test_suite_policy": {
  "production_authority": "{{PRODUCTION_PATH}} is the only production path tests may certify. {{DEPRECATED_PATHS}} are deprecated code retained for history: write no tests for them, never add parity tests between them and production, and never change production to match them.",
  "default_verification": "Routine check after an edit: `{{FAST_CMD}}` ({{FAST_TIME}}, zero known failures). Then `{{SUBSYSTEM_CMD}}` for the boundary you touched. Run `{{BROAD_CMD}}` ({{BROAD_TIME}}, {{KNOWN_FAILURES}} classified pre-existing failures listed in {{TESTING_DOC}}) only before a push or when asked. Do not use `{{RAW_FULL_SUITE_CMD}}` as a routine check.",
  "new_test_placement": [
    "{{IGNORE_RULE_NOTE}}",
    "Add a file to the fast gate only if it is provider-free, needs no environment value, and runs in well under a second per test; add it to the matching subsystem list in the same script.",
    "Tests that need credentials or make paid or network calls carry `{{LIVE_MARKER}}`, self-skip without their credentials, and never join an automatic gate."
  ],
  "provider_safety": "{{ENV_LOADING_NOTE}} Any test that drives {{TOP_LEVEL_ENTRYPOINT}} must use {{OFFLINE_HELPERS}} and stub {{PAID_SEAMS}}. A test that reaches a provider is a defect, not flakiness.",
  "compatibility_and_alternates": "Tests over rows in a retired format that prove readability, calm refusal, migration, or stored-row contracts are production coverage and stay; no test drives a retired implementation to produce output. {{ALT_BACKENDS}} are admitted by configuration but refused by every production workflow before any call: adapter and pricing tests may certify them, workflow tests may not.",
  "removal_standard": "Do not add skip markers, root conftest skip machinery, or xfail-forever to hide broken tests. A test that no longer describes production is corrected with source authority, or removed with `git rm` (recoverable from history); untracked local tests are parked in the ignored {{ARCHIVE_DIR}}. Do not pin wording, numbering, pricing, or model names that the source is expected to keep changing.",
  "ledger": "Record suite-shaping changes (deletions, gate edits, measured runtimes) in {{TESTING_DOC}} and a {{LEDGER_LOCATION}} ledger, with numbers taken from tool output."
}
```

Commands entries to place first in the test-commands list:

```json
{ "desc": "Fast provider-free gate (default check after an edit)", "cmd": "{{FAST_CMD}}" },
{ "desc": "Subsystem gate for one boundary ({{SUBSYSTEM_NAMES}})", "cmd": "{{SUBSYSTEM_CMD_EXAMPLE}}" },
{ "desc": "Broad provider-free regression (before a push; {{KNOWN_FAILURES}} classified pre-existing failures)", "cmd": "{{BROAD_CMD}}" }
```

## Markdown form

```markdown
## Test suite policy

- Production authority: {{PRODUCTION_PATH}} is the only production path tests may certify. {{DEPRECATED_PATHS}} are deprecated code retained for history: no tests, no parity tests, and production is never changed to match them.
- Default verification: `{{FAST_CMD}}` ({{FAST_TIME}}, zero known failures) after every edit; `{{SUBSYSTEM_CMD}}` for the boundary you touched; `{{BROAD_CMD}}` ({{BROAD_TIME}}, {{KNOWN_FAILURES}} classified pre-existing failures in {{TESTING_DOC}}) only before a push or when asked. Never `{{RAW_FULL_SUITE_CMD}}` as a routine check.
- New tests: {{IGNORE_RULE_NOTE}} Join the fast gate only when provider-free, environment-free, and well under a second per test. Live tests carry `{{LIVE_MARKER}}`, self-skip without credentials, and never join an automatic gate.
- Provider safety: {{ENV_LOADING_NOTE}} Tests that drive {{TOP_LEVEL_ENTRYPOINT}} use {{OFFLINE_HELPERS}} and stub {{PAID_SEAMS}}. Reaching a provider is a defect.
- Compatibility and alternates: tests over retired-format rows that prove readability, calm refusal, migration, or stored-row contracts stay; no test drives a retired implementation. {{ALT_BACKENDS}} are admitted by configuration but refused by every production workflow; adapter and pricing tests only.
- Removal standard: no skip markers, root conftest skip machinery, or xfail-forever. Correct with source authority or `git rm`; park untracked local tests in {{ARCHIVE_DIR}}. Do not pin wording, numbering, pricing, or model names the source is expected to change.
- Ledger: suite-shaping changes go in {{TESTING_DOC}} and a {{LEDGER_LOCATION}} ledger with numbers from tool output.
```

## Placeholder guide

| Placeholder | What to write |
| --- | --- |
| `{{PRODUCTION_PATH}}` | The entrypoint plus the switch that selects it, e.g. `main/orchestrator.py with MAIN_CHAIN_VERSION=v2 (23 stages)` |
| `{{DEPRECATED_PATHS}}` | File names, not descriptions, e.g. `main/orchestrator_V2.py` |
| `{{FAST_CMD}}` / `{{FAST_TIME}}` | The gate command and its measured wall time |
| `{{SUBSYSTEM_CMD}}` / `{{SUBSYSTEM_NAMES}}` | Command form plus the list of subsystem names the script accepts |
| `{{BROAD_CMD}}` / `{{BROAD_TIME}}` / `{{KNOWN_FAILURES}}` | Broad gate command, measured time, and the count of classified pre-existing failures |
| `{{RAW_FULL_SUITE_CMD}}` | The raw runner command agents used to reach for, e.g. `python -m pytest tests/` |
| `{{IGNORE_RULE_NOTE}}` | Only if the repo ignores tests by default, e.g. "`.gitignore` ignores `tests/*`; every new test file must be allowlisted (`!tests/<file>.py`) in the same change or git never sees it." Otherwise delete the line. |
| `{{LIVE_MARKER}}` | e.g. `@pytest.mark.live` |
| `{{ENV_LOADING_NOTE}}` | e.g. "config.py loads a developer .env with real keys." Delete if not true. |
| `{{TOP_LEVEL_ENTRYPOINT}}` / `{{OFFLINE_HELPERS}}` / `{{PAID_SEAMS}}` | The function tests drive end to end, the harness helpers that keep it offline, and the seams to stub |
| `{{ALT_BACKENDS}}` | Backends config admits but the runtime refuses everywhere, by file, e.g. `src/engine/providers/anthropic.ts`; delete the sentence if none |
| `{{ARCHIVE_DIR}}` | e.g. `deprecated_tests_archive/` |
| `{{TESTING_DOC}}` / `{{LEDGER_LOCATION}}` | e.g. `wiki/testing.md` and `PUT_MD_FILES_HERE/session-*` |
