# Finite thermal endpoint: C5 implementation

**AUTHORED_NOT_EXECUTION_VERIFIED.** The owner explicitly authorized controller-direct C5 implementation on 2026-10-28 and retained separate permission for test execution and scientific admission. This directory supplies source, authored controls and a one-attempt runner. No module import, syntax/AST/compile check, test, CAS, source evaluation or numerical campaign was performed as part of C5. No red/green TDD execution is claimed. The controller is the actual author; native subagents and distinct-author review are NOT_RUN.

## Authority and progress

Integration base: `9ced7d82bc7bdfd7bc3a574618a5486bf1a6bbec` on `research/rei-causal-prefix-consumer-20261027`, PR240. This preserves the newer literal-binding addition after `e77bc7ec48ae2aee8ded573e66ac0a1060017c54`.

Read the unchanged parent files `CONTRACT.json`, `theory/R5_FINITE_CALORIC_DERIVATION_20261028.md`, `review/R6_SOURCE_BATH_RECONCILIATION_20261028.md`, `inputs/SOURCE_BATH_LITERAL_BINDING_20261028.json` and `implementation/C1_C4_DESIGN_20261028.md`. The scope is exactly the existing finite ideal-caloric construction. C5 authoring moves the workflow from 9/20 to 10/20: theory 5/10, coding preparation C1-C5 5/10. C6-C9 and distinct-author R6 remain pending; C10 is not a completed scientific release. Original working33/88, central last-observed28/88,88IDs/17edges, delta0 are unchanged. Old atomic-storage20/20 is separate.

## Equations and code

N counts thermal particles per common reference volume V0. U, Q and W are J per V0. cv is per-particle J/K; the monatomic source bridge uses cv=3*k_B_SI/2, retaining k_B_SI=1.380649e-23 J/K. All scalar algebra uses Fraction. The strict core accepts Fraction or explicit decimal/rational strings, not float, bool or int.

| Function | Equation / obligation |
|---|---|
| `finite_endpoint` | N=Na+dN; U=cv*Na*Ta+Q+W; T=U/(cv*N), on Na,Ta,cv,N,U>0 |
| `saved_endpoint_diagnostics` | r0=Ua-cv*Na*Ta; r_balance=Ub-Ua-Q-W; rE=r0+r_balance; rN=Nb-N. Preserve independent Ua, require Ub,Nb>0; return both direct temperature difference and residual identity |
| `endpoint_jvp` | Full dNa,dTa,dcv,ddN,dQ,dW chain rule, including exact dlogT |
| `proper_coordinates`, `normalized_coordinates` and their JVPs | Divide both coordinates by the same R and optionally actual supplied b; retain their separate derivative terms |
| `temperature_interval`, `temperature_error_bound`, `endpoint_interval` | Positive Cartesian algebraic enclosure and supplied-radius discrepancy bound. None remains unknown; no physical certification |
| `compose_local_segments` and its JVP | Unweighted increments only: x02=x01+R01*x12, R02=R01*R12, including dR01*x12 |
| `selected_h_thermal_count`, `selected_h_event_count` | Saved H stocks plus separately saved electrons; event sum(dFine)+dContinuum retains defects |
| `source_bath_counts` and its JVP | Add inert source He B=NH*fHe to both endpoints; dB=fHe*dNH+NH*dfHe in parameter directions |
| `gas_ports` | Select only index2 of the exact five-sector event and geometry-work orders. Never add atomic or photon energy to heat |
| `decode_source_literal`, `load_literal_binding` | Explicitly distinguish original JSON binary64, binary64 hex, and saved MP-decimal-string representation |
| `source_temperature_bridge` | theta_eV*EV_source/k_B_SI; retain native-K and source-constant mismatch diagnostics |
| `consume_saved_source` | Complete byte-pinned original-result + literal-packet -> source-model caloric diagnostics; no provider imports and no physical client mutation |
| `to_wire` | Fractions serialize as decimal integer strings `{num,den}`; no floating conversion |

The ratio T/Ta and the two positive logarithm arguments are exact rational outputs. Generic logarithms are not evaluated. `dlogT` is exact rational. General EOS inversion, polytope optimization, weighted fractional-power evaluation, new thermal feedback and ODE integration are not implemented.

