# REI-L1 selected elemental-HI adapter: independent theory/static review

## Verdict

**Theory and static preparedness: PASS_SCOPED.** The selected no-deposition scalar source, its supplied-moment handling, six energy owners, particle ledger, fixed-moment JVP, and proposed future execution wrapper are internally consistent with the frozen implementation contract. **No actual in-scope finding requires a source or fixture correction.** No correction was requested or applied by this reviewer.

**Numerical validation: NOT_RUN. Full L1 scientific/source admission: NOT_ADMITTED.** The source, fixture, and runner are prepared files. This review does not turn their intended checks into observed numerical results or authorize their execution. The proposed one-child CPU 1 s / wall 5 s allocation remains **NOT_AUTHORIZED**; no unused L0 SRC-01 allowance is transferred.

Reviewer: **`/root/source_review`**, the separately invoked native independent reviewer of L0 and SRC-01, reused for this compatible L1 theory/static task. I did not implement these files and did not import, compile, or execute the candidate, fixture, or runner. I read the theory, contract, source card, source, fixture, README, binding manifest, and final proposed runner/contract. I also performed read-only byte comparison and hashing. The only files written by this reviewer are this review and its JSON companion. There was no CAS, rendering, Git, or cloud mutation.

## Reviewed identities and scope

For citations below:

- `T/` is `/workspace/scratch/03a65a604d4c/rei_l0_uv_repair_20261024/l1_theory/`.
- `M/` is `/workspace/scratch/03a65a604d4c/rei_l0_uv_repair_20261024/work/research/rei_source_pair_binding/hi_primary_20261024/`.

The selection is elemental ground-state HI at z=2.479, threshold 13.6 eV and photon support [13.6, 50000] eV, bath-frame rest target, zero-recoil approximation, an explicit isotropic scalar closure, and no deposition. It is an instantaneous prescribed-source snapshot. It does not identify an isotope, evolve a finite radiation stock, introduce RR/feed/secondary reactions, or supply a nonthermal equation of state (`T/THEORY_L1_KO.md:11–21,187–206`; `T/IMPLEMENTATION_CONTRACT.json:12–47`).

The supplied source is pinned to the C23B selected row read at commit `b8882d026887f375acf90768d4e3740eb03da226`, CASES blob `61bcbc0b44206f496534da6bdffcdfe1731ad063`; the original science commit is `54477b285e0c712610453bca1408a076af43521d`. These are supplied provenance pins, not a claim that this reviewer revalidated the remote provider. The L0 science commit `566f242b843fe4428cedbb8f2ea319ad706ac605` is the preceding scoped admission recorded in the implementation contract.

I independently confirmed that `M/source_card.json` is byte-identical to the locally saved selected row at `survey/github/L1_SELECTED_SAVED_ROW.json`. I checked the following byte hashes:

| File | SHA256 |
|---|---|
| `T/THEORY_L1_KO.md` | `577b4628ed040d0f4b9b6ebb393584a482aceaeea1ee9e9851f378c4cc7a5d8b` |
| `T/IMPLEMENTATION_CONTRACT.json` | `6c8b7c0b9c8c01731f3db773656e4e0f49beef200ef4b8f238e51a7c29e59f9f` |
| `M/source_pair.py` | `ee5fb4d009945da7d4f3233f5624870095090404d015524c3abe0de3955653f4` |
| `M/focused_check.py` | `8222a8f66bea1ecf6da1df1344a638a89c4654ae7d61e494165096ee23b5addb` |
| `M/source_card.json` | `1b4077f58752b2112ebdac1661d19c7942612adcf65fa5e98a41bb9bdb3707dd` |
| `M/README_KO.md` | `eb4e9e4212c81100d950bfb62587f21289d0cd2692e8903f32fa6d5d2ed09113` |
| `M/SOURCE_BINDING.json` | `4cee8d78a8b26dbdc092d8026b62fdbe40697f50ebddbd2895a78cea42c37428` |
| `M/run_focused_once.py` | `dd95849ac3bdbef4ac498bbaef643e006a0ba15119757f3f6dc3e18629124242` |
| `M/PROPOSED_EXECUTION.json` | `7b578cfe872e12dad4edcdd6ba51a0809896db0cd572f7d422bd2896804aa1a0` |

