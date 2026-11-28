# BASS_HE R8 -> R9 handoff: ARSENY author-code normalization audit

## Purpose

Resolve the remaining CPC 2023 Eq.(52)/Eq.(55)/Eq.(56) normalization conflict by **read-only static inspection of the public author ARSENY program package**. Do not reopen CODE-I02 and do not import/copy author implementation code into the clean-room BASS_HE implementation.

## Frozen project state

Repository: `cosmosapjw-quantum/BASS_HE`

Before any work fresh-read:
- PR #15 `audit11/dr11h-certificate-binding`; expected HEAD `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`.
- PR #17 `research/shared-c64-crossrepo-20260928`; read the newest R7 closeout and R8 source-normalization namespace.
- root `AGENTS.md`.

Inherited gates:
- `CODE_I02_CLOSED=true`
- `full_certificate_fail_closed=true`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`

Do not rerun the closed CODE-I02 hostile matrix, focused/full suite, 56-action replay, worker sweep, or DR9B benchmark unless a newly changed dependency exists. This node changes no clean-room source.

## Authoritative source identities

CPC paper:
- Gusev, Solov'ev, Vinitsky, CPC 286 (2023) 108662
- DOI `10.1016/j.cpc.2023.108662`
- authorized PDF `1-s2.0-S0010465523000073-main.pdf`
- expected size `961962`
- expected SHA256 `1367f5ab3239cad1b3ea377edb28a9b9e6975f4cec27fb6d289fdb1d601b1c55`

Author program dataset:
- DOI `10.17632/n43srxwdnm.1`
- Version 1
- dataset title token `ARSENY`
- license: CC BY 4.0
- language: FORTRAN 90/95

A previously prepared fetcher exists as `FETCH_ARSENY_MENDELEY.py`. Treat it as retrieval tooling, not scientific authority.

## Source facts already closed by R8

Do not rediscover these unless checking provenance:

1. PDF p.12 Eq.(52): `p_k=exp[-Delta_k(rho)/v]`, explicitly an **elementary-transition probability**, used in Eq.(51) probability matrices.
2. PDF p.13 Eq.(55): `P^Q=exp[-2 Delta/v]`, explicitly the **single-pass transition probability**.
3. PDF p.13 Eq.(56): Delta is the complex contour/action Stückelberg parameter.
4. Program description: STCKLBR2 computes Eq.(56) parameters and these are used in subsequent calculations; CR_SECTION computes Eq.(54).
5. CPC Eq.(43) prints `Delta=pi DeltaE_min/(4 DeltaF)` without a square, whereas Richter-Solov'ev 1993 prints `Delta=pi (DeltaE_min)^2/(4 DeltaF)` and factor-two probability. Do not silently correct either source.
6. Wolfram: repeated Eq.(51) stochastic matrices give `2p(1-p)`, not `p^2`; Eq.(50) double traversal does not algebraically explain Eq.(55).

## Phase A: provider retrieval and provenance

1. Use a fresh isolated working directory. Do not edit/reset user worktrees.
2. Retrieve dataset metadata and files from Digital Commons Data / Mendeley using the public API. Preferred prepared command:

   `python FETCH_ARSENY_MENDELEY.py --dataset-id n43srxwdnm --version 1 --out ARSENY_MENDELEY_v1`

3. If the visible slug is not accepted by the provider, resolve the provider-internal dataset ID from the public record/API. Do not guess a neighboring dataset.
4. Verify dataset DOI/title/version/license, file IDs, sizes and provider SHA256 where exposed. Preserve raw metadata and original bytes append-only.
5. Produce `AUTHOR_SOURCE_MANIFEST.json` with every file's relative path, byte size, SHA256, provider hash and provenance.
6. Do not compile or execute author code in this phase.

If network/authentication blocks retrieval, return `AUTHOR_SOURCE_RETRIEVAL_BLOCKED` with HTTP/provider evidence. Do not substitute the clean-room implementation for the missing author source.

## Phase B: static exponent/data-flow trace

Search the actual author source case-insensitively for at least:
- `STCKLBR2`, `STCKLBRG`, `STUCKELBERG`, `CR_SECTION`, `SECTION`, `C_S_AT`
- `EXP`, `DEXP`, `DELTA`, velocity variables, probability variables
- reads/writes of `stuckelberg.dat` or `STCKLBR2.dat`
- construction of the Eq.(51)/(53)-equivalent transition matrix.

Build a line-numbered static call/data-flow trace from the Eq.(56) parameter to the probability actually placed in the crossing matrix. Preserve short source excerpts only as permitted by CC BY 4.0 and cite original file/line/hash.

The decisive classification is one of:

- `AUTHOR_USES_FACTOR1_DIRECT`: author code applies `exp(-Delta/v)` to the Eq.(56)-derived stored Delta;
- `AUTHOR_USES_FACTOR2_DIRECT`: author code applies `exp(-2*Delta/v)`;
- `AUTHOR_RENORMALIZES_DELTA`: code rescales the stored quantity before exponentiation; report the exact transformation;
- `AUTHOR_BRANCH_DEPENDENT`: different branches/series use different rules;
- `AUTHOR_PATH_UNRESOLVED`: static trace cannot determine it.

Also inspect the implementation corresponding to the printed Landau-Zener/Stückelberg Eq.(43), if present, and determine whether the source code uses `DeltaE_min` or `(DeltaE_min)^2`. This is a separate finding from Eq.(52)/(55).

## Phase C: compare source, author code, and clean-room lanes

Return `NORMALIZATION_CROSSWALK.json` with columns:
- CPC printed equation
- printed meaning
- author-code expression/file/line
- input Delta provenance
- clean-room BASS_HE lane
- identity/agreement status
- unresolved interpretation.

Do not change `src/arseny_reimpl/` in this audit. Author code is evidence, not implementation material.

## Decision table

### If author code uses factor 2 on Eq.(56) Delta
Record strong evidence that CPC Eq.(52) factor-one text is inconsistent with the distributed implementation and upstream hidden-crossing theory. Request, but do not automatically perform, a bounded clean-room policy decision for an Eq.(55)-faithful standalone lane / possible Eq.(50) correction.

### If author code uses factor 1 on Eq.(56) Delta
Record that the distributed implementation follows Eq.(52) despite Eq.(55)/upstream theory. Keep the source conflict OPEN and do not rewrite the clean-room default. The next task becomes a source/erratum interpretation decision, not more numerical benchmarking.

### If author code rescales Delta
Map the transformation exactly and test algebraically whether it reconciles Eq.(52) with Eq.(55). Use Wolfram/SymPy for algebra only, not production numerics.

### If unresolved
Preserve HOLD and return the exact missing authority.

## Explicit non-scope

Do NOT:
- run Eq.(55) production calculations;
- change Eq.(50)/(54) production code or exponent defaults;
- alter physical tolerances;
- reinterpret Nmax sink as a disjoint physical ionization channel;
- run 56-action/cloud/worker replays;
- start L2/Krawczyk implementation;
- copy author code into BASS_HE clean-room source;
- merge or force-push.

## Publication / backup

Publish audit artifacts append-only under a new PR17 timestamped namespace. Source archive itself may be backed up privately/create-only if allowed, but never mix it into the clean-room source tree. Record provider acknowledgements, IDs, sizes, SHA256 and restore status separately.

Use the existing BASS_HE Drive folder and Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/` for new durable audit artifacts. Do not duplicate existing archives.

## Return contract

Return:
- fresh PR15/PR17 identities;
- dataset identity and provider manifest;
- exact author-source archive/file SHA256s;
- static call/data-flow trace;
- Eq.(52)/(55)/(56) decisive classification;
- Eq.(43) source-code classification;
- clean-room crosswalk;
- findings with severity and claim ceiling;
- backup status;
- next bounded decision prompt.

Keep until a separate decision explicitly changes them:
- `CODE_I02_CLOSED=true`
- `full_certificate_fail_closed=true`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`.
