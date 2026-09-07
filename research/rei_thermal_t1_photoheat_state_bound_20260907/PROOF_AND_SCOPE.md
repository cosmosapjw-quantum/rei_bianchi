# REI thermal_t1_final resolved-photoheating state-partial bound

STATUS: DERIVED_SOURCE_BOUND_RESOLVED_PHOTOHEAT_PARTIAL__THERMAL_INVERSE_OPEN
Date: 2026-09-07
Task: REI_THERMAL_T1_RESOLVED_PHOTOHEAT_STATE_BOUND

## 1. Parent and reused evidence

Parent is Draft PR #80 final publication `43a68343e1dc872e60e61f19279bd394e83a0373`, tree `d68a5dab45cc6e2fad934f9f618d7846ca9976f9`.
No O01--O10, G01--G06, owner producer, endpoint producer, canonical interval, native runtime, or old suite is rerun here.

Reused bounded results:

- G2a first-cell resolved-owner state partial: `L_G2a < 5.7e52` box photons/s per unit global-He-normalized share l1.
- G2b saved-endpoint resolved-owner state partial: `L_G2b < 1.914e52` box photons/s per unit combined global-element-normalized share l1, with actual `D_lo > 0` from PR #80.
- First-cell support split: G1 has no resolved owner; G3 has zero current throughout the first exact-real PCHIP cell for the fixed-forcing state partial.

PR #80 observed one exact-rational scalar invocation, G01--G06 6/6 PASS, exit 0, no timeout. Those are inherited results, not new executions in this node.

## 2. Source mapping at the same site

The critical site restriction is preserved: PR #80 is bound to the second-half `thermal_t1_final` corrected population input. It is NOT automatically a predictor/gamma/corrector F0/F1 source-site enclosure.

At the parent commit, `physical_trial.py` defines

    heat_i = EV_ERG * sum_{species,group} node_current[species,group,i] * excess_eV[species,group]

and passes `photo.heating` directly to the thermal root. `unresolved_heating` is stored separately and is not passed as resolved thermal photoheat.

The fixed canonical excess moments in `bdf_heating_moment_calibration.csv` relevant to the actual first-cell resolved support are

    E_HeI,G2a = 5.058090825749249 eV,
    E_HI,G2b  = 31.261852675211813 eV,
    E_HeI,G2b = 20.60995742654565 eV.

The source constant is `EV_ERG = 1.602176634e-12 erg/eV`.

The owner mask makes all other resolved first-cell terms irrelevant for this fixed-forcing state partial:

- G1: no resolved owner;
- G2a: resolved HeI only;
- G2b: resolved HI and HeI;
- G3: current identically zero on the selected first-cell forcing hull.

This source mapping is distinct from the full OTS event graph in `event_uncertainty_operator.py`. Collisional/OTS rates and their thermal derivatives are not included below.

## 3. Norms

Let

    U_H  = ||delta u_HI||_1,
    U_He = ||delta u_HeI||_1,
    U_plus = U_H + U_He,

where `u_HI,i = N_HI,i/H_H` and `u_HeI,i = N_HeI,i/H_He` use the fixed global elemental totals and extensive node counts already carrying their quadrature weights.

The PR #80 G2b input norm is exactly `U_plus`. The G2a norm is `U_He`.

For compatibility with the earlier denominator paper's block norm, also define

    E_block = max(U_H,U_He),

so `U_plus <= 2 E_block` and `U_He <= E_block`.

The output norm below is the ordinary l1 norm of the RESOLVED per-node photoheating rate vector, in erg/s. It excludes the subgrid unresolved-energy reservoir.

## 4. Resolved photoheating theorem

At fixed comparison time, forcing, global elemental totals and fixed canonical energy moments, let `Q_res` denote the resolved photoheating vector.

For G2a,

    ||delta j_G2a||_1 <= L_G2a U_He.

Since only HeI/G2a is resolved,

    ||delta Q_G2a||_1
      <= EV_ERG * E_HeI,G2a * L_G2a * U_He.

For G2b, the two resolved species have unequal but positive fixed excess moments. Therefore

    ||delta Q_G2b||_1
      <= EV_ERG * max(E_HI,G2b,E_HeI,G2b) * ||delta j_G2b||_1
      <= EV_ERG * E_HI,G2b * L_G2b * U_plus.

Adding the independent group contributions gives

    ||delta Q_res||_1
      <= EV_ERG * [E_HeI,G2a L_G2a U_He
                   + E_HI,G2b L_G2b U_plus].                 (1)

