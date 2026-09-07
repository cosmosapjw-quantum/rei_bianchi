# REI_THERMAL_T1_PHOTOHEAT_ROOT_INVERSE_BOUND

ROLE=LOCAL_CODEX
RETURN_TO=MAIN_CONVERSATION
WORK_THREAD_REQUIRED=false

## 목적

PR #80의 saved endpoint와 이번 research directory의 resolved-photoheat numerator bound를
재사용해서, **second-half thermal_t1_final에 한정한 photoheat-mediated thermal-root
inverse component**를 계산한다. 전체 source tube나 population F0/F1로 확대하지 않는다.

먼저 현재 immutable intake head의 `PROOF_AND_SCOPE.md`와 PR #80 handoff/result를 읽고,
동일 작업의 더 새 결과가 있으면 재사용한다. O01--O10, G01--G06, producer, 기존
validated map suite는 다시 돌리지 않는다.

## 고정 source와 입력

읽기 전용으로 아래 parent source를 사용한다.

- ADAPT `analysis/thermal_backends.py`: `_thermal_rhs_numpy`, `_balance_numpy`.
- ADAPT `analysis/physical_trial.py`: resolved `photo_fields()`와 actual thermal call.
- CROSS `data/VALIDATED_PUBLIC_BOXES.npz`: `LOCAL_NEUTRAL_HAZARD_PRIMARY` endpoint lower/upper.
- INITIAL `data/initial_material_state_z6.npz`: fixed node H/He totals needed to reconstruct populations from public fractions.
- 첫 microstep second-half forcing/site identity already pinned by PR #80: `t in [duration(0)/4096,duration(0)/2048]`; use the actual source-consumed midpoint/average convention for volume, Hubble and dt. Do not invent a different time.

All NPZ reads use `allow_pickle=False`. Preserve exact blob/source identities. No production package import is necessary; implement a small research consumer under the new research directory.

## 수학 계약

For each node, at fixed populations, volume, Hubble, parent energy and dt,

```text
B(l) = E(T) - U0 - dt * [Qphoto - C(T,pop) - X(T,pop)],
T = exp(l).
```

Differentiate the literal source formulas with respect to `l=log T`.
Do not approximate this derivative by finite differences as the authority path.
A finite-difference or complex-step check may be an independent diagnostic only if the source functions admit it.

Build an actual enclosure of

```text
m_T = inf partial B / partial logT
```

over the saved endpoint Cartesian set and the fixed second-half forcing values. Use genuine inclusion arithmetic: exact-binary-rational + controlled transcendental enclosures, MPFR/MPFI/arb/interval library, or another documented outward-rounded method. Ordinary float evaluation followed by one final nextafter is not sufficient.

The public box coordinates are x_HII, x_HeII, x_HeIII, log_T. Reconstruct

```text
N_HI   = h_i * (1-x_HII)
N_HII  = h_i * x_HII
N_HeI  = he_i * (1-x_HeII-x_HeIII)
N_HeII = he_i * x_HeII
N_HeIII= he_i * x_HeIII
```

without extra node weights. If the independent Cartesian helium box permits a negative neutral value, do not floor it; classify the enclosure issue. PR #80 observed no nonpositive upper-face neutral node for its selected endpoint, but re-read the exact arrays rather than inheriting that as a new calculation.

## 결과 gate

If `m_T>0`, the nodewise implicit photoheat partial is

```text
delta logT_i = dt_i * delta Q_i / (partial B_i/partial logT),
```

so, with `m_T=min_i lower(slope_i)`,

```text
||delta logT||_1 <= (dt_max/m_T) ||delta Q_res||_1.
```

Compose only with the inherited bound

```text
||delta Q_res||_1 < 1.421e42 * U_plus erg/s.
```

For temperature and energy components retain the actual endpoint upper bounds:

```text
|delta T_i| <= T_i^max |delta logT_i|,
|delta E_i| <= E_i^max |delta logT_i|
```

at fixed populations, where the thermal energy is the source literal `1.5*k_B*particles*T`.
Do not call these the total thermal derivative: population-mediated cooling/expansion and direct
population changes are separate chain-rule components.

If the slope enclosure includes zero, return `THERMAL_ROOT_INVERSE_NOT_CERTIFIED_ON_ENDPOINT_BOX`
with the worst node, slope interval, dominant derivative terms and whether the failure is physical
or dependency/wrapping-induced. No derivative floor or narrowed box may be introduced silently.

## 최소 검사

Create a small research consumer/tests before finalizing. At minimum:

1. analytic derivative versus independent high-precision point derivative on a synthetic positive fixture;
2. exact source energy derivative `dE/dlogT=E`;
3. zero-dt limit;
4. photoheat derivative of balance exactly `-dt`;
5. endpoint neutral/simplex reconstruction and no-double-weight check;
6. outward-enclosure self-check against sampled interior points (sampling is diagnostic, never proof);
7. sign/normalization mutant that must fail.

Preserve actual command, process exit, timeout, per-test outcomes and raw logs. Generate one plot of per-node slope lower bounds / decomposition if runtime permits and actually inspect it. The proof does not rely on the plot.

## 금지와 claim ceiling

No old suite replay, producer/canonical interval rerun, GitHub Actions dispatch/re-run, production import/lock, native Rust/MPFR production attempt, Section-0/ref/lease/worker, Snapshot/GCC/XZ, BASS/REC/HTT writes, first interval/provider, ready/merge/force-push.

Do not merge the other three source sites. Do not claim complete thermal inverse, total nonlinear thermochemistry Lipschitz constant, exact-flow rho, or production PASS from this one component.

Publish only REI-scoped research/evidence files on a non-force Draft child with `[skip ci]`; return a fixed Git handoff directly to the main conversation.
