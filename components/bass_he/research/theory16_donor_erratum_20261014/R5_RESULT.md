# THEORY16, selected R5: donor erratum and optical-depth repair

Unit: `HERE_RUX03_DONOR_ERRATUM_OPTICAL_REPAIR_16`. Date: 2026-10-14.
Evidence: direct derivation, exact-rational source-bound calculation, actual Wolfram/xAct. Independent scientific review remains pending. Native subagents were not available; execution was serial. This is R5 with its local checks, not a completion or promotion of the whole R1–R10 workflow.

## 1. Dependency correction

The source author in bass_cr PR52, commit `110724bf8e4fc0d937d3098ee78f441aa22802c2`, corrected the stopping-event l1 norm in separate active-bin energy and thermal coordinates. For Ep>Ed>=0,

    nu_stop=(-Ep,Ed,Ep-Ed), ||nu_stop||_1=2Ep,

not 2(Ep-Ed). The exact example(-10,9,1) has norm20, not2.

As a result, CR_TIME_DONOR NT4's donor-error/branch certificate and its downstream use in THEORY14 CR numerical radii and THEORY15 full-model optical-depth intervals are no longer supported by the stated old proof. The old integrated radius1.210140295...e-22 and old99.6864% budget decomposition are superseded as current certification. Original archives and historical records are retained. This does not assert that the unknown actual errors necessarily violate those old numerical values.

Retained independently of this error: NT1 exact first-event exposure solution; the surrogate optical-depth integral; current/census and conditional error-transfer identities; THEORY14 HH lane; cold KN angular interval and positive-energy kinetic-shape bound.

New source52 uses stopping depth(P,S)=(2,3), with three added internal edges and a valid full-path cutoff bootstrap. Its source archive SHA256 is `f743d601cf67603a2ddb7a3e46f50d7384898e6d269ea3b3ba58a3e2c693af2b`. Its MODEL.json is byte-identical to the prior source model.

## 2. Exact projected observable: why the existing surrogate integral survives

Read the actual source52 `checks/check_nonlinear.py` and the earlier `checks/reference_flow.py`. In the selected nonlinear surrogate let

    y=(x_H,x_He,P0,S0),
    n_th=(n_th0+b_H*x_H+b_He*x_He)/V,
    r_a=kappa_a*P0*(X_a0-x_a)/V.

The projected equations are exactly

    x_a'=r_a,
    P0'=-r_H-r_He-lambda_P0(n_th)*P0,
    S0'=-lambda_S0(n_th)*S0.

The added stages modify hidden P1/P2/S1/S2/S3/U but do not enter these four equations. All added endpoints remain above the bath cutoff; they transfer active electrons internally. Their descendant ionization is still omitted in this selected surrogate and covered by its new donor residual. The stored retained rates depend on n_th, not directly on U/T within the fixed branch.

Let Pi select y. Then Pi F_selected(Y)=f(Pi Y), with the same f and initial y as the old first-event model. Local Lipschitz continuity and initial-value uniqueness prove equality of y(t), hence of N(t)=3+x_H+x_He and its Thomson integral. This is a source-specific closed projection. Hidden temperature and spectrum are not identified.

The same argument would require revision if added branches reached the thermal bath, new ionization were activated inside the surrogate, or root rates acquired U dependence. A test adds a_T U P0 and obtains nonzero hidden derivative -a_T P0.

Therefore the retained exact surrogate optical-depth interval applies to the newly selected nonlinear surrogate as well. No frozen-rate-reference state error is added to this exact observable equality.

## 3. Integrate the corrected source bound using endpoint scores

For fixed certified horizon h, source52 supplies an all-time majorant

    B_D(t)=sum_j C_j*t^(r_j+1)*phi_(r_j+1)(L*t),
    phi_m(x)=sum_(k>=0) x^k/(k+m)!,  C_j,L>=0.

The stored score b_j is an upper bound on the corresponding endpoint contribution at h. Termwise integration of the positive series yields

    integral_0^h B_D(t)dt
      <=h*sum_j b_j*phi_(r_j+2)(L*h)/phi_(r_j+1)(L*h).

The ratio is a positive weighted mean of1/(k+r+2), so it is at most1/(r+2), with equality in the zero-growth limit. A rational positive series through k=50 with a geometric tail encloses each phi ratio. Each upper ratio is then explicitly rounded upward to a10^-30 grid.

At h=100000s, L*h=1.7694336139589225013..., the upper ratios for r=1,2,3 are respectively0.279584639147585158126344661152,0.224685683262858304549431006549,0.186326820619855907776012816879. The exact source-score calculation gives

    integral_0^h B_D(t)dt <=1.81877618051763168543e-4 eV*s/cell.

