# THEORY16 R9: source-bound current column, finite bins and event-aware connection

2026-10-14, Asia/Seoul. Selected R9 only, following HE43 head `efacaa1c7a17416debac18101cc6558e44e825cf`. Formal result/code connection with stage-local checks; not R10, a new source trajectory, independent scientific review or production promotion.

## 1. Canonical physical quantity

Signature(-,+,+,+), x0=ct, u.u=-1, dx^a=c*k^a*ds, k.k=0. Source age theta is in seconds; q_a=c*nabla_a(theta), u.q=1, A=q.k>0 and D=-u.k>0. Retain the full current

    J_e^a=c*N_e*u^a/V+j_e^a,
    C_[a,b]=integral_a^b [c*D*N_e/(V*A)-k_a*j_e^a/A] dtheta,
    B_[a,b]=sigma_T*C_[a,b].

C is a cross-section-free electron column, in m^-2; B is dimensionless. With j=0 the previous pure-bulk formula is recovered. Constants c,hbar,k_B and atomic eV/J conventions remain explicit. k is a parametrized dimensionless null tangent, not an unspecified physical four-momentum.

The original source/clock/volume/current and coverage travel with C. Change a passive constant cross section by applying it to the same C, rather than integrating chemistry again or multiplying by sigma twice. An endpoint-only certificate cannot supply an arbitrary cropped sub-bin. Different geometry, spatial current, energy-dependent opacity or changed source dynamics need their own matching inputs.

## 2. Actual CR53 consumption and finite-bin connection

The new executable `current_to_bin.py` reads the actual preserved CR53 result and contract, checks their supplied hashes, source unit/horizon/geometry/clock, nonzero-work assembly, center/radius pairing and branch status. Source is CR-IR-04 at `cc3249947a1fc93f2bacf2190604371dfde2f42f`; the original archive hash is `5e48631308ff68dc89287463094cb04561735fcd26fea1e3309b558ed555e4d8`. It has h=100000 proper seconds, H=(2,4,6)e-15/s, V(t)=V0 exp(Theta t), zero bulk tilt and spatial current, with total initial free-electron count3.

The stored source full-depth interval is approximately

    [5.94727990479807732897461970749551106531742e-15,
     5.94727990510379930255537770859128857092795e-15].

The source radius is <1.528609867904e-25. The same moving reference center and nonzero-work bound remain paired. No static R7 center, CR54 event witness or HH rate is inserted into this source. Exact Fractions, including the smaller signed ionization surplus, are preserved in the archive.

REI115 supplies the finite-bin survival formula. Let T>=0 be the near-edge-to-observer optical tail and B>=0 the depth of the finite bin:

    P(T,B)=exp(-T)*(1-exp(-B)),
    P_cond(B)=1-exp(-B).

The second quantity is conditional on survival from the near edge to the observer, not renormalization of a finite bin to unity. These are passive optical survival/scattering-location functionals; no detector count or polarized redistribution calculation is supplied.

For nonnegative boxes,

    P in [exp(-T_hi)*(1-exp(-B_lo)),
          exp(-T_lo)*(1-exp(-B_hi))].

This remains a valid outer enclosure for correlated inputs; endpoint attainability is not claimed. An unspecified foreground remains `None`/null, never silently zero. The T=1/4 evaluation in the tests is explicitly synthetic. For a common baseline B0 and positive signed deltaB,

    P_cond(B0+deltaB)-P_cond(B0)=exp(-B0)*(1-exp(-deltaB)).

Retain this paired expression rather than subtracting unrelated histories. A shared known foreground multiplies it by exp(-T); different foregrounds require their own terms.

The new exact-rational implementation encloses exp(-x) by odd/even alternating Taylor sums after reducing x to[0,1], then outward rational squaring. Its bounded reference domain is x in[0,1024], digits20..200. It does not evaluate a cancellation-prone binary64 `1-exp(-B)`; production point estimates should use `-expm1(-B)` with a separate error contract.

