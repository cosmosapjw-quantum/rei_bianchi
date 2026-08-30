# Local executor prompt V2: prompt-only REI-LOCAL-01 continuation

Attach **this file alone** to the local executor. It contains every immutable
publication value needed to recover the exact locator; no separately attached
`FETCH_AND_VALIDATE.py`, publishing response, commit SHA, or PR URL is needed.

You are continuing `cosmosapjw-quantum/rei_bianchi`. The current scientific
claim remains `NO_PASS_FIRST_CANONICAL_INTERVAL`. The earlier
`BLOCKED_BY_MISSING_LOCATOR` stop is resolved only by the authenticated
materialization below. Do not search the filesystem for another locator, do not
reconstruct one, and do not substitute `FETCH_AND_VALIDATE.sh`.

## Immutable delivery authority

Use these literal values. A branch or PR ref is transport-only and never
authority for object identity.

```text
REPOSITORY=cosmosapjw-quantum/rei_bianchi
REPOSITORY_URL=https://github.com/cosmosapjw-quantum/rei_bianchi.git
PR14_SOURCE_COMMIT=053b97c56e089e28a83f37d79a4128ed3cdae9f4
PR14_SOURCE_TREE=46a96c789a691d671644685893a552cd9486788d
DELIVERY_BASE_COMMIT=1893f12d14b212eb4b6bd637332824f692e6f4b3
DELIVERY_BASE_TREE=773fcdc4d1ab115fa0542d26ba67af5c086f450b
DELIVERY_TERMINAL_COMMIT=04a353339c0fe517ac5209a78bc57b49b8006f77
DELIVERY_TERMINAL_TREE=6cde78286be28f1c4077e389f3b8bab8373c5a9d
DELIVERY_PAYLOAD_COMMIT=4d6bf6a356f8e944d20fd1e2423d8db55f5961b7
DELIVERY_PAYLOAD_TREE=7c01b545b6f30b9b43c290ad0757f9a564972c97
DELIVERY_BRANCH=agent/handoff/rei-local-01-bootstrap-spec-20260830-r1
DELIVERY_DRAFT_PR=https://github.com/cosmosapjw-quantum/rei_bianchi/pull/19
LOCATOR_PATH=handoff/rei_local_01_source_bound_paired_map_20260830/FETCH_AND_VALIDATE.py
LOCATOR_BLOB=0f43968815b8fa8da3a7d426c07af294e46fcc6a
LOCATOR_SHA256=241f5f5722b9eda0f9fbbd8600da80907e3056fca3d04dc4c52ba48927c6579c
```

PR #19 is the sealed delivery. Do not edit, amend, rebase, force-push, merge,
mark ready, or otherwise update its branch. Its exact terminal commit is the
base for the later isolated local implementation.

## Prompt-only locator bootstrap

Resolve `REI_REPO` to the existing absolute path of the non-bare, non-shallow
SHA-1 `rei_bianchi` worktree. Preserve every existing worktree and every
dirty/staged/untracked path. If more than one repository candidate remains
after checking its `origin` URL and exact PR14 source commit, report the
candidates and stop; do not guess.

Create one new private directory outside every Git worktree and Git directory,
then export both absolute paths. For example:

```bash
export REI_REPO=/absolute/path/to/rei_bianchi
export REI_PIN_ROOT="$(mktemp -d /tmp/rei-local-01-prompt-v2.XXXXXXXX)"
chmod 0700 "$REI_PIN_ROOT"
```

Run the following block verbatim under Bash. This one bounded bootstrap is
explicitly authorized to fetch the exact PR #19 terminal object without
updating a ref or `FETCH_HEAD`. If the server rejects direct SHA transport, the
literal PR #19 source ref may be used once with the same empty refmap; the
fetched ref tip is not trusted. Exact commit, tree, path, blob, and raw digest
checks remain mandatory.