No source ODE, rate campaign or full generator was rerun. This uses the corrected upstream proof at its own status and scope, not an independent reproduction of that entire proof.

## 4. Repaired optical-depth intervals

Keep the fixed homogeneous reference medium, proper h=1e5s, V=1.0060180360540648648m3, initial free-electron count3, nuclear count13, HI/HeI ionization and downward stopping. Signature(-,+,+,+), u.u=-1, physical velocity c*u, photon energy E=hbar*omega. Energy conventions include k_B and the parent eV conversion. The reference volume converts counts to density; this is not a single crossing of a box of side V^(1/3).

From the common chemical census,

    |N_full-N_selected|<=B_D(t)/Bmin,
    R_N=c*sigma_T/(V*Bmin)*integral B_D(t)dt,

where Bmin=13.60570000000000057...eV. With the same specified central constants c=299792458m/s and sigma_T=6.6524587051e-29m2,

    R_N=2.65005867974783344689e-25.

Outward displayed intervals:

    tau_T,full in [5.94727990825430e-15,5.94727990878432e-15],
    tau_T,full-tau_initial in [1.22557e-23,1.27858e-23] > 0.

The source's full finite-model ionization excess is now positively separated from the initial3-electron baseline. This does not determine the sign of full-minus-surrogate. Its radius is approximately2.11653% of the retained surrogate excess.

For a70eV gas-frame diagnostic, retain the separate isotropic active-bin / same-temperature MJ thermal closure and the earlier cold KN factor. The positive-energy spectrum-shape radius5.51358655786418747567e-23 is independent of the invalid NT4 norm. Combined with the new Thomson interval:

    tau_KN,full in [5.94565103814730e-15,5.94565114894891e-15].

Atomic/kinetic closure and measured-constant uncertainty remain separate. This is passive scattering-out; source dynamics and photon redistribution are unchanged.

## 5. Corrected budget priorities

Shares of the new sufficient integrated bound: primary ionization daughters9.82997091%, Pstage1 omitted ionization17.13092077%, Pstage2 omitted ionization0.00088964%, Pstage2 omitted stopping16.33501245%, Sstage3 omitted stopping56.70320622%. These are error-budget shares, not measured physical error contributions. The old99.6864% is no longer used for current prioritization. A ratio against the invalid old radius is not presented as a validated speedup.

## 6. Actual checks and bounded evidence

Three cloud Wolfram evaluator calls returned17 certificate conditions,3 repair conditions and8 actual xAct groups. The xAct run had11zero tensor residuals, Wolfram15.0.1, xTensor1.3.0 and pure-Wolfram canonicalization. Official archive SHA2567a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be; xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36.

A Pstage1 source score was first transcribed slightly upward in distant digits. The first bound remained conservative, but CALL2 restored the exact original decimal. Its integrated-error and radius fractions agree exactly with source-derived Python. Pre-analysis undefined-symbol warnings were retained. A temporary Python denominator serialization failure was addressed with declared directed ratio rounding. No physical equation or tolerance was relaxed.

Sixteen same-author Fraction/Sympy checks verified source identity, active-path domain, closed projection, counterexample and corrected exact outputs. A portable recomputation subsequently reproduced all seven stored result fields from source scores. Neither procedure calls the source RHS or IVP. Online result files are normalized transcriptions; portable WL replay files reconstruct checked equations and were not separately executed as files. Independent scientific review is pending.

## 7. Evidence and next execution

Complete47-member artifact: `BASS_HE_THEORY16_R5_DONOR_REPAIR_EVIDENCE_20261014_v1.zip`,309958bytes, SHA256 `3c28e9de465de662ddd77b87387bf30b7a6440a67133e1fe70ee4eeb9e4a45bb`. Local CRC and all46manifest file identities verified. Full Korean proof, exact outputs, selected original source files and replay material are included; no source PDFs or font binaries are redistributed.

[Complete Drive evidence](https://drive.google.com/file/d/14xmoBCp5Lu1iHc5HiqyNjEQR3uyrbD9J/view). Backup acknowledgement and final provider details are in the adjacent evidence index.

Selected stage is R5 only. Original native HE endpoint/residual and RUX/all-Bianchi/D2.3 obligations retain their owners. Next execution may consume this corrected bound or continue the source-owner geometry/time binding; no new mandatory abstract gate is introduced. Other stages and global scientific promotion are unchanged.

References read at abstract/bibliography scope: Li and Rabitz, Chemical Engineering Science44(1989),1413–1430, DOI10.1016/0009-2509(89)85014-6; Le and Cambier, Physics of Plasmas24(2017)122105, arXiv1711.05946. SciSpace, Exa and primary publisher/preprint discovery were actually used. The closed-projection and phi integration proofs required here are supplied above rather than imported from an unread theorem.
