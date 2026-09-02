#!/usr/bin/env bash
# Layered provider-free test gates.  Template: set RUNNER, fill FAST_GATE and
# the subsystem table, set BROAD_PATHS.  bash 3.2 compatible (macOS default):
# no associative arrays, and the empty-array guard below is required under set -u.
#
#   scripts/run_test_gates.sh fast                 explicit file list, zero known failures, seconds
#   scripts/run_test_gates.sh subsystem <name>     one owning boundary
#   scripts/run_test_gates.sh subsystems           every subsystem in turn
#   scripts/run_test_gates.sh broad                everything provider-free (minutes)
#   scripts/run_test_gates.sh deprecated           local archive only, if it exists
#
# Live, paid, or credentialed tests are documented, never run here.
set -euo pipefail
cd "$(dirname "$0")/.."

# The runner on PATH, never a repo-local virtualenv.  Other stacks:
#   RUNNER="npx jest --"        RUNNER="go test"        RUNNER="cargo test --"
RUNNER="python -m pytest -q -p no:cacheprovider"

# Explicit list.  Add a file only if it is provider-free, environment-free,
# and well under a second per test.  Measure after every change.
FAST_GATE=(
  tests/test_example_request_identity.py
  tests/test_example_accounting.py
)

# One line per owning boundary.  Keep names short; they become CLI arguments.
subsystem_paths() {
  case "$1" in
    transport)     echo "tests/test_example_transport.py tests/test_example_retries.py" ;;
    persistence)   echo "tests/test_example_state.py tests/test_example_resume.py" ;;
    api)           echo "tests/test_example_api.py" ;;
    *)             return 1 ;;
  esac
}
SUBSYSTEM_NAMES="transport persistence api"

# Broad scope.  The runner config (pytest norecursedirs, Jest
# testPathIgnorePatterns, Go build tags) must fence archives, backups, scratch
# and results directories out of collection so this cannot wander.
BROAD_PATHS="tests/"

# Ignored-by-git, never-collected archive of parked untracked tests.
ARCHIVE_DIR="deprecated_tests_archive"

usage() {
  echo "usage: $0 fast | subsystem <${SUBSYSTEM_NAMES// /|}> | subsystems | broad | deprecated" >&2
  exit 2
}

[ $# -ge 1 ] || usage
mode="$1"; shift || true

case "$mode" in
  fast)
    echo "== fast gate (${#FAST_GATE[@]} files) =="
    # shellcheck disable=SC2086
    $RUNNER ${FAST_GATE[@]+"${FAST_GATE[@]}"} ;;
  subsystem)
    [ $# -eq 1 ] || usage
    paths="$(subsystem_paths "$1")" || { echo "unknown subsystem: $1" >&2; usage; }
    echo "== subsystem gate: $1 =="
    # shellcheck disable=SC2086
    $RUNNER $paths ;;
  subsystems)
    for name in $SUBSYSTEM_NAMES; do
      paths="$(subsystem_paths "$name")"
      echo "== subsystem gate: $name =="
      # shellcheck disable=SC2086
      $RUNNER $paths
    done ;;
  broad)
    echo "== broad provider-free gate =="
    # shellcheck disable=SC2086
    $RUNNER $BROAD_PATHS ;;
  deprecated)
    if [ -d "$ARCHIVE_DIR" ]; then
      echo "== deprecated archive (local only, failures expected) =="
      $RUNNER "$ARCHIVE_DIR" || true
    else
      echo "no $ARCHIVE_DIR directory; nothing to run"
    fi ;;
  *)
    usage ;;
esac