The worker's requested model/effort is `gpt-6.1-sol` / `high`; independently observed backend/effort remains `unknown` (`M/SOURCE_BINDING.json:64–69`). This review does not claim a different observed model identity or an executed external-review service.

## 1. Theory: source measure and units

The dimensional derivation is consistent. With `S(E)=4*pi*nu*J_nu` in erg s^-1 cm^-2 and photon energy coordinate E in eV, the target event measure is

\[
d\mu=\frac{\sigma(E)S(E)}{c_{\rm erg}E}\,d\ln E
     =\frac{\sigma(E)S(E)}{c_{\rm erg}E^2}\,dE.
\]

Here sigma in cm^2 cancels the flux area, `c_erg*E` is photon energy in erg, and the result is an event rate per target per proper second. The `4*pi` factor is already included in S; none is added again. The zero-recoil coordinate change kappa=E-chi has unit Jacobian, yielding the stated primary-electron spectrum. These are direct algebraic/dimensional checks of `T/THEORY_L1_KO.md:27–76`, not a new integration or provider validation.

The four supplied quantities have distinct roles: A is event count rate; B, P, and K are binding, absorbed-photon, and direct primary-kinetic powers per target. For an exact common event measure, `B=chi*A` and `B+K=P`. Independently rounded saved summaries need not obey these identities exactly. The theory correctly keeps that representation issue separate from physical stopping and from the adapter's own final rounding (`T/THEORY_L1_KO.md:67–95,208–251`).

The per-Href multiplier is `m=x_hi*amplitude`, where `x_hi=n_HI/n_ref`. Applying it once yields proper-time energy rates in eV/(Href s) and particle rates in events/(Href s). No additional number-density, area, 4*pi, or Hubble-clock factor appears in the adapter. The source is not an implementation of SI stress conversion or cosmological time evolution (`T/THEORY_L1_KO.md:97–118`; `M/source_pair.py:181–190`).

## 2. Source preservation and represented-input residuals

The loader verifies the source-card byte hash and uses ordinary `json.load`, so the saved decimal spellings become the intended binary64 inputs rather than newly asserted exact decimal physics (`M/source_pair.py:101–129`). It maps A/B/P/K directly from their four separate donor fields at lines 118–119. The unchanged source card retains all unused donor diagnostics as well (`M/source_card.json:9–78`).

`SourceCard` validates finite/nonnegative moments, pinned z/channel/threshold/support, bath-rest frame, proper-time target normalization, isotope semantics, and the declared zero-recoil approximation. Unsupported selection is rejected by the loader; no interpolation or alternate source path is supplied (`M/source_pair.py:77–112`).

The required diagnostics are correctly formed from exact representations of the actual inputs:

\[
r_B=B-\chi A,\quad r_E=B+K-P,
\]

\[
g_B=|B|+|\chi A|,\quad g_E=|B|+|K|+|P|.
\]

They are returned as Fractions (`M/source_pair.py:132–145`). B is not overwritten by chi*A, P is not overwritten by B+K, and K is not reconstructed as a difference. The donor's separately saved signed floating residual remains its own field, without relabeling it as r_E. The actual binary64 r_B/r_E values have not been evaluated in this preparation or review.

The three unavailable quantities remain None: physical secondary heat, global error bound, and the atomic event rate above the admitted support. The dataclass requires those None values; the loader preserves the corresponding donor fields (`M/source_pair.py:89–92,123–127`; `M/source_card.json:41–42,73–77`). A finite support declaration is not used to claim that the physical radiation or event source outside it is zero.

