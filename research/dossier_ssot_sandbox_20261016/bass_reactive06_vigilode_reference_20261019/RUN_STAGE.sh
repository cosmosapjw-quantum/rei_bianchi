#!/usr/bin/env bash
set -euo pipefail

BR06_UNIT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BR06_MODE="${1:-verify}"
BR06_WORK="${2:?Usage: bash RUN_STAGE.sh verify|matrix /absolute/new/workspace}"

case "$BR06_MODE" in
  verify)
    exec python3 "$BR06_UNIT_ROOT/scripts/restore_and_verify.py" \
      --root "$BR06_UNIT_ROOT" --work "$BR06_WORK" --mode verify
    ;;
  matrix)
    python3 "$BR06_UNIT_ROOT/scripts/restore_and_verify.py" \
      --root "$BR06_UNIT_ROOT" --work "$BR06_WORK" --mode prepare
    BR06_WORK="$(CDPATH= cd -- "$BR06_WORK" && pwd)"
    export CARGO_HOME="$BR06_WORK/cargo_home"
    export CARGO_TARGET_DIR="$BR06_WORK/target"
    export CARGO_NET_OFFLINE=true
    export CARGO_BUILD_JOBS=2
    export CARGO_INCREMENTAL=0
    export CARGO_PROFILE_DEV_DEBUG=0
    export CARGO_PROFILE_TEST_DEBUG=0
    mkdir -p "$CARGO_HOME"
    case "$(rustc --version)" in
      'rustc 1.94.1 '*) ;;
      *) printf '%s\n' 'Rust 1.94.1 is required.' >&2; exit 2 ;;
    esac
    cd "$BR06_WORK/br06"
    cargo build --release --locked --offline --bin br06_reference
    exec python3 "$BR06_UNIT_ROOT/scripts/run_matrix_r1.py" \
      --binary "$CARGO_TARGET_DIR/release/br06_reference" \
      --source-identity "$BR06_UNIT_ROOT/evidence/implementation/SOURCE_IDENTITY_FINAL.json" \
      --output "$BR06_WORK/matrix" --workers 3 --timeout 600
    ;;
  *) printf '%s\n' 'Mode must be verify or matrix.' >&2; exit 2 ;;
esac
