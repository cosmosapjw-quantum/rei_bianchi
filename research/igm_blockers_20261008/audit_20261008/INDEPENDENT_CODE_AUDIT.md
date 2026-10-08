# Independent read-only stock/owner audit

Audited HEAD: `ddf125732854f4365e000b013c4bb78970ac6fcd` in `/home/cosmosapjw/rei_worktrees/igm-rate-export01-20261008`. Prefix below is `research/igm_blockers_20261008/numeric/`. No repository writes, history advance, RHS call, or photon observer call. Pure probes are under `/tmp`. Parent explicitly authorized exactly three audit provider calls and one isolated analytic kernel evaluation to identify the first failed cell; actual counts were RHS=0, sigma=3, coupled advances=0, observers=0, history writes=0. Compile wall total ~0.62 s, CPU total ~0.66 s; probe runtime below displayed 0.01 s. All executed probes exited 0.

## Central correction: observed failure is HI heating, not transported stock

**High/current blocker, confirmed bit for bit.** `source/rei-next-nodes/short-hhe-midpoint/src/radiation.rs:184–189` calls `nonnegative(o.be[i] - EPS*CHI[i]*o.an[i])`. `lib.rs:14–25` rejects every nonzero subnormal, including a positive physical heating increment. The original `FAILURE_12.json` correctly records the generic error `unsupported nonnormal 3.812277937532397e-309`; the later README/RESULTS/TASK_RETURN diagnosis incorrectly calls that value transported stock and attributes it to radiation.rs:121.

Direct read-only decoding of all three current HEADs yields no subnormal density node at all:

- coarse k11/tail k11 smallest N = `2.50921566666785190e-296` (normal), node 0;
- fine k22 smallest N = `2.509215491420924e-296` (normal);
- coarse/tail N total ~`1.5428951364060414e-4`, active E ~`1.535986352672504e-14`.

Independent first-cell probe uses coarse k11, node0, first Newton trial y=old.y, unchanged background and provider:

- eta `0.05244705397124411`, a `-2.56445769079487`, b `-2.5644493574615366`, h `8.333333333609971e-6`;
- initial photon energy `13.6932737451958` eV, q=0, rates `[1357929.4363808532,0,0]`;
- returned N `3.05511443136939113e-301` (normal), returned U `6.70257290553098821e-312` (subnormal), red `4.05389843775204402e-313`;
- A_HI `2.5091851155235384e-296`, B_HI `5.5049080207218545e-307`;
- threshold energy `5.4667852413465305e-307`;
- **HI heating `3.81227793753239748e-309`, bits `0002bdc74d339a20`, exactly equal to observed failure**;
- canonical owner's preheat check returns `Ok(())`.

Both operands of the final heating subtraction are normal, and Fraction arithmetic confirms their binary64 subtraction is exact. The quantity is positive and finite. This is a numerical-domain false refusal, not a negative heat, invalid ionization state, provider failure, or measured physical-budget violation. The failure counters (4 RHS,3 sigma,1 residual evaluation) independently corroborate passage through entry stock validation and first opacity evaluation before the heat check.

Minimal current repair: give this **signed heating classifier** its actual finite/nonnegative domain, or perform the difference in a signed scaled/error-aware representation. Preserve A/B, their covariance/loss, and original physical thresholds/tolerances. Add the captured exact cell as a regression. Do not globally weaken every `checked/nonnegative/product` guard. Do not relabel a general transported-state rewrite as the necessary fix for this observed failure. Correct the diagnosis documents before using them as implementation requirements.

Artifacts: `/tmp/igm-stock-checkpoint-read.json`, `/tmp/igm-first-cell-probe.rs`, `/tmp/igm-first-cell-probe.txt`.

## Per-node representation remains a real future blocker

**High/future execution blocker, not the observed current one.** `diagnostics.rs:115` stores only `Density(Vec<f64>)`; `radiation.rs:140–141,191–195,210–218,262–275` hand off scalar N and U, reset stock ledger components, and store only N in the next density. `canonical_owner.rs:108–137` still forms decay, transported N/U, source and absorption owners in ordinary binary64. `radiation.rs:121` will indeed reject a future subnormal incoming N; kernel U can reach zero while N remains positive and `try_add_scaled` then fails its paired check at canonical_owner.rs:550. After N itself rounds to zero, kernel logs mark a positive tail but `try_add_scaled` refuses `authoritative tail is not empty` at line551.

Minimal falsifier without any provider: n=`1024*2^-1074` (>0), E=13.7 eV, exact EPS*E*n>0, while binary64 U=0. Thus accepting a finite subnormal at one check alone cannot satisfy the original requirement to retain all positive N/E through a long horizon.

A correct eventual lane carries one coherent per-node scaled amplitude/paired energy relation and uncertainty through kernel input/output, intersegment handoff, old/trial/accepted states, observer and checkpoint. For fixed stage rates/source the cell solution is linear in incoming/source amplitude, so power-of-two normalization is viable; normalize *before* products/exp would erase them. A finite loss/truncation alternative would need explicit user/scientific contract permission and a bound propagated into observables; existing instruction prohibits silently dropping positive tails.

