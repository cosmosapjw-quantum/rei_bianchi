# Frozen contract and loop-2 specification review

2026-10-07. Independent reviewer. Inspected `repo/research/transport_20261007/igm-two-loop/CONTRACT.json` and `LOOP2_SPEC.md` before the candidate implementation was ready. This note reviews their mathematical contract, not incomplete stub source.

**Verdict: mathematically sound bounded scope, with oracle scaling requiring explicit pre-execution definition.** The two loops are genuinely dependent: the continuous exported measure uses the admitted first-loop positive restrictions and all-owner logarithmic characteristic. The scope explicitly preserves the unresolved production, gas-feedback, projection-history, and 37-field long-window gates.

## Source-on export formula

Write d=ln(Emin/Ec), D=ln(Emax/Emin), and s>=0. A characteristic crossing the cutoff at time t has eta=t+ln(Ec). It receives source over [max(0,t-d-D),t-d], if the interval is nonempty. Hence its density at crossing is q min(max(t-d,0),D). Because d eta/dt=1, this is also the number export rate per hydrogen nucleus. Integrating from 0 to s gives

    out_N(s)=q [min(w,D)^2/2 + D max(w-D,0)], w=max(0,s-d).

This proves the specified result and the zero derivative at first onset. The cutoff energy owner is epsilon Ec times that count. The injected rates are q integral dlnE=qD and epsilon q integral E dlnE=epsilon q(Emax-Emin), so the specified cumulative injection owners are correct. The source is constant per logarithmic energy, unlike the original manufactured q proportional to 1/(EH); the specification correctly treats it as a new explicit control.

The statement about source shutoff refers to a characteristic leaving the emitting band. No global source termination time is present in this fixture. A global shutoff experiment would be an additional case and should not be claimed as executed merely from this band-exit example.

The left-front density follows directly: close to eta=ln(Emin) from above, the source-active duration is eta-ln(Emin), so f=q[eta-ln(Emin)] after local source exit in the transparent case. A positive y exp(beta y) family therefore has the correct linear trace structure, although it is not an exact arbitrary source-history representation. Restricting it to an interior child must retain the original coordinate and taper until an explicitly declared projection.

## Fixed owner and budget tolerances

The source-free denominator correctly keeps emitted_N=emitted_E=0. It does not use the initial inventory to weaken the original floor. N0=1e-8 means the count budget floor 1e-20 corresponds to about 1e-12 relative accuracy on the initial stock; this is a legitimate stronger control. Adding the dimensional underflow bound to the absolute residual is conservative. A passing small-inventory control remains a small-inventory control and does not certify arbitrary normal scales.

The phrase `relative_or_scaled_error_target=3e-12` is insufficient by itself to define a reproducible acceptance predicate. Before oracle execution, specify the target for positive normal readouts, exact mathematical zeros, and positive zero-readout tails. One unambiguous choice for a positive owner represented by a finite authoritative logarithm is |expm1(log(candidate)-log(reference))|<=3e-12. This measures relative error even below binary64 readout. A normalized common-scale comparison can also be used, but the scale and error denominator must be frozen before results. Using absolute log error divided by the magnitude of a large negative log does not measure physical relative error and must not silently replace it.

## Prescribed opacity convention

The optional lambda_HI(eta)=2 exp[-3(eta-ln(Ec))] is a valid dimensionless prescribed characteristic coefficient, but it is constant along that characteristic. With stock control s0=-ln13, it is approximately 13^3 times the natural initial-energy formula 2(Ec/E_initial)^3. If the intended coefficient is normalized to initial physical energy, it should instead be 2 exp[-3(eta-s0-ln(Ec))]. If the literal eta formula is retained, label it as a prescribed toy coefficient. Neither formula is the full physical time-dependent opacity c n_H(s) x_HI(s) sigma(E(s))/H(s).

## Observable envelope

The E^-3 inequalities are sharp over all positive measures with the prescribed two moments and support. They follow from Jensen's lower bound and the integrated secant-line upper bound. Restriction-based refinement can sum valid bounds for each restricted positive measure; this adds subpanel moment information and should never be described as obtaining a sharper result from the original two global moments alone. Mean and endpoint atoms are proof controls, not authorized replacements of smooth simulation panels.

## Remaining review steps

After implementation, inspect exact restrictions, all-owner logarithmic arithmetic, source/stock quadrature weight units, and export ledger wiring. Execute reviewer-owned comparisons against independent positive integrals. Preserve first failures and distinguish primitive acceptance from the still-open production exporter and coupled cosmological history.

## Pre-execution clarification accepted

The root subsequently fixed the positive-owner predicate to |expm1(log(candidate)-log(reference))|<=3e-12, with exact zero requiring authoritative emptiness, and changed the optional prescribed opacity coordinate to eta-s0-ln(Ec). Both requested clarifications are present in the actual files. Contract review is therefore ACCEPTED for the bounded declared scope. The existing V2 rejection was read from `work/root/baseline_blocker.log`; this is evidence readback, not an independent rerun by this reviewer.
