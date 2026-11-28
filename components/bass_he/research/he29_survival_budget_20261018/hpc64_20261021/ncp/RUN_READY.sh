#!/usr/bin/env bash
# Run by an authorized NCP executor from the pinned clean hpc64 Git checkout.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
HE29_REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
HE29_CODE_REV="$(git -C "$HE29_REPO_ROOT" rev-parse HEAD)"
HE29_EXPECTED_CODE_REV="${1:?pass the fixed hpc64 code_commit from DELIVERY.json}"
[[ "$HE29_CODE_REV" == "$HE29_EXPECTED_CODE_REV" ]]
HE29_REL=research/he29_survival_budget_20261018
HE29_HPC_LANE="$HE29_REPO_ROOT/$HE29_REL/hpc64_20261021"
HE29_BASE="${HE29_BASELINE_WORK_ROOT:-/root/HE29_REFERENCE_20261020T120000Z}"
HE29_PY="$HE29_BASE/venv/bin/python"
HE29_DATA="${HE29_VERIFIED_DATA_ROOT:-/root/HE29_NCP_20261020T105630Z/checkouts/baseline1569/research/he29_survival_budget_20261018}"
HE29_CTRL="${HE29_CONTROLLER_ROOT:-/root/HE29_NCP_20261020T105630Z/checkouts/controller_ed5adca}"
HE29_STAGE="$(mktemp -d /root/HE29_HPC64_STAGE_XXXXXXXX)"
HE29_PACKED="$HE29_STAGE/packed-a5"
HE29_PACKED_REV=a5d4711460c09b310b78c9692aa62534b7a843d3
HE29_CTRL_REV=ed5adca43f474553a9bce7f5de45d464be5905cb
[[ -x "$HE29_PY" ]]
[[ -d "$HE29_BASE/references" ]]
[[ -d "$HE29_DATA/inputs" ]]
git -C "$HE29_REPO_ROOT" worktree add --detach "$HE29_PACKED" "$HE29_PACKED_REV"
if [[ ! -d "$HE29_CTRL" ]]; then
  HE29_CTRL="$HE29_STAGE/controller-ed5"
  git -C "$HE29_REPO_ROOT" fetch origin "$HE29_CTRL_REV"
  git -C "$HE29_REPO_ROOT" worktree add --detach "$HE29_CTRL" "$HE29_CTRL_REV"
fi
HE29_ARGS=(run --out "$HE29_STAGE/run" --source-revision "$HE29_CODE_REV"
  --packed-root "$HE29_PACKED" --controller-root "$HE29_CTRL"
  --baseline-campaign "$HE29_BASE/references" --binary "$HE29_BASE/build/he29_owner_server"
  --owner-receipt "$HE29_BASE/build/RECEIPT.json" --data-root "$HE29_DATA"
  --table-cache /root/HE29_HPC64_TABLE_CACHE --observe-root /root
  --max-table-workers 48 --max-build-jobs 8 --sync-every 256 --wall-s 900)
if [[ -n "${HE29_REUSED_BRIDGE_BUILD:-}" ]]; then
  HE29_ARGS+=(--bridge-build "$HE29_REUSED_BRIDGE_BUILD")
fi
if [[ -n "${HE29_VIGILODE_CHECKOUT:-}" ]]; then
  HE29_ARGS+=(--vigilode-checkout "$HE29_VIGILODE_CHECKOUT")
fi
if [[ -n "${HE29_CARGO:-}" ]]; then HE29_ARGS+=(--cargo "$HE29_CARGO"); fi
if [[ -n "${HE29_RUSTC:-}" ]]; then HE29_ARGS+=(--rustc "$HE29_RUSTC"); fi
if [[ "${HE29_CARGO_OFFLINE:-0}" == 1 ]]; then HE29_ARGS+=(--offline); fi
HE29_EXIT=0
"$HE29_PY" -B "$HE29_HPC_LANE/src/batch_entry.py" "${HE29_ARGS[@]}" || HE29_EXIT=$?
# Package success, HOLD, or failure exactly once; never resubmit from this script.
"$HE29_PY" -B "$HE29_HPC_LANE/ncp/MAKE_RETURN.py" \
  --run-dir "$HE29_STAGE/run" --archive-dir "$HE29_STAGE/return"
exit "$HE29_EXIT"