Actual CR53-derived column and probabilities, conservative short displays:

    C_full in [8.9399726754240372e13,8.9399726758835997e13] m^-2,
    P_cond in [5.94727990479805e-15,5.94727990510379e-15],
    deltaP_ion in [1.23679012351712e-23,1.26736232087520e-23] >0.

The full precise outward table and exact rational endpoints are in results/RESULT.json and OBSERVABLE_TABLE.csv. The thin-probability correction is bounded by B_hi^2/2<1.768506914e-29. This is new arithmetic evaluation of an inherited source certificate, not new source ODE integration or a complete cosmological foreground probability.

## 3. Separate Thomson conventions explicitly

HH60's actual source-bound result identifies sigma_source=6.6524587051e-29m2 versus sigma_BASS_P01=6.6524587e-29m2. Keep the exact conversion

    sigma_BASS_P01/sigma_source =66524587000/66524587051
                              =3913211000/3913211003.

The same CR53 column gives BASS-convention depth

    [5.94727990023869126450836072132658683302334e-15,
     5.94727990054441323785474191012189202411111e-15].

The central depth shift is approximately4.55938606458344739232e-24, or29.8270092344479 times the inherited source donor radius. This is a deterministic convention change, not physical model disagreement or measured-constant uncertainty. The P01 label is source-specific, not an assertion about every BASS code path. Rescale depth and reevaluate the nonlinear probability; multiplying P by the cross-section ratio is not exact.

## 4. Formal connection through a thermal-prefix event

CR54 newly supplies a two-edge subthreshold event witness, not an extension of CR53's full HI/HeI trajectory. Its fixed-time energy reset is conservative but its event-time state sensitivity is noncontractive. We read that result without replaying its numerical event campaign.

For x'=f^-/f^+ in one clock, guard g(theta,x)=0, reset R(theta,x), and d*=g_theta+g_x*f^- nonzero, the standard saltation is

    S=R_x+(f^+-R_x*f^- -R_theta) outer g_x/d*.

Add a continuous optical accumulator z'=ell^-/ell^+, reset z^+=z^-; assume the guard does not depend on z. The augmented saltation is exactly

    S_aug = [[S,0],[(ell^+-ell^-)*g_x/d*,1]].

This follows by applying the ordinary saltation to the augmented vector field and reset. The lower-row direct event term vanishes when the total current and geometry/clock give ell^+=ell^-. The internal S and subsequent ell_x*delta x response remain. First-order saltation is not a finite-error certificate. A finite jump of ell alone still leaves the integrated z continuous, though its event sensitivity row can be nonzero; a physical impulse would require a different reset model.

For the count-preserving thermal transfer Nth+=Nth-+deltaN and Nactive+=Nactive--deltaN, total J_e is unchanged if the bulk/spatial current conditions also match. CR54's stronger witness has total N_e=3 throughout, so its fixed-horizon Thomson integral is event-time independent. That witness's numbers are not substituted into CR53. In general no direct optical event term does not eliminate post-event chemistry/work sensitivity.

For a purely spatial stress change deltaT_ab=delta p*h_ab+delta pi_ab, the comoving energy projection vanishes while the work contraction is Theta*delta p+shear^ab*delta pi_ab. Thus preserving current or total energy at the reset does not delete subsequent stress/work differences.

## 5. Pre-bin memory and ownership

With a continuous reference error e(theta) and source residual, a bin[a,b] still receives source errors/births before a, unless they have already been carried into e(a). For constant weight and constant birth forcing from0, the integrated response is proportional to(b^2-a^2)/2, not(b-a)^2/2 or endpoint response times duration. REI115's pre-bin residual kernel and HH60's actual birth-time integral are kept in the connection contract. Event, source, volume work and residual corrections must each be consumed once.

## 6. Current related results and scope

