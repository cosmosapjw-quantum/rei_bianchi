# Git-first handoff: main conversation <-> local Codex

Updated owner instruction: 2026-09-06. Task layer: document.

This replaces the old download/re-upload and mandatory WORK_THREAD routing for
future REI handoffs. It is a delivery convention, not another admission gate,
new experimental authorization, or a requirement to build a handoff framework.
Past receipts and completed WORK_THREAD reviews remain valid historical records.

## Default route

The main conversation performs all feasible research, derivation, coding,
verification, review and publication. Delegate only work that actually needs
the workstation or an unavailable execution capability. Local Codex returns
results directly to the main conversation; no separate work thread is required.

Handoff prompts, small reports and return summaries are committed and pushed to
`cosmosapjw-quantum/rei_bianchi` whenever the available authorized Git path works.
The user should normally paste only one immutable handoff URL or the short Codex
completion output. Do not require them to download a ZIP and re-upload it just
to transport text or review an already published result.

Use the existing task branch/directory when appropriate. An active source branch
has one writer. If it is owned by an ongoing local job, publish independent
handoff documentation on a separate REI branch instead of racing that writer.
Never reset a source branch to an old handoff commit merely to resume the task.

## Main conversation -> Codex

Before delegating, publish the actual task prompt rather than only describing
it in chat. It should identify the source anchor, objective, allowed changes,
protected invariants, acceptance checks and genuinely local work. Reference
already published source/evidence instead of copying old packages repeatedly.

Return a GitHub file URL pinned to its actual commit, plus a brief starting
instruction. A moving branch or PR URL is useful for discovery; the exact file
commit identifies the handed-off version. Repository default/main is not assumed
to be the latest active research line. No automatic dispatch is implied.

## Codex -> main conversation

Reuse an existing equivalent layout; do not create duplicate report families.
A normal small return has:

- `CHATGPT_HANDOFF_KO.md`: actual progress, diagnosed cause versus uncertainty,
  changes, verification, remaining limits and one next action;
- `RETURN_STATUS.json`: tested source commit/tree, actual commands and results,
  invocation counts, changed paths, executed/not-run boundaries and publication
  state; a compact text record is sufficient when JSON adds no useful structure;
- the minimal new logs/results needed to inspect the claim, plus an evidence
  index for larger artifacts. Preserve initial failures; do not rewrite raw logs.

Commit these files with the task result on the authorized REI branch or a narrow
evidence child, then non-force push. Create/update a Draft PR when the task uses
one. A failure or unresolved result can still be published: source/test failure
and successful evidence publication are separate facts. Never wait for a fake
PASS before preserving useful failure evidence.

Keep tested source identity separate from a later evidence-only commit. Obtain
the publication commit after committing; put its immutable file link in console
output or the PR comment. Do not create a commit/manifest self-reference loop to
embed a commit's own unknown SHA inside itself.

The final Codex output should be compact:

```text
STATUS: <actual result, including a precise failure or partial completion>
TESTED_SOURCE: <commit> / <tree>
PUBLISHED_HEAD: <actual pushed commit>
HANDOFF: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/<actual-commit>/<actual-path>/CHATGPT_HANDOFF_KO.md
PR: <actual PR URL, or NOT_CREATED>
NOT_VERIFIED: <remaining limits>
NEXT: <one next action>
```

All placeholders must be replaced by observed values or explicitly marked
unavailable; never emit a fabricated file/PR URL. The user need only paste this
output or the HANDOFF link. The main conversation reads the repository files
through its authenticated connector and reviews the new delta directly.

## Readable evidence first; archives are optional transport

Small Markdown/JSON/CSV and relevant raw text logs belong in Git when safe and
reasonable. Do not place the only usable result inside an opaque ZIP, Git LFS
pointer or local `/home/...` path. Important failure messages, exact test outcomes
and source identities must also be available as ordinary repository text.

Large binaries/full logs may use an existing authorized GitHub artifact, release
asset or other durable storage. Record a stable identifier, retrieval location,
size/hash and retention limit when known. Do not upload large data, introduce LFS,
create releases or use new external storage merely because this convention says
Git-first; use the current task's permission and storage limits. Avoid recursively
embedding previous ZIPs or committing secrets, credentials or private keys.

A summary/index makes review possible when binary access is unavailable; it does
not prove that the reviewer inspected or rehashed the binary. State that limit.
Do not rerun successful experiments solely to recreate a lost download link.

## Publication verification and fallback

A local file or commit is not a push. With Git CLI, check the push exit and compare
the remote branch SHA with the intended published commit. With the GitHub API,
create the commit/ref and read back the ref, changed paths and file contents/blob
identities. Read existing CI if relevant; do not replay science or full regression
suites merely to prove that a handoff document was uploaded.

If this conversation's write route fails, hand publication to local Codex using
the already authorized repository/branch scope. If local Git publication fails,
preserve the committed files, state the precise blocker, and return the compact
text/diff needed to continue. Manual download/upload is a last-resort fallback,
not an obligatory intermediate step and not grounds to hide completed work.

## Autonomous correction without restarting the review loop

Within an approved objective, scope, invariants and acceptance criteria, Codex
may perform multiple evidence-driven edit -> test -> diagnose -> edit iterations.
One repair cycle is not one edit. Return a converged repair and its evidence, not
just another plan at every ordinary implementation failure. Do not weaken a
scientific assumption, fixed input, tolerance or test meaning to obtain PASS.
Stop for a genuine scope/authority/resource boundary or material nonconvergence;
do not reset consumed one-shot network or production allowances. The main
conversation reviews the final changed delta instead of requiring a standing
WORK_THREAD or a new approval for every in-scope correction.

## Scope of this update

Before: repository instructions still included manual archive recovery and an
older default continuation. After: link-only, two-party delivery is specified in
the existing handoff path. This change does not execute or repair the XZ decoder,
re-run the completed index acquisition, admit any first interval/provider, change
runtime locks or write BASS/REC/HTT/global-harness source. Repository merge, ready
transition and force push remain outside the standing handoff publication scope.

Historical versions of these instructions remain available in Git. Do not run
old bootstrap scripts or peer-lock updates just to transmit or read a handoff.