## 3. Six energy owners and particle ownership

For the selected no-deposition model,

\[
q=m(0,B,-P,0,0,K).
\]

The implementation follows that equation directly (`M/source_pair.py:167–178`).

| Index | Energy owner | Implemented coefficient |
|---|---|---|
| 0 | gas_thermal | 0 |
| 1 | binding | supplied B |
| 2 | uv_radiation | negative supplied P |
| 3 | dynamic_escape_radiation | 0 |
| 4 | source_reservoir | 0 |
| 5 | primary_nonthermal | supplied K |

The exact expected energy sum is `m*r_E`, not an imposed zero (`M/source_pair.py:174–178`). A source-summary residual is therefore visible and is not silently assigned to gas or another physical owner. The output stores no hidden feed or deposition transfer. The thermal zero is the explicit no-deposition rule; physical secondary heat remains unknown/None in both the card and returned rates (`M/source_pair.py:159,172`; `T/THEORY_L1_KO.md:148–198`).

The corresponding particle source is

\[
m(-A,+A,+A,0,-A)
\]

in order HI, HII, e_nt, e_th, absorbed_photon. A single rounded reaction rate is reused with exact sign changes in the particle tuple, preserving nuclear count, charge, and one absorbed photon per selected PI event (`M/source_pair.py:20,171–173`). `e_all_rate` is a derived `e_nt+e_th` quantity, not an additional independent pool to count again (`M/source_pair.py:161–164`). The new electron is not placed in the thermal particle count or heat capacity.

The named flux0/STF0 fields and closure label describe a chosen isotropic scalar model. They do not supply a calibrated pressure trace, momentum recoil, or general four-force (`M/source_pair.py:155–159`; `T/THEORY_L1_KO.md:305–316`). The theory's optional algebraic L0 projection and explicitly assumed instant-deposition discussion are not activated in this source implementation.

## 4. Fixed-moment JVP and rounding

At fixed supplied moments, the differential multiplier is

\[
\delta m=a\,\delta X+X\,\delta a.
\]

The source JVP and particle JVP are the same coefficient vectors multiplied by this full differential. `source_jvp_fixed_moments` forms both products and their sum as Fractions before passing the result to `_rates` (`M/source_pair.py:193–206`). It does not first round dm to a float. The expected derivative energy sum is consequently `dm*r_E`, just as required by the theory; independently rounded source consistency is not replaced with an assumed conservative derivative column.

The source normalization is likewise exact before coefficient multiplication (`M/source_pair.py:187–190`). `_rates` multiplies the exact multiplier by each exact represented coefficient and calls `_finish` once per final float-containing active component (`M/source_pair.py:167–178`). `_finish` preserves all-exact results, converts a float-containing final result once, and rejects final nonfinite/overflow results (`M/source_pair.py:44–53`). It does not repair already rounded provider inputs. Ordinary final underflow rounding remains possible; no universal range guarantee is asserted by this static review.

The base x_hi and amplitude must be finite/nonnegative. Tangents may be signed finite, and the code documents their domain interpretation at physical boundaries. It introduces no division by a rate or abundance, so zero X or amplitude does not create a relative-derivative singularity. It offers no z, chi, support, angular, source-shape, or stopping derivatives. These are exactly the fixed-source sensitivity semantics in the implementation contract (`T/IMPLEMENTATION_CONTRACT.json:40–47`).

## 5. Unexecuted fixture adequacy

`M/focused_check.py` is prepared, not run. Its references are expressed using the separately loaded saved coefficients and exact Fraction arithmetic; it never reconstructs K from P or calls a candidate internal arithmetic helper to define the expected source (`M/focused_check.py:15–47,54–72`). For the selected JSON-loaded card, active coefficients are floats, so its expected one-final-rounding vector matches the declared output representation.

The planned checks cover the finite task:

