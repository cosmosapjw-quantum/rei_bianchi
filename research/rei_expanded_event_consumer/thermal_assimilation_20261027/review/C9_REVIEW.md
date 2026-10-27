# C9 outcome review — conditional native thermal source

Date: 2026-10-27. Reviewer: `/root/normalization_review`.

**Decision: `PASS_CONDITIONAL_NATIVE_COUPLED_LOCAL_SOURCE`. Blocking findings: 0.** The preserved authorized `attempt01` supports admission of the selected conditional local source, its frozen directional derivative, and the stated native component/coordinate joins. `REC-COUPLED` remains **PARTIAL**, with original-node completion increment **0**. This decision does not change the working 32/88 or central 27/88 counts, admit an integrated history or whole-domain VigilODE certificate, or close L4/global physical completion.

## Review method and evidence identity

This review reuses `C5_PREEXEC_IMPLEMENTATION_REVIEW.md`. The reviewer contributed theory but did not implement the source or checker. No scientific source was imported or executed, and no numerical physics calculation, provider test, IVP, quadrature or spectral source was rerun. The review read the saved numerical outputs, inspected their recorded row residuals and controls, compared JSON evidence and hashes, and checked resource-accounting arithmetic. Byte identity establishes which reviewed artifacts ran; the numerical claims come from the separately inspected checker and its saved outcomes.

The operator, checker, runner and frozen input manifest retain their C5 SHA256 identities: respectively `a84f318d66c11166db080f0f4db64b48f82ea5bc09abb87671c2ca44b162bbb6`, `5832cb8062a0c8e46f7ca892ae3260328fedd89bd4dc74303bbc41e2a508acdb`, `e32add916b80df9e5e53933f50a29e5daa817701aa6b21e2b6ec3285ce946312`, and `8f55b02555bc2ef1797efa77f54ed7c185275a384985f01afd5b626dcb4544b2`.