`radiation.rs:168–170,212` and `diagnostics.rs:93–107` use scalar relative energy continuity. At sufficiently tiny U, a single subnormal ULP exceeds relative 2e-12; use a paired canonical continuity comparison plus charged boundary error instead of a global relative tolerance increase.

## Loss accounting scope does not cover raw kernel/readout error

**High/continuum and complete representation-bound blocker; actual finite falsifier.** `canonical_owner.rs:541–542` wraps every raw binary64 kernel owner with `Tracked::from_f64` (zero initial error). `kernel` at lines110–137 performed its multiplications, exp, phi/psi and N/E projection before this. The wrapper at lines554–558 charges *subsequent* scale/sum rounding. This cannot enclose the upstream error.

Captured actual first-cell U falsifier, using only Fraction arithmetic and the frozen numeric operands:

- rounded normal factor EPS*end_e = `2.1938860412919833e-11`;
- N = `3.05511443136939113e-301`;
- product float U = `6.70257290553098821e-312`;
- exact rational product differs from U by `1.3851956928792620920e-326`;
- first canonical times-one wrapper U bound is `2^-1085 = 2.4124299113342116415e-327`;
- omitted error is **5.74191062037 times** that postkernel bound.

This is sufficient to falsify interpreting `owner_bounds` as the complete representation bound. The current `record::AUTHORITY` (record.rs:7) explicitly says kernel/provider/state error unresolved, so the defect is a coverage gap for the long-run authority, not grounds for retroactively calling the existing postkernel-only ledger dishonest. Missing old precheckpoint arithmetic is separately marked NOT_MEASURED and must stay so.

`coupled.rs:102–105,174–178` propagates only these owner-bound components. It does not include raw kernel arithmetic, incoming density error, signed residual assembly (`assemble_residual` lines126–130), material accumulation, or state error. `material.rs:62–96` remains ordinary binary64. Those omissions do not prove physical budgets presently fail; they prevent a continuum certificate or a statement that all canonical representation loss has been covered.

## Observer bound is conditional on already-rounded density

**Medium/complete observer/continuum-bound blocker.** `radiation.rs:299–305` correctly uses extended-range accumulation and charges product/sum/readout rounding *after* density input, but passes every density f to `Tracked::from_f64` as exact through `scale(f)`. There is no argument for per-node uncertainty and no same-spectrum incident-energy partner in this observer. `LAST_GAMMA_BOUND` therefore bounds arithmetic of the supplied scalar finite grid only; it cannot include upstream transport, spectral reconstruction, exp-energy, or provider error. Keep that claim ceiling explicit. Future canonical density must feed its uncertainty to the same observer inputs rather than being converted back to unlabelled f64 first.

The positive summation wrapper's extra `2^(exp-51)` charges are conservative for its own ordinary add/mul; no underbound found at that local boundary. Bare `Tracked::mul` itself does not charge partial mantissa rounding by design (`canonical/src/primitives.rs:231–238`): 0.1*0.3 has a nonzero exact rational error `1.6653345369377347e-18` with empty loss. New uses of bare Tracked arithmetic must honor that contract.

## Dormant accepted-record replay regression

**Medium/API regression; not blocking the current record-disabled driver.** `record.rs:62–70` builds canonical sums, then directly assigns sum.n/u/outN/outE or clears total.n/u without synchronizing their ledger. `try_add_scaled` calls owner_ledger and rejects `canonical owner/readout mismatch`. Minimal pure probe creates a sum with canonical red=1, directly assigns n=1,u=2 as replay does, and the next sum operation rejects exactly that mismatch. The current driver sets `record::set_enabled(false)` at main.rs:51, so existing history execution does not exercise it.

Repair replay's stock replacements with a typed assignment/move that preserves proper active N/E authority and updates the corresponding canonical components. Test actual saved accepted records in this new research implementation; do not modify preserved PR86/88 copies. `replace_owner_components` at canonical_owner.rs:545 resets term error/occurrence/coefficient to zero; it is valid for intentional removal/move-to-another-owner but must not become a generic error-dropping synchronization shortcut.

## Codec observation (bounded, not a current-driver defect)

Public `record::write_state/read_state` at lines82–92 drops canonical ledger and resets active_loss to zero. Current new driver intentionally appends/restores that state at main.rs:46–49, so its actual roundtrip preserves cumulative/active ledgers. Do not use `record::state_bytes` alone as proof of complete state equality: driver failure atomicity check at main.rs:51 only compares that legacy image. Current advance takes immutable old State, reducing present mutation risk; any future per-node canonical extension needs a complete equality/codec path.

## Suggested stopping order

1. Correct current blocker diagnosis and fix/test the local finite positive heating refusal with the exact frozen cell; no full campaign is needed.
2. Preflight every nonnormal assumption in transport, pair projection, heat and continuity together before attempting a longer suffix, instead of chasing one generic `unsupported nonnormal` at a time.
3. Implement one per-node scaled transport/error path including restart/observer; check normal regression and actual subnormal pair cases.
4. Keep finite-grid arithmetic, empirical refinement and continuum error authority distinct. Kernel/source/time/spectral/historical bounds are necessary for the latter, not prerequisites for every bounded exploratory step.
