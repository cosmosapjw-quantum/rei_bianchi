# R6/C9 same-author adversarial referee, one bounded hostile pass

**Independence:** Self-adversarial audit with independent original scanned papers and exact tool/code tests. No separate author or native subagent execution; therefore `R6_DISTINCT_AUTHOR=C9_DISTINCT_AUTHOR=NOT_RUN`. Audits do not count toward central physics DAG.

| Question | Failure mode/counterexample | Disposition |
|---|---|---|
| 1969 source actual visually checked? | Previously PR283/286 relied on OCR; original scan p.29 Table II and separately typeset p.14 now uploaded. Verify each of 21 Li II printed ordinates against nested old `A_TAB`, and total 1945.475 s^-1 against Table I 1.95e3 rounded. | RESOLVED scoped to Li II singlet table only; old archives untouched. |
| Is 1S+3P a pure singlet yield? | Ferrett Table IV columns: **unresolved 1S+3P**, so setting this equal to 1S would overestimate true singlet source. | BLOCKED; only `0<=sigma_1S<=sigma_(1S+3P)`. |
| Is 3S merely speculative? | Ferrett provides measured sigma_3S >0, e.g. at 85 eV sigma3S=0.99 Mb out of n2=1.58 Mb. | Confirmed actual laboratory state-specific partial cross-section. |
| Missing n=3 for 75 and 77.5? | Ferrett Table IV has empty n3 entries, not numeric 0. | No inferred 75-80 n2+n3 rates. |
| Do n2+n3 sections exhaust K-shell? | n4+n5 shake-up and valence/double channels explicitly discussed. | `K×f3S_n2n3` conditional, never actual full source-rate admission. |
| Can the Ferrett 20% absolute systematic cancel? | It is a shared scale across measured channels, whereas quoted statistics differ and are correlated. | Only central fractions; no unjustified independent Gaussian propagation. |
| Is isotope-specific triplet fraction measured? | 1987/1991 experiments not separately Li6/Li7-resolved in these source tables. | Same electronic ratio on both isotopes only conditional. |
| Historical ionization energy discrepancy? | Ferrett Table I singlet binding=66.15 eV vs Langer Fig2=66.31 vs NIST/BASS 66.3143. | Preserve three numbers, no secret overwrite, NIST/BASS emission physics only with original owner. |
| 2E1 photon rate equals production yield? | Drake 1969 A(y) gives conditional decay rate per occupied singlet state; not singlet population production. | Separate source K and emission, no forced all-singlet beyond bounded upper. |
| 3S M1 guaranteed? | Drake triplet 2γ 1.50e-6 s-1 vs measured M1 lifetime 52.2 s. | 0.999921706 M1 branch only **vacuum two-mode**; collisions, optical density, hyperfine not bound. |
| Does mapping lab fraction onto native K match exact BASS operator? | BASS K is source-native but original σ_K energy/ionization subchannel owner not jointly verified against experimental σ_n2+σ_n3 and omitted n>=4, direct valence, DPI. | HOLD physical rate admission; publish conditional source-subspace response. |
| Does interpolation become measured value? | Six native BASS bin energies lie between 13 actual experimental points. | `MEASURED_INTERPOLATION` distinct from printed measurements; outside [75,99] NO_EXTRAPOLATION. |
| Did branch CI fix alter actual physics? | PR288 separate Rust quality/fmt green, not this physics branch. | No port/merge/force; direct target Python verification only. |
| Could source window cover full cosmological CMB? | Original K includes energies 65.63..194.318, only 6 bins measured. No time/angle RT or secondary thermalization. | F4 PARTIAL; no thermal or τ_CMB claim. |

**Positive outcome:** the Drake 1969 Li II table pixel blocker is resolved; the measured triplet 3S partial-source physics and hard upper bound on unresolved singlet can be combined with original BASS K only under explicit subspace-normalization assumption. The source owner and acceptance gates are not silently expanded. No new strong no-go claim.
