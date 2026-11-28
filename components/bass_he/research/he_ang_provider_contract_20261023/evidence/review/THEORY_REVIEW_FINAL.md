# HE-ANG independent theory review — R6 PASS_SCOPED

Reviewer: `/root/heang_independent_review`. Workflow 1.0.0 / approval 0.2.

**Decision: PASS_SCOPED for the HE-ANG-CONTRACT source/frame/event-correlation derivation and corrected machine-readable template. F1 and F2 are CLOSED.**

The independent argument and original findings are preserved in `THEORY_REVIEW_INITIAL.md` and `THEORY_REVIEW_INITIAL.json`; the initial preparation calculation remains in `REVIEW_CRITERIA.md`. This final report adds the actual correction readback and scope decision. No scientific code, old fixture, provider scan, IVP or renderer was executed by this reviewer.

## Reviewed final identities

Paths below are relative to `BASS_HE/research/he_ang_provider_contract_20261023/`.

| Artifact | SHA256 |
|---|---|
| `theory/DERIVATION.md` | `c71c7d702f708d79449f70870a62184c5ea71128ef4351f0dde529bc4558fc3d` |
| `theory/PROVIDER_TEMPLATE.json` | `a96df2ade32b5fbe21529555758ea32f9f06d55fcb2a2adc54d0688260bdc99c` |

The supplied identities were checked against local bytes. A textual diff against the preserved child draft showed only the intended normalization subsection, corresponding machine fields, preparation-aware rate formula and rate-interface fields. `CONTRACT.json`, `BUDGET.json`, and `CLAIM_GATE.json` were also reread; their inspected identities are included in the JSON record.

## F1 closure — normalization

The corrected derivation §3 explicitly introduces event measure mass `Z=1` for a conditional law and `Z=sigma` for a cross-section-weighted law. It states that `P,R,K,C12` share that normalization and that `Ne=2Z`, `Np=Z`. The general recoil relations are now

\[
P_p=-P_e,\qquad K_p=Z(E-I)-K_e,\qquad
R_p=(m/M)R_e+C_{12}/M,
\]
\[
\operatorname{tr}C_{12}=2MZ(E-I)-2(M+m)K_e.
\]

`theory/PROVIDER_TEMPLATE.json` now carries the same `event_measure_mass`, normalization-dependent counts, `K_p` and `trace_C12`. Subsequent conditional equations are explicitly the `Z=1` specialization. Zero cross section leaves conditional probabilities undefined rather than inventing a normalized event law. **F1 CLOSED by direct algebra and final-byte readback.** The later implementation review should confirm the sigma-weighted path uses this contract.

## F2 closure — preparation-aware rate

The corrected Eq. (30) uses `sigma(E,a;preparation)` and evaluates the relative incoming axis for each pair. The accompanying text states that suppressing these arguments requires an explicitly unpolarized rotationally invariant preparation. The machine template's `rate_interface` preserves the same argument and relative-flux policy. **F2 CLOSED by direct formula and template readback.**

## Scientific scope accepted

The result provides a consistent finite-mass event-measure interface, normalization rules, energy/frame maps, raw first and second moment transforms, and capability/error obligations. The two-cone construction establishes the specific event-pairing information absent from an inclusive electron marginal, even when that entire marginal and the scalar energy ledger agree. The complete independent calculation and checked identities are in the initial review.

The accepted pressure-type convention is `R_s=<sum qqᵀ/m_s>`, with `S_s=R_s/2`, `K_s=tr R_s/2`, and `J_s=STF(R_s)`. Its boost term is `m_s N_s UUᵀ`; this applies to signed reaction sources as well. The five-coordinate finite-mass shell requires all physical radial roots and their Jacobians. The witness's four-direction quadrature is exact for the specified degree-two moments, while its finite rotational symmetry is kept distinct from the continuous axial law.

The contract keeps physical source selection at `SOURCE_INPUT_PENDING`, empirical calibration false, model replacement false, and no-merge/no-activation holds true. HE-X1's 32 fixtures and independent review remain reused evidence with zero replay. The new small verification allowance is a separate bounded contract; it neither resets historical ledgers nor claims an exact residual allowance for the old unknown-cost failure.

This theory decision licenses implementation and the already frozen affected contract controls. The resulting code still requires C9 independent review and its actual execution receipts. The theory decision does not admit an empirical H1 kernel, a source scan, a new IVP, a completed baryon closure, or runtime activation.

## Remaining obligations

- Implement and verify the selected explicit event/metadata interface under the fresh cumulative budget.
- Independently review the actual changed code, its normalization and error paths, and actual receipts at C9.
- Keep physical source, support, correlation and uncertainty qualification pending until a pinned source payload and its evidence are supplied.

There are no open theory findings in the reviewed scope.
