# Follow-ups: executing the high-blast-radius items

Run this in `followups` mode after a testprune pass deferred items whose
"fix" could change production behavior: startup, provider or backend selection,
release gating, schema, or a customer-visible path. Budget: 45 minutes. Every
rule and safety rule in SKILL.md still applies; this file adds the discipline
that phase lacks on its own.

## Principle

**Prove the production boundary before any test moves.** A follow-up item is a
contradiction between two or more of: a comment, the code, a test, a design
document, a CI step. The job is to find which one is the authority, not to make
them agree by editing whichever is cheapest. Production is never changed to make
an alternate backend, a dead helper, or a historical row pass.

## Preflight (five minutes)

1. Recheck HEAD and dirt; the follow-up prompt's base commit may be stale.
   Record the actual HEAD as the recovery authority for every file you touch.
2. Read the repo instruction file and, if the repo keeps a mandatory working
   ledger, read it in full; note its size limit if it has one.
3. Collect exact `file:line` pointers for every claimant in every item before
   deciding anything.

## Per-item adjudication protocol

1. **Name the claimants.** Each thing that asserts a behavior: comment, code
   branch, test title, design-document line, CI step.
2. **Date each claim.** `git log --format='%h %ad %s' --date=short -S"<phrase>"
   -- <file>` for the comment and for the code branch. Read the body and
   `--stat` of the commit that wrote the claim: what did it change, and what
   did it deliberately leave alone?
3. **Rank the authorities.** Design document or invariant manifest, then the
   certifying test that document names, then the commit body that scoped the
   behavior, then the code comment. A comment documents intent; it is not the
   intent. A test a design document names by title is a contract.
4. **Check observability.** Does the runtime log or surface the state (startup
   event, health field, label)? Visible is not silent.
5. **Decide one of two ways.**
   - Conclusive: write the decision with its evidence; add one production-path
     regression pinning the decided behavior across the whole path (config to
     factory to consumer); then apply the smallest fix, which is usually a
     comment, a doc row, or a registry entry, not a runtime change.
   - Inconclusive: write `Confirm needed` with the two strongest competing
     authorities quoted; make no runtime change; add no test that would lock
     in either side.
6. **Park anything that changes the product.** Tightening a fallback into a
   refusal, adding backend support, deleting a production module: product
   decisions. Record them under Parked with files, reason, and prerequisite,
   never as fixes.

## Four recurring shapes

### A. Comment, code, and test disagree

Shape: a config comment says "never silently downgraded"; the factory falls
back to a labeled offline provider when a named backend lacks its key; a
fast-gate test asserts the fallback; the design document names that test.
Resolution: the fallback is the authority; narrow the comment to its true scope;
one regression pins "config admits, factory returns the labeled stub" for every
named backend. Do not make the factory throw.

### B. Config admits an option the runtime refuses everywhere

Shape: an alternate provider passes config and the factory, but every real
workflow checks the provider name and refuses before any call.

1. List every caller of the factory and every gate:
   `grep -rn "resolveProvider(\|provider.name\|config.provider" src`.
   Classify each: refuses, ignores, or would call.
2. Choose exactly one position and write it down: supported partial transport
   (some real workflow completes), retained adapter with no reachable workflow
   (nothing completes), or missing support (a real workflow would call it with
   no fence).
3. Add one boundary test per entry point proving refusal before any call: a
   fake provider whose `complete`/`search` throw, zero calls observed, no rows
   persisted, the exact calm copy read from source with a `file:line` comment.
4. Audit every test that sets the alternate option; classify each as
   adapter-only, pricing, config acceptance, historical-row resume, or defect
   (it lets the option certify a real workflow). Fix only defects.
5. Do not build support and do not delete the adapter in this time box.

### C. A dead transport is still wired

Shape: a route still injects a callback that the receiving function always
discards.

1. Record every caller, type-union member, trace or purpose step name, test
   registry row, and doc key-file entry:
   `grep -rn "<module>\|<function>\|<step_name>" src tests scripts docs wiki`.
2. Run the registry sweep in `techniques.md` so no manifest, matrix, allowlist,
   or doc list still presents the module as live.
3. Check shared unions: a scope or enum member stays if any other writer uses it.
4. Write the retention record: callers, registrations, what stays and why,
   prerequisites (read-only census of stored rows carrying its step names,
   explicit authorization for a production edit, a build gate if a route
   changes), and the ordered removal list.
5. Do not delete the module.

### D. Historical rows versus the retired machine

Shape: tests insert rows in a retired format and assert refusal, readability,
or migration.

- **Production compatibility (keep):** proves stored rows stay readable, are
  refused with the calm retired message, survive migrations, satisfy stored-row
  contracts, or that a legacy env value maps to the current mode.
- **Deprecated-path coverage (remove):** drives the retired implementation to
  produce output.

Produce a table: `file:line`, test title, category, one-line reason. Expect zero
of the second kind after a completed retirement; if one exists, report it, do
not silently delete it. Remove an inert env write only after
`grep -rn <VAR> src` proves nothing reads it, and run that file before and after.

## Release pipeline pin (always, even when no item names it)

When the first pass changed what the default test command means, grep CI
workflows, release scripts, and their orchestration tests for the old command.
Repoint to the broad gate, update the expected-order pin, confirm the trusted CI
profile is still forced strict, run the orchestration test once, record the
count. Confirm every operator script that intentionally runs live tests opts
into the live collection explicitly.

## Execution

- At most two subagents, split by lane with disjoint allowed-file lists (for
  example provider/config/session regressions versus registries and
  historical-mode manifests). Give each the decision, not the question: they
  implement and audit; they do not adjudicate. Read their diffs.
- Verification: the touched file, then the fast gate; one subsystem gate for the
  boundary touched; the broad gate once, only after every runtime-affecting edit
  is final. Typecheck and lint only what you touched unless a production file
  changed.
- A comment-only production edit still triggers the repo's documentation
  protocol (architecture rows, wiki, working ledger).
- Grep design docs for a test's exact title before renaming or deleting it.

## Deliverables

- A new section in the first pass's ledger: per item, the claimants, the dated
  evidence, the decision, test movements, commands, counts, runtimes; then
  Done / Optional / Parked; then files changed.
- Focused regressions and retargeted registries.
- A retention record and removal plan for every module excluded but kept.
- The report in the "Follow-up run" variant of `final_report.md`.

## Red flags: stop and re-read the protocol

| Thought | Reality |
| --- | --- |
| "The comment is newer, so the comment wins." | The scoping commit's body and the design document outrank a comment. |
| "Fail-closed is always safer, so make it throw." | A refusal at startup on a hosted service is a product change. Park it. |
| "This test inserts legacy rows, so it is deprecated coverage." | Readable and refused is production behavior. Keep it. |
| "It is only 70 lines; deleting the dead module is cleaner." | A production edit without authorization, a census, or a build gate. |
| "The subagent said it passed." | Read its diff; check no assertion moved. |
| "I'll run the broad gate now to be safe." | Once, after the last runtime-affecting edit. |