<!-- BEGIN EXECUTABLE_BOOTSTRAP_V2 -->
```bash
set -euo pipefail
umask 077

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

: "${REI_REPO:?REPOSITORY_POLICY: export an absolute REI_REPO}"
: "${REI_PIN_ROOT:?PIN_ROOT_POLICY: export an absolute REI_PIN_ROOT}"

case "$REI_REPO" in /*) ;; *) fail "REPOSITORY_POLICY: REI_REPO must be absolute" ;; esac
case "$REI_PIN_ROOT" in /*) ;; *) fail "PIN_ROOT_POLICY: REI_PIN_ROOT must be absolute" ;; esac
[ -d "$REI_REPO" ] || fail "REPOSITORY_POLICY: REI_REPO is not a directory"
[ -d "$REI_PIN_ROOT" ] || fail "PIN_ROOT_POLICY: REI_PIN_ROOT is not a directory"

REI_REPO="$(cd -- "$REI_REPO" && pwd -P)"
REI_PIN_ROOT="$(cd -- "$REI_PIN_ROOT" && pwd -P)"
case "$REI_PIN_ROOT/" in
  "$REI_REPO/"*) fail "PIN_ROOT_POLICY: pin root is inside the selected worktree" ;;
esac

pin_mode="$(stat -c '%a' -- "$REI_PIN_ROOT")"
(( (8#$pin_mode & 077) == 0 )) || fail "PIN_ROOT_POLICY: pin root must not grant group/other access"

DELIVERY_TERMINAL_COMMIT=04a353339c0fe517ac5209a78bc57b49b8006f77
DELIVERY_TERMINAL_TREE=6cde78286be28f1c4077e389f3b8bab8373c5a9d
DELIVERY_PAYLOAD_COMMIT=4d6bf6a356f8e944d20fd1e2423d8db55f5961b7
DELIVERY_PAYLOAD_TREE=7c01b545b6f30b9b43c290ad0757f9a564972c97
DELIVERY_BASE_COMMIT=1893f12d14b212eb4b6bd637332824f692e6f4b3
DELIVERY_BASE_TREE=773fcdc4d1ab115fa0542d26ba67af5c086f450b
PR14_SOURCE_COMMIT=053b97c56e089e28a83f37d79a4128ed3cdae9f4
PR14_SOURCE_TREE=46a96c789a691d671644685893a552cd9486788d
DELIVERY_TRANSPORT_REF=refs/heads/agent/handoff/rei-local-01-bootstrap-spec-20260830-r1
LOCATOR_PATH=handoff/rei_local_01_source_bound_paired_map_20260830/FETCH_AND_VALIDATE.py
LOCATOR_BLOB=0f43968815b8fa8da3a7d426c07af294e46fcc6a
LOCATOR_SHA256=241f5f5722b9eda0f9fbbd8600da80907e3056fca3d04dc4c52ba48927c6579c
LOCATOR_TARGET="$REI_PIN_ROOT/FETCH_AND_VALIDATE.py"

if [ -e "$LOCATOR_TARGET" ] || [ -L "$LOCATOR_TARGET" ]; then
  fail "TARGET_ALREADY_EXISTS: $LOCATOR_TARGET"
fi

run_git() (
  unset GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_CEILING_DIRECTORIES GIT_COMMON_DIR
  unset GIT_DIR GIT_DISCOVERY_ACROSS_FILESYSTEM GIT_GRAFT_FILE
  unset GIT_IMPLICIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE GIT_OBJECT_DIRECTORY
  unset GIT_PREFIX GIT_QUARANTINE_PATH GIT_REPLACE_REF_BASE GIT_SHALLOW_FILE
  unset GIT_SUPER_PREFIX GIT_WORK_TREE
  for name in ${!GIT_CONFIG@}; do
    unset "$name"
  done
  export LC_ALL=C LANG=C GIT_NO_REPLACE_OBJECTS=1 GIT_OPTIONAL_LOCKS=0
  export GIT_NO_LAZY_FETCH=1
  exec git --no-replace-objects -C "$REI_REPO" "$@"
)

[ "$(run_git rev-parse --is-bare-repository)" = false ] ||
  fail "REPOSITORY_POLICY: a non-bare worktree is required"
[ "$(run_git rev-parse --is-shallow-repository)" = false ] ||
  fail "REPOSITORY_POLICY: a full non-shallow history is required"
[ "$(run_git rev-parse --show-object-format)" = sha1 ] ||
  fail "REPOSITORY_POLICY: SHA-1 Git objects are required"

reject_pin_root_below() {
  local protected_root="$1"
  case "$REI_PIN_ROOT/" in
    "$protected_root/"*) fail "PIN_ROOT_POLICY: pin root is inside $protected_root" ;;
  esac
}
reject_pin_root_below "$(run_git rev-parse --show-toplevel)"
reject_pin_root_below "$(run_git rev-parse --path-format=absolute --git-dir)"
reject_pin_root_below "$(run_git rev-parse --path-format=absolute --git-common-dir)"
while IFS= read -r -d '' worktree_field; do
  case "$worktree_field" in
    "worktree "*) reject_pin_root_below "${worktree_field#worktree }" ;;
  esac
done < <(run_git worktree list --porcelain -z)

fetch_args=(
  fetch
  --no-tags
  --no-write-fetch-head
  --no-recurse-submodules
  --no-auto-maintenance
  --no-write-commit-graph
  --no-filter
  --refetch
  --refmap=
  origin
)
if ! run_git "${fetch_args[@]}" "$DELIVERY_TERMINAL_COMMIT"; then
  printf '%s\n' "FETCH_NOTICE: direct SHA transport unavailable; trying pinned PR19 source ref without a refmap" >&2
  run_git "${fetch_args[@]}" "$DELIVERY_TRANSPORT_REF" ||
    fail "FETCH_UNAVAILABLE: neither exact SHA nor pinned transport ref closed the object graph"
fi

object_state_before="$(run_git count-objects -v | sha256sum | cut -d ' ' -f 1)"
[ "$(run_git rev-parse --verify "${DELIVERY_TERMINAL_COMMIT}^{commit}")" = "$DELIVERY_TERMINAL_COMMIT" ] ||
  fail "OBJECT_MISMATCH: delivery terminal commit"
[ "$(run_git rev-parse --verify "${DELIVERY_TERMINAL_COMMIT}^{tree}")" = "$DELIVERY_TERMINAL_TREE" ] ||
  fail "OBJECT_MISMATCH: delivery terminal tree"
[ "$(run_git rev-list --parents -n 1 "$DELIVERY_TERMINAL_COMMIT")" = "$DELIVERY_TERMINAL_COMMIT $DELIVERY_PAYLOAD_COMMIT" ] ||
  fail "OBJECT_MISMATCH: delivery terminal parent"
[ "$(run_git rev-parse --verify "${DELIVERY_PAYLOAD_COMMIT}^{tree}")" = "$DELIVERY_PAYLOAD_TREE" ] ||
  fail "OBJECT_MISMATCH: delivery payload tree"
[ "$(run_git rev-list --parents -n 1 "$DELIVERY_PAYLOAD_COMMIT")" = "$DELIVERY_PAYLOAD_COMMIT $DELIVERY_BASE_COMMIT" ] ||
  fail "OBJECT_MISMATCH: delivery payload parent"
[ "$(run_git rev-parse --verify "${DELIVERY_BASE_COMMIT}^{tree}")" = "$DELIVERY_BASE_TREE" ] ||
  fail "OBJECT_MISMATCH: delivery base tree"
[ "$(run_git rev-parse --verify "${PR14_SOURCE_COMMIT}^{commit}")" = "$PR14_SOURCE_COMMIT" ] ||
  fail "OBJECT_MISMATCH: PR14 source commit"
[ "$(run_git rev-parse --verify "${PR14_SOURCE_COMMIT}^{tree}")" = "$PR14_SOURCE_TREE" ] ||
  fail "OBJECT_MISMATCH: PR14 source tree"
[ "$(run_git rev-parse --verify "${DELIVERY_TERMINAL_COMMIT}:${LOCATOR_PATH}")" = "$LOCATOR_BLOB" ] ||
  fail "OBJECT_MISMATCH: locator path/blob"
[ "$(run_git cat-file -t "$LOCATOR_BLOB")" = blob ] ||
  fail "OBJECT_MISMATCH: locator object type"

candidate="$(mktemp "$REI_PIN_ROOT/.FETCH_AND_VALIDATE.py.XXXXXXXX")"
cleanup_candidate() {
  rm -f -- "$candidate"
}
trap cleanup_candidate EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

run_git cat-file blob "$LOCATOR_BLOB" >"$candidate"
object_state_after="$(run_git count-objects -v | sha256sum | cut -d ' ' -f 1)"
[ "$object_state_after" = "$object_state_before" ] ||
  fail "UNEXPECTED_OBJECT_STORE_MUTATION: authenticated reads caused object growth"
observed_sha256="$(sha256sum -- "$candidate" | cut -d ' ' -f 1)"
if [ "$observed_sha256" != "$LOCATOR_SHA256" ]; then
  fail "LOCATOR_SHA256_MISMATCH: expected $LOCATOR_SHA256 observed $observed_sha256"
fi
chmod 0500 "$candidate"
ln -- "$candidate" "$LOCATOR_TARGET" ||
  fail "TARGET_ALREADY_EXISTS_OR_UNAVAILABLE: $LOCATOR_TARGET"
rm -f -- "$candidate"
candidate=
trap - EXIT HUP INT TERM

[ "$(sha256sum -- "$LOCATOR_TARGET" | cut -d ' ' -f 1)" = "$LOCATOR_SHA256" ] ||
  fail "LOCATOR_SHA256_MISMATCH_AFTER_PUBLISH: $LOCATOR_TARGET"
printf 'LOCATOR_READY=%s\n' "$LOCATOR_TARGET"
```
<!-- END EXECUTABLE_BOOTSTRAP_V2 -->

