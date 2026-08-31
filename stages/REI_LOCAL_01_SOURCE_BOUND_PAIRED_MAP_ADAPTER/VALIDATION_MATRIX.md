# Validation matrix

Recovery classification: `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL`

Status vocabulary: `PASS`, `CONCERN`, `FAIL`, `BLOCKED`, `NOT_RUN`,
`NOT_APPLICABLE`.

| Requirement | Executable check | Expected | Current status |
|---|---|---|---|
| Exact reconstruction authority | base tree and harness/toolchain SHA checks | exact identity | PASS |
| Non-code formula contract | external ZIP/markdown plus repo-relative 7-file manifest | exact identity | PASS (`FORMULA_CONTRACT_CLOSED`; 7/7) |
| Independent rational oracle | `test_noncode_formula_contract` plus Sage-source AST | tangent, midpoint counterexample, mixed/normalization/conservation identities, 2x2 16-corner Krawczyk, 2x2/3x3 margins | PASS (9/9) |
| Static formal review | formula and proof-source consistency | bounded formulas only | PARTIAL_PASS_STATIC_ONLY |
| Wolfram/Sage/Singular/Lean/Rocq runners | versioned executable replay | exact pass | NOT_RUN (executables absent from this executor PATH) |
| Lean dependency closure | pinned workspace/toolchain/lock hashes | exact identity | BLOCKED missing pins |
| 3x3 Krawczyk derivation | derive K3 and prove margin | exact | NOT_RUN (supplied margin checked only) |
| Non-code Wolfram replay | rerun supplied script and compare receipt | exact local replay | NOT_RUN |
| Non-code EVID-01/02/03 | evidence acquisition gates | source-backed | NOT_RUN |
| Universal execution policy | `test_universal_policy` | 8/8 | PASS (final reseal run) |
| Runtime input closure | `test_runtime_input_closure` plus production-lock automatic invocation | 14/14 and sealed production lock pass | PASS_BOUNDED_INVOCATION_SCOPE (automatic audit-hook observation; self-reported evidence rejected; lock `0d5e30ff...c582`) |
| Hostile fresh-process native authority | independent process capability gate | independently pinned native identity cannot be fabricated in-process | BLOCKED `RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING` |
| Prestart interpreter/ELF identity | close the already-running interpreter and loader before invocation | exact interpreter and ELF dependency graph | BLOCKED `BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED` |
| Rust ABI v4 MPFR enclosure | native Rust suite plus independent Fraction corner oracle | 11 native cases and 96 families/6144 corner systems pass | PASS |
| Python/Rust bridge | focused bridge/joint and lock-independent security suites | all bounded synthetic checks pass | PASS_BOUNDED (fresh 12 joint + 16 bridge = 28/28; native mutation uses replacement inode) |
| Certificate graph | graph/gate focused suite | all pass, production fail-closed without payload | PASS (14/14) |
| Node 38382 fixture contract | fixture suite | all structural mutations rejected | PASS (14/14; certificate + node combined 28/28; structure only) |
| Original endpoint replay | pinned predecessor replay, node predicate only | endpoint SHA matches authority | BLOCKED `NODE_38382_FIXTURE_MISSING`, `NODE_38382_FIELD_PARENT_AUTHORITY_MISSING`, and `NODE_38382_VERIFIED_REPLAY_ABI_MISSING` |
| Four-site production operator | real evaluator replay at four named sites | complete certificate graph | BLOCKED missing ABI/authority |
| Four-site/node/canonical formal proof | real production authority | exact | NOT_RUN / unproved |
| BASS custody substrate | custody/transaction mutation suite | all pass | PASS_SUBSTRATE_ONLY (33/33 after seven P1 repairs) |
| BASS worktree/common lazy config | promisor/partial-clone mutations | rejected | PASS |
| BASS same-inode publication | descriptor/swap mutation | rejected | PASS |
| Exact BASS/REC authority | URL, commit, tree, load-bearing blob graph | exact | BLOCKED missing authority |
| REIAFF1 strict format | seven-block canonical codec and mutation matrix, including base64 alias rejection | all pass | PARTIAL_PASS_FORMAT_ONLY (14/14) |
| REIAFF1 real split restart | real operator split/restart mutations | lossless and strict | BLOCKED on real four-site operator ABI |
| PHYS-MATH audit | [PHYS_MATH_AUDIT.md](PHYS_MATH_AUDIT.md) independent exact fixture derivation | bounded-fixture pass only | PASS_BOUNDED_GENERIC_FIXTURE_ONLY / BLOCKED_PRODUCTION_AND_SCIENTIFIC_CLAIM |
| PHYS-MATH-CODE audit | [PHYS_MATH_CODE_AUDIT.md](PHYS_MATH_CODE_AUDIT.md) fresh integrated review | all repairs and residual P0/P1 disclosed | PASS_WITH_RESIDUAL_HOST_BLOCKERS / STOP_INVALID |
| Repository/payload verification | `scripts/verify_repo.py`, continuation payload verifier with and without `--repo .`, `git fsck --full --no-dangling --no-progress`, JSON parse, pycompile, manifests, whitespace/diff check | pass | PASS (repository: 60 artifacts; payload: 13 files with source objects `CHECKED`; Git fsck and bounded package checks pass) |
| 46,080 x 3 canonical pilot | excluded by scope | not run | NOT_RUN (scope-excluded) |

The matrix cannot promote a scientific pass.  Until all production gates are
closed, the claim remains `NO_PASS_FIRST_CANONICAL_INTERVAL` and the adapter
remains `PARTIAL_RUST_IMPLEMENTATION_STOP_INVALID`.
