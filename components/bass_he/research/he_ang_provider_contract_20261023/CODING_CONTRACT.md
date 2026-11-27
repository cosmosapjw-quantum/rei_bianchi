# HE-ANG coding contract

Authority: corrected `theory/DERIVATION.md`, `theory/PROVIDER_TEMPLATE.json`, independent theory PASS_SCOPED and saved exact witness. Workflow1.0.0 / approval0.2.

## Inputs and outputs

The selected new package is `code/heang_contract`. The numerical reference uses Python stdlib Fraction. Exact represented inputs are integers or rational strings; binary floats and booleans are rejected at that interface. This is an exact contract/testing path, not a high-throughput empirical quadrature implementation.

`Event(weight,q1,q2,qp)` describes a finite positive law at one COM E,I with additive masses m,M. `integrate_events` requires weights summing to1 and checks each momentum and energy shell. It emits electron/proton `RawMoments(mass,N,P,R,normalization,kind)` plus C12. R is pressure-type, sum qq^T/m, and P is momentum. The accumulator does not use HE38's independent uniform angular assumption.

`cross_section_weighted` multiplies a conditional bundle once by sigma, preserving Z=sigma. `zero_cross_section` returns zero cross-section moments without manufacturing a conditional probability. `transform_raw` applies q'=O(q-mU) to N/P/R, including signed reactive N. It checks an exact orthogonal O and does not repair malformed axes/matrices. RawMoments is a carrier for declared moments, not an independent PSD certificate.

`precheck_provider` validates source metadata and supplied payload bytes. It compares common source/law/preparation/angle identities, units, normalization, electron counts, actual coverage declarations, frame/incident energy/relative flux, Jacobian/root references, physical/numerical uncertainty separation and a candidate-bound X1 record. Source truth cannot be established from a nonempty reference or a metadata boolean. Every outcome keeps empirical_admission=false and runtime_activation=false.

The inherited X1 algorithm/theory pin and completed32fixture evidence are separate from a decision for new candidate moments. A candidate certificate must identify the current represented moment payload. The manufactured example uses direct event-support algebra; it does not claim that X1's old fixtures were run for that candidate.

## Required affected controls

Compare integrated A/B moments with hand-derived matrices and the independently saved R7 results. Verify same electron marginal and different ion tensor, sigma conversion and zero sigma, raw and signed frame transforms, errors in energy/momentum/weight/shape/normalization, and serialization. Mutate only the relevant metadata dependency to check mismatched source identity/hash, missing correlation, partial support, wrong flux/frame, missing uncertainty, and X1 candidate binding. Preserve every failed attempt and command output.

## Admission and cost

Mathematical/implementation controls must pass exactly for represented rational inputs. There is no new floating tolerance replacing a physical source uncertainty. Byte hashes bind source and saved deterministic evidence; numerical validity follows the exact predicates and independently justified algebra.

All new scientific child invocations use `run_bounded.py`; BUDGET.json is frozen, RESOURCE_LEDGER.json is current. Existing HE-X1/HE38/HE32 tests, IVPs, scans, benchmarks and renderers are not invoked. C9 reviews actual code and receipts; C10 packages the independently accepted scope. Numerical integration of arbitrary measured TDCS, physical calibration and source-model replacement require the next source-admission unit.