- Preservation of all A/B/P/K values, donor residual, and the three null fields.
- Exact represented r_B/r_E and gross scales.
- Six energy components, five particle components, nuclear/charge/photon identities, derived e_all, and the thermal/nonthermal distinction.
- A source at mixed rational/float normalization and a fixed-moment JVP with both normalization derivatives.
- A cancellation direction with `X=1`, `a=1.0`, `dX=1+2^-54`, `da=-1.0`, whose exact dm is `2^-54` and would be erased by premature conversion.
- Refusal of one unsupported redshift.

References: `M/focused_check.py:20–47,59–92`. The expected exact sum and the sum of the individually rounded output components are distinguished; their difference is returned as a separate component-rounding diagnostic. The fixture does not require all energy sums to be machine zero or invent a ledger tolerance. Its proposed output explicitly marks tolerance-based source qualification as not evaluated (`M/focused_check.py:93–107`).

This is an adequate prepared focused check for the current adapter contract. It is neither an executed result nor a full source-provider or cosmological validation. No additional old L0 suite, donor quadrature, raw-atom integration, or adjacent-helper audit is required by this static finding-free review.

## 6. Proposed one-child runner: prepared, not authorized

The final finite review boundary includes only `M/run_focused_once.py` and `M/PROPOSED_EXECUTION.json`, added after the original five prepared files. The proposal's status is explicitly `NOT_AUTHORIZED` (`M/PROPOSED_EXECUTION.json:2–4`). The wrapper's documentation correctly states that the attempt marker is for reproducibility, not an approval token or security mechanism; root's separate execution authorization is required (`M/run_focused_once.py:1–6`). This review issues none.

By inspection, the wrapper:

- Verifies hashes of the source, focused fixture, and source card before launching science (`M/run_focused_once.py:29–35`).
- Creates one exclusive `raw/attempt.json` before attempting one direct Python `-B focused_check.py` child, with no retry loop (`M/run_focused_once.py:36–55`).
- Sets CPU soft/hard limits to 1 s and deducts process-launch elapsed time from the 5 s wall timeout (`M/run_focused_once.py:21–26,45–58`).
- Kills/reaps the child on timeout or launch-path exception, then retains raw stdout/stderr and a receipt containing user/system CPU deltas, total child CPU, wall time, exit/timeout/error state, file identities, and no automatic retry (`M/run_focused_once.py:59–99`).
- Leaves scientific admission to root rather than claiming it from an exit code (`M/run_focused_once.py:95`).

The parent wrapper does not import the candidate or fixture. Its resource accounting uses `RUSAGE_CHILDREN` for the single child and distinguishes parent IO/review costs as separately unmeasured, not zero. Once a future execution is authorized, actual measured CPU and wall values must be assessed against the new limits; a configured limit or zero exit code alone is not an observed resource PASS. There is no such receipt or PASS in this preparation.

The proposed contract has one maximum child, zero automatic retries, and no transfer from SRC-01 (`M/PROPOSED_EXECUTION.json:22–42`). No modification to this prepared wrapper is required by the requested static review.

## Final state and next allowed boundary

| Item | Review state |
|---|---|
| Selected theory and dimensions | PASS_SCOPED by inspection |
| Summary-preserving adapter and analytic JVP | PASS_SCOPED static preparedness |
| Future focused fixture | Prepared and statically adequate; NOT_RUN |
| One-child runner/proposal | Prepared and statically consistent; NOT_AUTHORIZED and NOT_RUN |
| Actual in-scope findings / correction requests | None / zero |
| L1 numerical values and resource results | Not produced |
| Full L1 scientific/source admission | NOT_ADMITTED |
| L0 budget transfer | None |
| Whole-model completion | Not established; null |

The next concrete action is root's separately bound execution decision for the already prepared, hash-pinned one-child proposal. Static readiness does not authorize that step. No empirical heat source, stopping law, source-spectrum evolution, full radiation inventory, or cosmological-history completion is inferred from the present files. This review stops at the requested finite boundary.
