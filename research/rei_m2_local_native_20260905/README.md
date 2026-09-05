# REI M2: first local owner-native calibration evidence

The existing BASS launcher was executed exactly once on the user's workstation
on 2026-09-05. It produced real Wolfram/xCoba output in 8.520384 seconds.
This directory preserves the first result, sequential audits and source
identity; it contains no new launcher or formula implementation.

| Evidence | Observed result |
|---|---|
| Original process status | `PASS_NATIVE_CALIBRATION_ONLY` |
| Original native status | `PASS_NATIVE_TYPED_VIEW_CALIBRATION_ONLY` |
| Wrapper / kernel exit | 0 / 0 |
| Timeout | false; default 360 seconds retained |
| Required checks | 12/12 boolean true; exact ID set |
| Stored scalar residual entries | 416 exact integer zeros, including package and sentinel checks |
| Native receipt failed_ids / messages | [] / [] |
| First code-audit finding | `NATIVE_API_OR_MESSAGE`: raw stdout has one pre-evaluation `Verbose::shdw` warning outside receipt message capture |
| Source / archive / final worktree | unchanged / unchanged / clean |
| Visual readback | Direct PNG/SVG inspection completed; 180 mm screen proxy readable, 90 mm publication readability not admitted |

The component-calibration PASS is observed. A complete message-free kernel
invocation is not claimed. The receipt-only NATIVE_READBACK.json predates the
raw-log code-audit finding; CODE_AUDIT_FINDING.json records that additional
limitation without editing either original native receipt. No nonzero
mathematical residual or local runtime absence was observed.

## Exact source and execution

```text
BASS #130 source commit 477371143f15ef2625a7de21a5d178b09ffc1c32
BASS source tree        fe4c9f9b6deae0bf072dd553cd046c0a4a7801e3
BASS worktree           /home/cosmosapjw/bass/.worktrees/REI-M2-NATIVE-477371143f15-20260905
wolframscript           /usr/bin/wolframscript
resolved executable     /opt/Wolfram/WolframScript/bin/wolframscript
Wolfram Engine          15.0.0 for Linux x86 (64-bit) (May 26, 2026)
xAct archive            /home/cosmosapjw/Downloads/xAct_1.3.0.tgz
xAct archive SHA-256    7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be
native.json SHA-256     5b28385a1e2d80b4e9281675f45c3f4e92c611864c4afdf4852b840f88c5ec33
OUT                     /home/cosmosapjw/research_runs/REI-M2-NATIVE-20260905T024945Z/native
```

OUT was absent at preflight and was created by run_native.py. The surrounding
capture directory holds wrapper logs and source identity; it is outside both
checkouts. The archive was already downloaded and was not downloaded again.
The BASS clone was normally fetched; the worktree is detached and non-shallow,
and no partial/promisor clone was used. Full porcelain was empty before/after.

Executed command (shell variables held the absolute paths above):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  "$BASS_WT/research/diagnostics/bg02_b0_20260905/native/run_native.py" \
  --repo "$BASS_WT" --xact-source "$XACT_ARCHIVE" --output "$OUT"
```

stdout/stderr were redirected to the preserved wrapper logs, and the shell
saved the actual command exit code. No `--timeout` override, replacement raw
kernel executable, source patch, retry, CAS fallback or cleanup was used.

## Publication chain and source distinction

This evidence-only REI child is based on handoff PR #66 at
`28dfc4a348640a61922f90cea0229f2877251a86`, tree
`f57192e949c394810465c0b491dc9357e1400a1c`. Its parent is REI #65.
The live BASS #130 and REI #64/#65 heads/comments were read before execution;
no identical completed native submission was present. #66 was then read as
the existing documentation parent before creating this publication child.

| Anchor | Commit | Tree | Role |
|---|---|---|---|
| BASS #129 | `ac01009dec8678d9f1b8af10fb915b871e2358fd` | `ef10fb3199645e3962fce3ad322e5a23d5971e2f` | Handoff reference anchor; not this run's source |
| REI #64 | `3f2f876b219d5c435cfd5d0dc70236a1edc1fd96` | `87a30c114b00a987beefc34d757a0eb736dc54ba` | Independent sign oracle / visually inspected artifact |
| REI #65 | `7d2fe29d46e3aab4a649c3679ae028e82ef0796c` | `08970b6b35bc749b37be9db6b9aaa6a2848fe06e` | Exceptional algebra oracle / visually inspected artifact |

## Audit and changed next step

PHYS_MATH_AUDIT.md and PHYS_MATH_CODE_AUDIT.md are two sequential passes by
the same assistant, not independent reviewers. The code review classifies
the observed setup/definition warning and proposes a minimal BASS-owner
message-scope correction/adjudication. It does not silently patch the source
or reclassify a reported warning as a failed Einstein equation.

The next single owner task is a versioned BASS registry/consumer amendment,
including explicit resolution of the observed message-scope limitation before
any message-free admission claim. That task is not executed here. The abstract
bridge, exceptional native bridge, constraint propagation and background
evolution remain open; the sentinel is an off-shell witness, not a prediction.

The REI Rust/MPFR production lane is separate. This task neither queried nor
changed its attempt refs/ledger, leases, Section-0 or controller/workers and
does not refresh their current state. It performs no first interval, provider
admission, scientific-status transition, ready/merge/rebase/force-push, or
BASS/REC/HTT source change. Existing dirty/untracked REI work is preserved.

Repository verification, publication and remote readback are reported in the
Draft PR and append-only BASS-18 locator; they are not a second native run.
The original Wolfram stdout includes trailing spaces. They are retained for
byte parity: full `git diff --check` flags only this raw log, while the check
excluding that preserved log passes. No whitespace cleanup is applied to data.