The weighted J2 coordinate is not a Q input. Its V1-local composition factor R01^(5/3), proved in the source addendum, must not be passed to the unweighted segment interface. Generic fractional powers are not exact Fraction operations. No implicit weighted-to-unweighted conversion exists here.

## Source path and limitations

The fixed BASS transaction is commit `634c3046ffccc5d00f1ab7588b5834a6eb8053ad`,3554206bytes,SHA256 `a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac`,Git blob `a9ea559f123da6c8f1fe070139bc80145d4582fc`. The separate11-field literal packet is8281bytes,SHA256 `b77aba9612584ffd74e2cdd951c0b9e2b573113bd7195c04d8cc857354cfe34f`,Git blob `ea4bd58d394a421533407b5d12acf2468b32fdcd`.

The original NH comes from the preserved tube reference, not another endpoint density multiplied by10^6. The adapter reports that difference rather than replacing NH. Full input bytes are required for the actual-source function; the literal packet alone is not enough. Calling the function is a new evaluation and needs separate permission. No original input archive was restored or repackaged in C5.

Saved MP output strings are represented as decimals. Bare input decimals are reconstructed through the original Python binary64 semantics, with exact dyadic extraction after that conversion. The result is exact for these declared representations, not the unprinted finite-precision MP arithmetic. Numerical input uncertainty and physical source uncertainty remain distinct.

Prescribed rate-driver temperature, the finite source-caloric diagnostic and the actual coupled REI recipient temperature are different outputs. Even when the source adapter can evaluate the diagnostic, `actual_temperature_update`, `actual_native25`, `actual_recipient_nb` and physical radii remain None. `full_state_update` and `L4_ready` stay false; global physical completion stays None. A tiny computed residual never becomes a physical radius.

CR parent-event species/ionic-charge corrections are not thermal-electron increments. No CR/HE/REC/WU/VigilODE source or budget is silently substituted for this frozen BASS transaction.

## Authored controls, not test results

`test_finite_thermal.py` contains27 authored methods:18 mathematical/representation controls,3 pure execution-authorization controls and6 pure outcome-classification controls. They cover the14 C1 acceptance categories, full mixed JVP, inert-He parameter sensitivity, retained count/EOS defects, exact source-decoder contrasts, input rejection, gas ownership and null physical outputs. Independent expected rational values or cross-multiplied identities are used. The authorization fixtures are synthetic dictionaries, not usable execution grants.

These are fixtures, not a reproduction of the actual3554206-byte source transaction. No test outcome, full-source integration success, code syntax success, runtime overhead, convergence or speed measurement is asserted. The first authorized C6 may reveal an implementation defect; preserve that outcome and allow only a specifically approved repair/recheck.

## Future one-attempt execution

`run_once.py` uses POSIX fork/wait4, child address-space and CPU limits, parent CPU/wall stops, a create-only output directory and one-use marker next to the authorization JSON. It does not import the scientific module in the supervisor. Child terminal CPU includes interpreter startup, imports and output serialization. The supervisor records its own pre-final-serialization CPU separately. A final-record reserve and external whole-command accounting are still required; no zero-overshoot or exact whole-turn-cost guarantee is made.

After a separate explicit test authorization, the fixed worker command is:

```text
<exact Python executable> -B -S -m unittest discover -s <absolute implementation directory> -p test_finite_thermal.py -v
```

The outer command, ALSO NOT AUTHORIZED by this README, is:

```sh
/usr/bin/time -v -o <new-external-accounting-file> \
  <exact-python> -B -S run_once.py \
  --authorization <approved-auth.json> --mode tests \
  --output-dir <new-attempt-output-directory>
```

Use an actual owner-approved record with the following shape. This illustration is deliberately unapproved; fill identity and resource fields only from the separate authorization. `worker_command` must be the exact resolved argv above. Source hashes include the runner itself. An approved tests mode does not allow the source mode.