| Preserved attempt artifact | SHA256 |
|---|---|
| `stdout.json` | `3f6e942336cb18cf1422ce4736984fb5d7f7d85ca1af39aa0f126748a0c66d99` |
| `CHECKS.jsonl` | `762842072061a5423cd06f6510249b2201911a750e2044a5c84c98c7c6075dd9` |
| `FORWARD_RAW.json` | `de1fbe6b125efce45a4999f1e4666b7e8bde1274a4d3b81d6dba854853284149` |
| `RESOURCE_RECEIPT.json` | `126f716340b1e42a0c90e2a06fdddfe299e3e822c5c382be55f51a1da877575e` |
| Empty `stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

`CHECKS.jsonl` is exactly equal, as parsed data, to the 118 check records in `stdout.json`. All 118 names are distinct, all pass, and every recorded row maximum agrees with its summary. `FORWARD_RAW.json` is an exact subset of the final observations. The resource receipt identifies the same input manifest and exit code 0, with no failure or stop reason.

## Numerical acceptance

The maximum algebra/native residual is **3.3297273737548715e-16**, from the DR transition JVP, below the frozen **2e-14** threshold. The independent transition-source and physical-caloric-JVP oracle maxima are **2.5188126750533155e-16** and **2.4395117223522834e-16**. The total energy-store residuals are **2.7133188970425294e-17** for the source and **2.5867107375229656e-17** for the derivative. The actual HE sink's returned `Tdot/T` matches the new log-temperature row with a recorded residual of zero.

Both frozen centered-FD steps use the identical predeclared analytic operand scale in each row. The recorded maximum over all maps and steps is **1.373105919989494e-10**, below **2e-8**.

| Output map | Maximum at h=2e-4 | Maximum at h=1e-4 |
|---|---:|---:|
| Proper-time | 8.539441405764767e-11 | 5.833296609399081e-11 |
| Physical-density | 1.373105919989494e-10 | 1.0097271786836361e-10 |
| Reference-density | 8.693577663494068e-11 | 2.3294450982679987e-11 |
| Eta-time | 6.865869718517768e-11 | 2.4467898344279536e-11 |

Rows 0, 5 and 6 have exactly zero contribution scales and zero recorded differences in every map. The minimum nonzero scale across the saved FD maps is about **1.3060744054111973e-42**, consistent with preserving tiny energy/source rows instead of imposing a unit denominator floor. Both steps pass the same criterion. Their rowwise behaviour does not establish a universal factor-four convergence rate, and none is claimed. This is one frozen directional derivative, not a full 25-state Jacobian certification.

## Boundary and failure-discrimination evidence

The saved outputs show exact-zero photo rows when the source is off; exact-zero assimilation transfers for zero nu and for an empty fast pool; and exact-zero RR/DR and Compton at zero thermal-electron density, with inward assimilation count transfer. The standalone Planck equilibrium has `T_r=9.4820145 K`, zero power, and a nonzero derivative `-3.076926674822812e-41 J per baryon per second` along the frozen test direction. As established in C5, this limit calls the Compton helper alone and does not evaluate REC below its 100 K domain.

Unsupported temperatures, wrong source owner, UV Compton, prompt thermalization, invalid reservoir support/reference density and nonzero neutron/tritium state or tangent are all rejected. All-electron substitutions produce nonzero RR, DR and Compton errors. The proper thermal electron density is **7.013468020719699 m^-3**, compared with the all-electron value **9.351290694292933 m^-3**. Omitting the assimilation particle-count term changes the isolated log-temperature response by **1.2146481832739274e-18 s^-1**. Wrong log-temperature density scaling and omitted density, reference and clock derivatives are detected. The separate changing-reference value and complete differential controls pass; they remain manufactured algebra controls.

The two saved positive measures have the same number and energy moments and the same transfers under constant-in-energy nu. Their energy-weighted-rate transfer differs, 4 versus 5 in the dimensionless control. This supports the stated conditional moment closure and does not assert a universal no-go theorem.

## Actual component join and scope

The saved background is the PW19 HeII source at z=2.479, with `T=14919.863839279506 K`, `nb=10.669321142818111 m^-3`, `r=8.033643390985384 m^-3`, and `beta=1.328080003500061`. The fast pool is explicitly manufactured: `zeta=0.2191163469802296` and `w_nt=7.010531745782858e-19 J per baryon`. The declared rate `nu=8.160348695705333e-18 s^-1` is independent of H despite equal base values.

At this point, assimilation supplies **6.103746165608298e-35 W/m^3** to the thermal pool. Native RR, DR and Planck Compton contributions are respectively **-4.0749095689223304e-36**, **-3.9721389300608827e-50**, and **-8.60381044771227e-36 W/m^3**. The net thermal power is **4.835874163944834e-35 W/m^3**. The actual HE call at supplier commit `ac6042a6b0610b09d0576538767ee0299389a5eb` records 21 ion rows plus one explicit thermal-electron row, and returns `Tdot=1.546634155707279e-13 K/s` and `Tdot/T=1.0366275271463654e-17 s^-1`.

These values describe the conditional instantaneous reservoir and source. They do not determine a physical stopping time or reconstruct a cosmological fast-electron history. Native Mao RR hybrid and DR moment closures retain their provider domains, masks and modeling limitations. The result uses the selected Planck reference; it does not qualify UV Compton, angular transport, differential stopping outcomes or a new full-network trajectory. Source-only normalization maps do not supply omitted expansion/pressure work.

## Resource accounting and remaining delivery step

The execution receipt records child CPU **0.511638 s**, wrapper CPU before receipt tail **0.053470553 s**, and conservative tail reserve **0.02 s**, for a charged new execution debit **0.585108553 s**. Recorded wall time is **0.5433866739986115 s** and child maximum RSS **27080 KiB**. The new CPU and wall limits were respected. The known cumulative planning debit before this outcome review is **12.821247432 s**, including the preserved prior debit, vendor-copy debit and authoring metadata exactly once. The original planning cap remains **10 s** after restoration; the temporary **14.9 s** cap does not reset the debit. Main-campaign **595.225063/600 s**, `NO_MORE_IVPs`, and other historical ledgers remain unchanged.

The three measured metadata-only phases of this reviewer total **0.057814337 process CPU seconds before serialization** and are separately itemized in `C9_VALIDATION.json`; they are not part of the preserved execution receipt. Unmeasured initialization/tool/serialization tail remains `UNKNOWN_NOT_ZERO`.

The plot is being prepared independently from the saved data. Its visual review is a separate presentation step and will be appended without reopening the closed scientific source review or rerunning the checker.