Do not proceed unless the block exits zero and prints `LOCATOR_READY` for the
new exact file. On Git 2.43 the unconditional explicit `--no-filter --refetch`
is what closes the reachable object graph before any authenticated read.
`GIT_NO_LAZY_FETCH=1` is defense in depth for Git versions that recognize it,
not bootstrap authority. Never invent an unsupported Git CLI option.

## Mandatory immutable transport

Use fresh paths inside the private root. The destination and receipt must not
already exist. Run normal locator mode exactly once and save its complete
stdout outside both output paths:

```bash
set -euo pipefail
umask 077

export REI_INTAKE="$REI_PIN_ROOT/upstream-intake"
export REI_RECEIPT="$REI_PIN_ROOT/upstream-intake.locator-receipt.json"
export REI_LOCATOR_STDOUT="$REI_PIN_ROOT/locator.stdout.json"
export REI_VERIFY_STDOUT="$REI_PIN_ROOT/verify.stdout.json"

run_pinned_locator() {
  python3 -I -B -c '
import hashlib, os, stat, sys
path = sys.argv[1]
expected = "241f5f5722b9eda0f9fbbd8600da80907e3056fca3d04dc4c52ba48927c6579c"
flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
descriptor = os.open(path, flags)
try:
    before = os.fstat(descriptor)
    with os.fdopen(descriptor, "rb", closefd=False) as stream:
        raw = stream.read()
    after = os.fstat(descriptor)
finally:
    os.close(descriptor)
identity = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_size)
if identity(before) != identity(after) or not stat.S_ISREG(before.st_mode):
    raise SystemExit("LOCATOR_IDENTITY_MISMATCH")
if hashlib.sha256(raw).hexdigest() != expected:
    raise SystemExit("LOCATOR_SHA256_MISMATCH_AT_EXECUTION")
sys.argv = [path, *sys.argv[2:]]
scope = {"__name__": "__main__", "__file__": path, "__package__": None}
exec(compile(raw, path, "exec"), scope, scope)
' "$REI_PIN_ROOT/FETCH_AND_VALIDATE.py" "$@"
}

run_pinned_locator \
  --repo "$REI_REPO" \
  --destination "$REI_INTAKE" \
  --receipt "$REI_RECEIPT" \
  >"$REI_LOCATOR_STDOUT"

python3 -I -B -c '
import json, sys
observed = json.load(open(sys.argv[1], encoding="utf-8"))
expected = {
    "transport_status": "PASS_IMMUTABLE_PAYLOAD_ONLY",
    "scientific_validation": "NOT_RUN",
    "canonical_adapter": "NOT_RUN",
    "pilot_46080x3": "NOT_RUN",
    "first_interval": "NO_PASS",
    "pr14_disposition": "RECORDED_BLOCKED_MINIMUM_STEP",
}
if any(observed.get(key) != value for key, value in expected.items()):
    raise SystemExit("LOCATOR_RESULT_MISMATCH")
' "$REI_LOCATOR_STDOUT"

REI_RECEIPT_SHA256="$(python3 -I -B -c '
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))["receipt_sha256"]
if len(value) != 64 or not set(value) <= set("0123456789abcdef"):
    raise SystemExit("INVALID_RECEIPT_SHA256")
print(value)
' "$REI_LOCATOR_STDOUT")"
export REI_RECEIPT_SHA256

run_pinned_locator \
  --destination "$REI_INTAKE" \
  --verify-receipt "$REI_RECEIPT" \
  --expected-receipt-sha256 "$REI_RECEIPT_SHA256" \
  >"$REI_VERIFY_STDOUT"

python3 -I -B -c '
import json, sys
observed = json.load(open(sys.argv[1], encoding="utf-8"))
if observed.get("status") != "PASS_DESTINATION_BINDING":
    raise SystemExit("DESTINATION_BINDING_MISMATCH")
' "$REI_VERIFY_STDOUT"
```