Since `U_He <= U_plus`,

    ||delta Q_res||_1 <= B_plus U_plus,                      (2)

with the conservative source-bound expression

    B_plus
      < 1.602176634e-12
        * [5.058090825749249 * 5.7e52
           + 31.261852675211813 * 1.914e52]
      approximately 1.4205908e42 erg/s.

A safe quoted bound is

    B_plus < 1.421e42 erg/s per unit U_plus.                 (3)

For the earlier block-max norm one may instead keep the sharper algebraic translation

    ||delta Q_res||_1
      <= EV_ERG * [E_HeI,G2a L_G2a + 2 E_HI,G2b L_G2b]
         * E_block,                                         (4)

rather than silently identifying `U_plus` with `E_block`.

Equations (1)--(4) are direct norm consequences of the already validated owner-current bounds and the source's fixed positive energy moments. No new numerical owner evaluation is needed.

Units: owner-current derivative is photons/s per dimensionless share. Multiplication by eV/photon and erg/eV yields erg/s per dimensionless share. No extra node weight or proper volume is inserted.

## 5. What this immediately implies for the thermal balance residual

`thermal_backends.py` uses

    balance(logT) = energy(T) - parent_energy
                    - dt * [photoheat - cooling(T,pop) - expansion(T,pop)].

Holding the population argument, volume, Hubble rate, parent energy, dt and temperature fixed while varying only the resolved photoheat channel,

    delta_balance_photo = -dt * delta Q_res.

Therefore

    ||delta balance_photo||_1 <= dt * B_plus * U_plus.       (5)

This is an exact source-level partial derivative relation composed with the conservative owner bound.

It is NOT yet a temperature or thermal-energy output Lipschitz bound. To infer `delta logT`, `delta T` or `delta energy`, one still needs a positive uniform lower bound on the nodewise thermal-root slope

    partial balance / partial logT

on the selected endpoint set. The bisection/bracketing code by itself does not supply such an inverse-slope certificate.

Population-mediated cooling/expansion changes are also separate chain-rule terms. Equation (5) closes only the owner -> resolved-photoheat -> thermal-balance-numerator channel.

## 6. Scope and nonclaims

Established / source-derived here:

- exact site-preserving source map from resolved owner currents to `photo.heating`;
- resolved-photoheating state-partial norm inequality (1);
- conservative `B_plus < 1.421e42 erg/s` in the direct-sum normalized-share norm;
- exact additive residual relation (5).

Reused numerical evidence:

- PR #80 exact endpoint `D_lo>0`, G01--G06 6/6 PASS;
- earlier G2a/G2b owner-current bounds.

NOT verified here:

- complete source-input tube;
- predictor/gamma/corrector F0/F1 owner bounds;
- unresolved subgrid heating sensitivity as a resolved thermal source;
- collisional/OTS/atomic total flux derivative;
- population-mediated cooling and expansion derivative;
- uniform thermal inverse/root-slope bound;
- exact-flow rho;
- binary64 owner residual-correction parity;
- native four-site production, first interval or provider admission.

No claim is made that the thermal output itself is Lipschitz with constant (3). The current result is a numerator/residual-channel bound only.

## 7. Review and execution status

PHYS-MATH review, same assistant: site identity, input/output norms, support zeros, sign-insensitive l1 step, energy units, overlap of HeI between G2a/G2b, and direct-sum versus max-block norm were checked.

PHYS-MATH-CODE review, same assistant: `physical_trial.py` resolved/unresolved split, fixed energy-moment table, and additive `photoheat` placement in `thermal_backends.py` were checked. This is not independent reviewer certification.

New project/CAS execution in this node: NOT_RUN. The numerical coefficient is arithmetic composition of already published conservative upper bounds and fixed source literals; it is not presented as a new CAS or production execution result.

## 8. Next work unit

`REI_THERMAL_T1_PHOTOHEAT_ROOT_INVERSE_BOUND`.

Use the EXISTING saved endpoint box and fixed second-half forcing/site identity only. Bound `partial balance/partial logT` from below over the endpoint set with actual inclusion arithmetic. If the lower bound is positive, compose it with (5) to obtain the photoheat-mediated `delta logT`, `delta T` and thermal-energy component bounds. If the slope enclosure crosses zero, return the exact obstruction; do not add a floor or infer instability from a Cartesian overestimate.

Do not substitute this endpoint for the other three source sites and do not rerun the producer or canonical interval.
