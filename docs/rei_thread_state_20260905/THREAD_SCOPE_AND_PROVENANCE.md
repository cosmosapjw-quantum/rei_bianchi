# Thread scope and provenance

## Inclusion rule

This package includes only material that directly describes, constrains, verifies, blocks, or advances `rei_bianchi`.

Included domains:

- REI formula and mathematical-oracle work;
- REI runtime bridge, one-attempt governance, repository ruleset, and host-epoch recovery;
- REI-owned reionization, opacity, thermochemistry, OTS, interval, and provider claim boundaries;
- exact BASS/REC/HTT dependencies where REI consumes or is blocked by them;
- external methods used to check REI reasoning;
- Atlassian projections of the REI state;
- the next bounded REI work units.

## Exclusion rule

The package does not reproduce unrelated BASS, REC, or HTT research. Those repositories appear only to preserve ownership, interface, and dependency truth.

Excluded:

- BASS implementation details that do not constrain REI;
- REC source work unrelated to the REI splice;
- HTT observational work unrelated to REI output consumption;
- speculative new physics not developed in this thread;
- any source merge between divergent REI formula and runtime branches;
- native execution, first-interval execution, provider publication, data fitting, or scientific promotion.

## Evidence classes

### `DIRECT_GITHUB_READBACK`

Fresh GitHub commit, tree, pull-request, workflow, ruleset, or ref state read directly during this consolidation.

### `REPOSITORY_BOUND_EVIDENCE`

A result recorded in a file or pull-request body that is itself bound to a Git commit and tree. It may still describe an operator or local execution; its execution class is not upgraded by being committed.

### `OPERATOR_DURABLE_EVIDENCE`

A user-operated command and durable receipt/transcript. Exact reported hashes and statuses are retained, but the consolidation did not independently replay the whole operation.

### `THREAD_SYNTHESIS`

A logical reconciliation of the above evidence. It has no independent authority over source bytes or runtime state.

### `METHOD_ONLY_EXTERNAL`

SciSpace or Wolfram evidence used to check mathematical or reproducibility methodology. It has `authority_effect=NONE` over REI bytes, ownership, runtime admission, attempt budget, provider state, or science claims.

## Source precedence

```text
fresh direct GitHub state
  > exact repository-bound artifact
  > operator durable receipt
  > thread synthesis
  > method-only external literature/tool result
```

A later direct readback supersedes an older locator, but does not silently change the semantics of a completed historical attempt.

## Identity policy

- `BYTE_IDENTITY` requires an exact digest of the exact bytes.
- `GIT_BLOB_IDENTITY` binds repository file bytes through Git object identity.
- `SEMANTIC_IDENTITY` requires a versioned normalization and comparator.
- `PROVENANCE_ONLY` identifies an origin but does not authorize execution.
- `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL` is never promoted to byte identity.
- A branch name, filename, parse success, or textual similarity is not byte identity.

`SOURCE_INDEX.json` uses exact Git blob identities for all indexed package members. It deliberately excludes itself to avoid a self-hash cycle; the enclosing tree and commit bind the index.

## Current exact GitHub sources

### Formula

```text
PR       #62
head     01fd5ea775795d27758f354971ca478f90701295
tree     d802eed60d98e5f2c32189ca0d358cb4f084df09
workflows 33870832194, 33870832204 / success
```

### Runtime/host epoch

```text
PR       #59
head     00d17c932eb41dbae6467e1e2fdf46818799d6db
tree     4752300f2715fba6368811204d159a5d4c2f6465
workflows 33868665546, 33868665599, 33868665555 / success
```

### Runtime path-binding predecessor

```text
PR       #57
head     ab1ea23fd8e3ebe17f46d13d5496bb1db3eba08b
tree     779c06d1e4bf9c54292ad22030cb1b47906af988
```

### Ruleset

```text
id          22240889
name        REI immutable attempt-ledger refs v1
enforcement active
pattern     refs/heads/attempt-ledger/**
rules       update, deletion, non_fast_forward
bypass      none
```

### Final-attempt ref

```text
refs/heads/attempt-ledger/rei-runtime-bridge-ntpath-rebind-20260903-attempt-3
fresh HTTP status 404
classification ABSENT_OBSERVED / authority_effect NONE
```

## Operator evidence incorporated

The following facts are preserved as operator evidence:

- exact Ubuntu Snapshot package identification for the locked compiler;
- current interactive-host compiler drift;
- H1A Docker admission, independent audit, and durable closeout;
- exact receipt and manifest SHA-256 values;
- one remaining native attempt and no attempt-state creation;
- initial independent ruleset audit stop on GitHub-normalized update-rule semantics;
- source repair and later operator-reported independent audit pass;
- Rust 1.94.1 environment helper as a locator only, not a full runtime-closure receipt.

## Atlassian state incorporated

The thread synchronized REI state into:

- Jira `BASS-18`, including the REI formula/runtime and ownership update;
- Jira `BASS-26`, including the four-repository shadow-DAG reconciliation;
- Confluence page `26574849`, successor host-epoch governance;
- Confluence pages `24641542`, `24608769`, and `20611074`, for the four-repository and formula-SSOT projections.

Atlassian is a workflow projection, not formula or code authority. No official dependency-link mutation or workflow transition is implied by this package.