Require the normal result to contain exactly these scientific/transport claim
values (additional authenticated observational fields are allowed):

```text
transport_status      PASS_IMMUTABLE_PAYLOAD_ONLY
scientific_validation NOT_RUN
canonical_adapter     NOT_RUN
pilot_46080x3         NOT_RUN
first_interval        NO_PASS
pr14_disposition      RECORDED_BLOCKED_MINIMUM_STEP
```

Require `status: PASS_DESTINATION_BINDING` in the fresh verification output.
Retain `REI_RECEIPT_SHA256` from locator stdout as external authority; never
derive it by hashing the writable receipt. Receipt verification mode may be
repeated immediately before use, but normal locator mode must not be repeated.

`remote_ref_status` may be `MATCH`, `DRIFT`, or `NOT_CHECKED`; it is
observational. Exact object, receipt digest, destination identity, or closure
mismatch is fatal. The locator requires Linux `renameat2`, `O_TMPFILE`, and
`/proc/self/fd`. On retained-stage errors, act only on a pathname whose reported
`stage_path_status` is `MATCHES_BOUND_IDENTITY` and whose device/inode match.
Never remove a substituted reported name. `STAGE_PRIVACY_FAILURE` (exit 41)
requires manual containment before proceeding.

## Repository preservation and delivered specification