```json
{
  "schema": "REI_FINITE_THERMAL_RUN_AUTH_V1",
  "unit": "finite_thermal_endpoint_20261028",
  "approved": false,
  "authority_ref": "UNSET",
  "attempt_id": "UNSET",
  "mode": "tests",
  "attempts": 1,
  "source_sha256": {
    "finite_thermal.py": "UNSET",
    "test_finite_thermal.py": "UNSET",
    "run_once.py": "UNSET"
  },
  "worker_command": [],
  "prior_known_planning_cpu_s": "15.929490885",
  "approved_absolute_planning_cap_cpu_s": null,
  "unknown_costs": "UNKNOWN_NOT_ZERO",
  "accounting_boundary": "UNSET: retain historical debit and explicitly address unmeasured costs",
  "limits": {
    "attempt_cpu_s": null,
    "worker_cpu_s": null,
    "final_record_reserve_cpu_s": null,
    "wall_s": null,
    "memory_bytes": null
  }
}
```

The historical lower record shown in the template is NOT a current exact total. Account for later documented costs and unknowns without resets or transfers. The earlier proposed research cap20/reserve3 remains unapproved, as does the separate ZIP cap60/reserve8. Main595.225063/600 NO_MORE_IVPs and presentation historical lower48.263016494/cap47 remain untouched.

A separately approved actual-source attempt uses `--mode source --source <original FINITE_CHANNEL_RESULT.json> --literals <original literal packet>`. Its exact argv includes the fixed `SOURCE_JOB` string from this runner and the resolved input paths, so it requires its own command authorization. There is no download, source regeneration or automatic retry. If the authorization marker or output directory already exists, stop and inspect rather than delete it and rerun.

`RESULT.json` distinguishes exit-zero observation from scientific admission. Reconcile external OS user+system CPU with the separately recorded terminal child CPU, without double adding that child to an already-inclusive outer total. Missing terminal logs after a hard process kill remain a failure of observation, not success. Authoritative physical admission still needs the outstanding independent review and recipient binding.

## Reproduction and preservation

Python3.10+ standard library APIs are used; no dependency installation is needed by design. This compatibility statement has not been runtime-tested. Module imports, py_compile, AST parsing, unittest and source evaluation were intentionally not used to validate C5.

Publication is additive under the four R1-owned implementation paths. Old provider code, R1/R5/design files, original DAG and existing backups stay untouched. The new C5 raw UTF-8 JSON capsule contains exactly these four files with sizes, SHA256 and Git blob IDs. It is not a ZIP, whole repository snapshot, or regenerated116-file source bundle. A later Git-only handoff records actual provider ACKs without rebuilding the capsule to include its own receipts.

Official API references checked for representation and process accounting:
https://docs.python.org/3/library/fractions.html
https://docs.python.org/3/library/json.html
https://docs.python.org/3/library/resource.html
https://docs.python.org/3/library/os.html#os.wait4
These document library semantics, not the correctness or physical validity of this code.

## C5 static correction: failure evidence, 2026-10-28

The published original runner at `fc265415b8011863f2cc3e4af851bb27ce8db4c7` conflated
a captured supervisor exception or missing child usage with a resource overrun.
For example, a pre-child `fork()` OSError sets `stop_reason`, leaves `usage=None`,
and unconditionally reaches RESOURCE_STOP_OR_OVERRUN, without a measured limit
violation. This is a source-level control-flow finding, not an observed run.

`classify_outcome` now separates explicit resource stops or observed overruns,
supervisor execution errors, operator interruption, incomplete terminal
observation, worker timer-related signals, and other exits. A negative exit code
retains the terminating signal. SIGKILL alone does not identify its cause. Even
SIGALRM/SIGPROF/SIGXCPU are reported as signal evidence without asserting an
observed timer sender. Ordinary nonzero exits do not prove a physical refutation.

The resulting record preserves the raw wait status, exception type, signal and
per-limit observations. Missing child accounting remains null, not a measured
zero or evidence of a cap violation. This is a diagnostic-classification repair;
the mathematical module, numerical acceptance, execution command, limits,
one-attempt rule and physical-null boundary are unchanged. Six regression
controls are authored but NOT_RUN. Total authored methods are27; executed0.
No new test, source-run, or packaging authorization is supplied by this change.
The source/test/runner hashes in any future authorization must bind this revised
source, not the historical C5 hashes.