-CR54 final v2 head `e484feb7762f969dbe29b3116b886455baa14395`: actual compact event theory read; new two-edge witness has total current3, internal saltation retained. Next NT_PREFIX_EVENT_FULL_SOURCE_BINDING. Its old no-event parent and this witness remain distinct sources.
-HH60 head `c56cae5662a4c44b4f387699b5602355e63cb7dc`: actual R5 result read, paired restored-minus-original observable signs and separate sigma conventions; next PHYS28_CONTINUUM_ORTHOGONALITY_AND_CHANNEL_CALIBRATION. No HH numerical reaction rate imported into CR.
-REI115 commit `4716c469535422ba6c293a26e3478cedd3923e6b`: actual RESULT_AND_HANDOFF read; finite-bin current/clock and pre-bin memory reused. Its source-specific interpolation result is retained while physical foreground, normalization and node error remain its own input obligations. CR53 numbers do not replace its SHEAR12 fixture. Native CR/RCT/HH activation remains unchanged OFF.

Primary comparison: Kong, Payne, Zhu and Johnson, arXiv2306.06862v3, Eq9-10, for standard saltation; actual Exa primary equation passages and SciSpace discovery. The augmented observable specialization above is supplied directly; no novelty claim for the standard matrix. Web direct arXiv HTML cache miss and A&A403 were retained, with primary abstract discovery available. No PDF image analysis or unavailable full-text claim.

## 7. Actual tests and failures

-New source/contract/arithmetic run:50named conditions passed, exit0. Three focused probability tests passed. These counts include source identity/domain tests and are not independent theorems.
-The first deliberate binary64 candidate returned0 for depth1e-30 and failed a focused assertion. A test-bound inequality was corrected before implementing the new algorithm; the same intentional candidate still failed, then the exact implementation passed. Original tests/candidate/logs retained. This is a new reference discriminator, not an upstream bug claim.
-An initial final-check variable typo th/nth produced NameError and was repaired only in the checker. Original failure retained; scientific source/results/tolerances unchanged.
-Two actual cloud Wolfram15.0.1 calls:13zero scalar groups plus3True conditions, and7actual xTensor1.3.0 zero tensor residuals. Exact submitted scripts saved before calls; selected observed outputs are normalized transcriptions, not raw transport bytes. Some zero arrays are summarized explicitly as groups.
-Official xAct archive SHA2567a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be; xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Actual xPerm load followed by pure-Wolfram canonicalization. No failed CAS residual returned.
-Same author/separate arithmetic and CAS; external independent review and native subagents NOT_RUN. No old source RHS/ODE/generator/native/HPC or old-suite replay. General contracts and reference implementation do not claim production call-site integration.

## 8. Reproducibility and preservation

The adjacent `current_to_bin.py` is the actual tested8103-byte source, SHA2561e2c16894d079ae3ec1088fb1fb22c6f6c377c168b5a47524ee90d1020f37047, Git blob386d7cbc10096ba70c1adf5793541a8b4d5b0ef4. Full exact inputs, tests, results and proof are in the archive.

[Full Korean report](https://drive.google.com/file/d/1XD79GIgu4_b6P5yTUmKONdyPCHLsUSSF/view).
[Complete reproducible ZIP](https://drive.google.com/file/d/1am9p5zv6oTyzMhdabx1UndKJnVhs9CH0/view): `BASS_HE_THEORY16_R9_CURRENT_BIN_20261014_v1.zip`,59690bytes,41members/40manifest payloads, SHA256bb8bd14d625509b3ac613c10246163612a5a865ba9c323347487d345a07307af. Local CRC and all40payload hashes verified. Both existing cloud destinations acknowledged the ZIP; Dropbox completed59690bytes, ID `id:BSpOijBcT10AAAAAAD48Pw`. Drive report also acknowledged correct name/parent. Separate Dropbox report upload failed FETCH_FAILED on initial and one retry; its exact report is preserved inside the completed Dropbox ZIP. No duplicate archive or remote restore claim.

Extract BASS_HE_THEORY16_R9_20261014 and run `python checks/test_probability.py`, `python checks/run_r9.py`; packaging-only verification is `python checks/verify_bundle.py`. The archive has no font binaries or source-paper PDFs.

Next selected stage R10: compact completion/resume handoff using these existing results. Existing actual native current/clock/observer binding, HE provider/moments/moving-stage/certificate adapter, original RUX/all-Bianchi/D2.3 and independent-review obligations retain their owners. No new global gate, production switch, main merge, force push or external-repo mutation.