Before implementation, snapshot every existing worktree plus every
dirty/staged/untracked path, ref, index, pseudoref, shallow marker, and current
HEAD. The locator itself enforces repository-state preservation while allowing
only object-database growth. If any existing state changed, stop without reset,
clean, stash, or repair.

Create one new sibling worktree from the exact delivery terminal
`04a353339c0fe517ac5209a78bc57b49b8006f77`. Never alter PR #14, PR #18, PR
#19, the R2 stage, old evidence, tables, blocked archive, or
`external/rec_bianchi.lock.json`.

The sealed delivery provides:

- `handoff/rei_local_01_source_bound_paired_map_20260830/CONTRACT.json`;
- `docs/superpowers/specs/2026-08-30-rei-source-bound-paired-map-adapter-design.md`;
- `docs/superpowers/plans/2026-08-30-rei-source-bound-paired-map-adapter.md`.

Read all three completely before editing. Finalize an explicit
`INPUT_LOCK.json` over the complete imported/dynamically-loaded/copied/opened
code and data closure; the named plan tables are minimum roots only.
Undeclared runtime imports or opens reject. Use the pinned primitive-level
outward interval/PCHIP backend, or an equivalently verified pinned replacement,
with independent high-precision oracle tests.

## Authorized local implementation

Execute only REI-LOCAL-01. Implement:

```text
src/rei_bianchi/correlated_map_adapter.py
src/rei_bianchi/joint_implicit_remainder.py
src/rei_bianchi/source_bound_mprk_sdirk_operator.py
stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/
```

Retain one immutable dependency registry across the full step, first half, and
second half. Full and first-half start from the same parent realization.
Second-half receives the complete first-half affine state, including all
source/global/mixed/remainder owners. Distinct physical source sites remain
independent unless a pinned authority record permits an alias.

Certify the full 2x2 H and 3x3 He population implicit systems before invariant
projection and the whole thermal residual. Temperature/state-dependent
photoheating/context must be in the total derivative or a separately proved
outer self-inclusion. A point solve, midpoint Jacobian, or frozen-context root
is insufficient.

Bind the real four-site map only through `LockedMPRK22SDIRK2Operator`.
Recompute each site's coefficients and remainders from that site's state, time,
forcing, and owners. Certify every Patankar, `q_He,ion`, absorption/owner
normalization, OTS, energy, and forcing denominator before division. The
existing interval wrapper is a comparison oracle only, never runtime code.

Every population solve and thermal predictor/gamma/final residual needs its own
source-bound full-enclosure certificate. Gate the physical state cone at every
parent, predictor, substage, endpoint, and public transform. Resolved OTS heat
enters thermal photoheat and the resolved ledger exactly once; unresolved OTS
is ledger-only.

Integrated ledgers must consume all four authenticated site models on one
dependency registry and prove joint feasibility; separate marginal intervals
that each contain zero are insufficient. Localize the earliest validated table
event, reject without candidate mutation, rebuild topology, and restart.
Non-monotone or uncertified event tubes fail closed.

Transform both endpoints to dependency-preserving public coordinates first,
then form two-half minus full by owner ID, range the same-site `vf` polynomial,
and subtract asymmetric endpoint remainder intervals as
`[H_lower-F_upper, H_upper-F_lower]` unless a direct delta remainder has its own
certificate. Only then project to intervals. Do not subtract interval widths or
endpoints. Reconstruct `x_HII=1-x_HI` and
`x_HeII=1-x_HeI-x_HeIII`; public helium remainders use the same owner with
opposite sign (or an equivalent sum-zero constrained block), never independent
species boxes.

Use TDD for every slice and record meaningful RED, minimal GREEN, refactor, and
regression commands. Required proof includes:

- an independently solved nonlinear fixture;
- locked node `38382` static-hull RED/adapter containment with its pinned
  full-field aggregate/global context;
- point-degenerate three-lane parity;
- deterministic `REIAFF1` split restart preserving complete authenticated
  certificate payloads;
- transaction rollback;
- mutation detection for dropped remainder, false alias, frozen photoheat,
  reversed difference, relaxed strict comparison, and one-lane acceptance.

Run only bounded node-local propagation against the authenticated full-field
aggregate/global context, or the locked full-field fixture while asserting only
node `38382`. Never renormalize a one-node slice. Do not run the canonical
all-46,080-node three-lane pilot; that is REI-LOCAL-02.

Even on local success, report exactly:

```text
adapter             IMPLEMENTED_AND_LOCALLY_CERTIFIED
canonical_pilot     NOT_RUN
first_interval      NO_PASS
scientific_pass     NOT_CLAIMED
performance         NONE
```

Run one independent PHYS-MATH audit followed by one independent PHYS-MATH-CODE
audit. Permit at most one bounded P0/P1 repair and differential retest. If any
certificate or gate fails, preserve the earliest exact failure and remove all
stale pass fields.

## Local publication boundary

If and only if local implementation, tests, manifests, protected-input hashes,
and both audits pass, create one new branch and one stacked draft PR against the
PR #19 delivery branch. Use object creation and a single new-branch creation;
never update an existing ref. Read back exact head/tree/base/changed paths and
checks. Mock merge eligibility with read-only compare/status/PR metadata. Do
not call a merge API because it has no dry-run mode.

Return exact commits, trees, blobs, raw SHA-256 values, test commands/counts,
audit verdicts, remaining blockers, and links. Never replace
`NO_PASS_FIRST_CANONICAL_INTERVAL` unless a later separately authorized full
pilot and original-start interval proof satisfy their own contracts.
