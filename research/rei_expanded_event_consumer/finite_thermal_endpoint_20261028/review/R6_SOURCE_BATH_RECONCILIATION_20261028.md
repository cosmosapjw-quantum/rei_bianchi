# Finite thermal endpoint: source-bath reconciliation and weighted-heat composition

Date: 2026-10-28 KST. Unit: finite_thermal_endpoint_20261028.
Repository: cosmosapjw-quantum/rei_bianchi.
Base: 18e3bdfee44b7782d29179fa1cd9ddb873148e33.
Stage: R6 source-level review, SAME_CONTEXT; distinct-author verification remains pending.
Progress: R1-R5 5/10, C1-C4 design 4/10, combined 9/20. Original working 33/88 and central 28/88, increment 0. This report does not complete a new loop or implement code.

## 1. Result and the correction's scope

Direct inspection of the frozen BASS producer locates a concrete source-model caloric bath: its gas energy includes inert neutral helium as well as hydrogen nuclei and thermal electrons. Thus the broad statement that no source bath definition is available is too strong. What remains unbound is the complete numerical extraction/validation of that source-bath diagnostic and, separately, its identification with an actual REI recipient and a self-consistent thermal history.

The previous C2 document explicitly called its count an H contribution; it did not implement an H-only temperature denominator. This is a newly resolved source-to-consumer binding and a prospective misuse check, not an observed bug in executed consumer code. The general R5 algebra remains valid. Old source bytes, R1, R5, C1-C4, science results and receipts are not rewritten.

A second result separates the composition of unweighted event/work ports from that of expansion-weighted heat moments. The former retain the R01 factor in R5; the latter require R01^(5/3) for a constant-gamma monatomic gas when the second moment is per its own reference volume V1. These are different data types, not conflicting formulas.

## 2. Actual source evidence

All following BASS paths are under research/bass_b3h_qss_channel_completion_20261027/ at immutable commit 634c3046ffccc5d00f1ab7588b5834a6eb8053ad.

| File | Git blob | Directly read relevance |
|---|---|---|
| code/owners_b.py | cfe9a7c07f1e3d42c17f86a265cd5cfeffc080fd | Gas initial energy, inert-He owner, finite stocks/electrons, weighted moments, gas work and propagated endpoint |
| code/native.py | 98b581a592b86432807d5f79269caeaa4a974ba3 | Source temperatures are k_B T in eV; fHe from Y; populate sets xe=xHII in the selected H-only phase |
| code/phase_b.py | b954722915fe532211bce124ab1bf98cb95a2efb | Binds the Phase-A operands, source constants, fHe and original binary64-lift eV-to-J conversion |
| inputs/EARLIER_H_ONLY_PHASE_WITNESS.json | d18b22c1dd7cba3d636c0557c243fdd35f6201a9 | Source-model neutral-He phase witness; expressly not an empirical zero-helium-ionization result |
| results/SOURCE_OPERANDS.json | aef53bb4770fe9917c22f3cf22fa5edc7c5d75dc | Only first 105 lines fetched in this continuation; whole operand values were not newly extracted or evaluated |

The first three code files and phase witness were read, not imported or executed. The Phase-B program pins SOURCE_OPERANDS.json to SHA256 179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd and the native packet to c335e0273677a55a910b4ff67a1aa47a64834a19bf460b286bfe78404e9cf710. These are source-declared pins, not newly computed whole-file hashes.

The retained finite-result identity is blob a9ea559f123da6c8f1fe070139bc80145d4582fc, 3554206 bytes, SHA256 a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac. No full-result restoration, provider solve or original calculation was repeated.

Code facts: owners() constructs gas0 = (3/2)*NH*(1+fHe+xe)*Tm*EV, reports the thermal owner as gas/ions/electrons with inert source He, and returns electrons_initial/final separately. Native populate() sets xe=xHII=1-x1s. Phase B takes fHe from source_steady_temperature[0].fHe, the left op from endpoints[0], and EV from the preserved native incoming packet. The source's Tm variable is an energy in eV, not kelvin.

Primary literature support is limited and explicit: Ali-Haimoud and Hirata, HyRec, Phys. Rev. D83,043513 (2011), arXiv:1011.3758v2. Exa retrieved the original-paper Eq.(12) excerpt with the matter-temperature denominator 1+fHe+xe, and SciSpace located the journal record. The official arXiv abstract confirms the authors/version/journal; it does not itself expose Eq.(12). Full HTML retrieval through web failed, so no newly read full-paper or PDF claim is made. This literature supports the caloric counting convention, not this consumer's independent validation.

Primary record: https://arxiv.org/abs/1011.3758v2 ; DOI: 10.1103/PhysRevD.83.043513.

## 3. Source-bath count and representation residuals

Use the fixed reference V0 and the original R3 units: number per reference volume, energy per reference volume in SI, and c_v in J/K per particle. Write H_a = sum_i S_ai + e_a and H_b = sum_i S_bi + e_b, where i runs over ground/2s/2p/continuum and e_a,e_b are the separately saved thermal-electron endpoints. These H symbols are particle counts, not the Hubble rate.

Let B = NH*fHe be the source-model inert-He count per V0. The matched source-bath candidates are

N_a = H_a + B,       N_b = H_b + B.

For the declared inert-He transaction Delta B=0. The event increment remains Delta N=sum_i Delta S_i+Delta S_continuum for this selected H process. Retain the fine-stock sum even when it is a tiny nonzero saved residual. The endpoint count defect is

r_N = N_b-N_a-Delta N
    = sum_i(S_bi-S_ai-Delta S_i) + (e_b-e_a-Delta S_continuum).

Thus adding the same inert count does not erase the original fine-stock or electron defects. It changes the temperature denominator, not their diagnostic meaning.

The source driver uses N_a^drv=NH*(1+fHe+xe). Define eta_H=sum_i S_ai-NH and eta_e=e_a-NH*xe. Then N_a-N_a^drv=eta_H+eta_e. Do not silently impose either equality on independently saved decimal representations.

Let theta_a be the source Tm energy in eV and EV the source's declared J/eV factor. Define epsilon_a=theta_a*EV and T_a^E=epsilon_a/k_B^SI. With c_v=3*k_B^SI/2, and rho_U=U_a-(3/2)*N_a^drv*epsilon_a, the initial caloric residual is exactly

r_0 = U_a-c_v*N_a*T_a^E = rho_U-(3/2)*epsilon_a*(eta_H+eta_e).

This is an algebraic diagnostic, not a residual correction. If a different physical initial T_a is supplied, keep the original R5 definition r_0=U_a-c_v*N_a*T_a instead.

Although Delta B=0 along the selected event, parameter differentiation gives delta B=fHe*delta NH+NH*delta fHe. Omitting it in a composition/cosmological parameter JVP is not justified by inertness. Constants held fixed by a particular tangent contract must be stated.

For U>0, H>0 and B>=0, using the same full gas energy with an H-only denominator would yield

T_H/T_bath = [U/(c_v H)]/[U/(c_v(H+B))] = 1+B/H.

This proves the prospective positive bias for B>0. No numerical bias or actual endpoint temperature has been evaluated here. A dimensioned hand control H=2N_star, B=N_star/4 gives ratio9/8; it is a manufactured algebraic example, not the source helium abundance.

## 4. Source energy encoding and the three different temperatures

native.py reconstructs Tm_eV=kBoltz_src*Tm_K. With the source EV conversion,

T_a^E/Tm_K = kBoltz_src*EV/k_B^SI.

Even when this is close to one, its exact represented equality cannot be assumed. Preserve the original binary64 lift, stored decimal lexemes and any convention discrepancy. The already-SI Q, W and U must not be multiplied by EV a second time. The source helium mass ratio3.97153 is not a baryon-count multiplier for an unprovided native25 normalization.

Distinguish (a) the prescribed/source thermal driver used to build rates, (b) a finite source-model caloric endpoint reconstructed from saved energy and the complete source bath, and (c) a fully coupled physical REI recipient temperature. Identifying (a) with (b) would require a new consistency demonstration; identifying (b) with (c) needs actual recipient state/EOS/frame/normalization and feedback. This report identifies the construction of (b), without evaluating it or activating (c).

## 5. The source's weighted gas-energy route

owners_b.py has R=exp(3h), common-reference final gas energy U_b=exp(-2h)*(U_a+q2[1]), event gas energy Q=q[1], and gas work W=expm1(-2h)*U_a+exp(-2h)*q2[1]-q[1]. Define G=R^(-2/3) in the exact model and J2=q2[1]. The label J2 denotes the expansion-weighted gas energy moment, not Q squared.

Therefore

U_b=G*(U_a+J2),
W=(G-1)*U_a+G*J2-Q,
U_a+Q+W=G*(U_a+J2).

The last identity follows by cancellation of Q, not by a new solution of the history. For separately rounded saved fields, report U_b-U_a-Q-W and U_b-G*(U_a+J2) as representation/balance diagnostics. Do not redefine W from the left identity and then call the resulting zero an independent verification. Nor reconstruct G from U_b/(U_a+J2) for that purpose.

This confirms the original R5 instruction to apply the saved W once. Multiplying the final reconstructed temperature by G again double-counts the assigned expansion work. The source thermal driver remains prescribed in the rate construction; the displayed energy balance is not a proof of a newly self-consistent matter-temperature trajectory.

## 6. Local-volume composition of weighted moments: direct derivation

For a constant-gamma ideal gas, let alpha=gamma-1 and let J_gamma be the heat moment weighted by the local expansion ratio to power alpha. The segment endpoint form is U_1^(0)=R01^(-alpha)*(U_0+J01), with all terms per V0. At the next segment's reference V1=R01*V0, its initial energy is U_1^(1)=U_1^(0)/R01. Its local output is U_2^(1)=R12^(-alpha)*(U_1^(1)+J12).

Converting that output back to V0 gives

U_2^(0)=R01*U_2^(1)
       =R12^(-alpha)*[R01^(-alpha)*(U_0+J01)+R01*J12]
       =(R01*R12)^(-alpha)*[U_0+J01+R01^gamma*J12].

Hence J02=J01+R01^gamma*J12. For the selected monatomic gas gamma=5/3, the multiplier is R01^(5/3). If J12 was already expressed per V0 rather than V1, only R01^(gamma-1) remains. The reference-volume metadata decides which formula applies.

Meanwhile the unweighted ports obey the unchanged R5 laws Q02=Q01+R01*Q12 and W02=W01+R01*W12. Weighted and unweighted coordinates must not be mixed in a common field. Three-segment associativity follows from R02=R01*R12 and R02^gamma=R01^gamma*R12^gamma for positive ratios.

At fixed gamma, the weighted tangent is

delta J02=delta J01+gamma*R01^(gamma-1)*J12*delta R01+R01^gamma*delta J12.

If gamma itself is varied, also retain R01^gamma*log(R01)*J12*delta gamma; this is outside the present fixed-gamma rational-core scope. State-dependent gamma needs another evolution law and is not covered by this composition theorem.

A dimensioned hand control takes R01=8, R12=1, U0=E_star>0, J01=0 and J12=E_star per V1. Direct segment propagation gives U2^(0)=E_star/4+8E_star=33E_star/4. Correct weighted composition gives the same value because 8^(5/3)=32. Replacing32 by the unweighted factor8 would give9E_star/4. This is hand algebra, not an executed test, and no physical source value is inferred from it.

The exact-Fraction core is still the unweighted U/Q/W route. Generic rational R need not have rational R^(1/3), so do not add a fractional-power function and advertise it as exact Fraction arithmetic. A later optional weighted diagnostic must consume source-supplied weights or an appropriate algebraic/numerical representation with explicit errors. It must preserve any saved G^3*R^2-1 representation residual.

## 7. Additive implementation binding, not an implementation claim

| Existing design surface | Required binding now identified |
|---|---|
| selected_h_thermal_count | Remains an H contribution; never silently returns the complete source bath |
| source-bath adapter | Read NH from the same source clock/tube, fHe from the pinned Phase-A left steady-temperature record, and separately saved electrons; add B to both endpoints |
| finite_endpoint / saved_endpoint_diagnostics | Consume one complete, declared bath and matching gas U/Q/W; retain rho_U, eta_H, eta_e and r0 separately when available |
| endpoint_jvp | Include the inert-He parameter direction delta B when its parameters vary |
| compose_local_segments | Keep the R01 multiplier for unweighted count/Q/W; do not feed J2 into these fields |
| optional weighted diagnostic | Apply the distinct source-bound G/J2 convention; no generic Fraction fractional powers |
| physical output fields | Leave actual native25, target temperature, physical radii and full_state_update unactivated |

These requirements refine existing acceptance cases for count ownership, normalization, residuals and two-segment composition. They do not require another broad test framework or changes to the original provider. No finite_thermal.py, tests or runner were authored in this continuation.

## 8. Single-pass scientific review and admission

The positive-domain R5 caloric map, discrepancy identity, JVP, box enclosure, affine-polytope argument and local-volume unweighted composition survive this same-context source review. The identified corrections concern the source bath and data representation, not their general algebra. Formal physical admission, independent R6 and C9 remain pending.

Finding SB1: source bath includes inert He. Impact: using partial H count with full gas energy gives an incorrect temperature. Smallest correction: explicit source-bath addition B and its tangent. Status: source definition located; adapter implementation/evaluation pending.
Finding SB2: source Tm is energy, not kelvin; EV and kBoltz have retained source conventions. Impact: silent unit/constant substitution. Smallest correction: explicit energy-to-K bridge and convention residual. Status: formula derived; no new numerical evaluation.
Finding SB3: J2 is weighted heat. Impact: R01-only composition of local J2 is wrong. Smallest correction: typed weighted/unweighted inputs with the proved R01^(5/3) law. Status: derived; future targeted control specified.

No observed numerical consumer failure, new global no-go, new independent proof admission, native25 activation or physical error certificate is claimed. A plot would require an authorized new calculation/rendering; none is manufactured from the hand controls.

## 9. Current survey coverage and provenance limits

The prior all-name census1417 across seven repositories is reused as historical evidence, not a fresh complete census. This continuation searched branch names containing20261028 in all seven repositories and followed returned cursors to terminal: REI0, BASS4, HE2, CR2, REC2, WU0, VigilODE0. This filtered10-name result misses updates on older-named branches and is not account-wide completeness. Selected actual refs and source files were read independently of the search index.

New BASS restart branch HEAD4d6e166cf9a644392a8a2b68c4c171a1fb658240 has an owner handoff for PR212: scienceb8bd56bd5e54354dbe2a6617da33ec076467fe4e,18/20, distinct-author R6/C9 pending. Its saved-panel/restart results are owner evidence and are not new runs or independent validation of this unit. Its math is a compatible future comparison, not a replacement of the frozen BASS205 input.

The new-named CR he-event-union branch still pointed to65e20e40e3c1d9e8384101017dc8940b3d09de09 at read time, the already known parent-event checkpoint. A new branch name alone establishes no new He event closure. Current central ref was22a99cb9b1691274e74c122d54521be4f2f51ba5. Its count28/88 is corroborated by the contemporaneous BASS handoff; a fresh complete central-DAG recomputation was not performed. Working33/88 remains the inherited unmodified local count.

The broad indexed commit search returned only older default-branch material despite newer direct refs; it was not used as evidence that no new work exists. An initial page_size500 branch request was rejected and replaced by valid size100 requests; this is an API-argument error, not a scientific or runtime failure.

Personal-context retrieval returned no matching conversation approval or completed review for this exact unit; older unrelated logs and indexed stale summaries were not imported as current status. This is not an exhaustive export of all private chats. Drive scoped name search returned six Markdown checkpoints; Dropbox scoped search reached has_more=false with seven including the R1 JSON. The existing R5 backup IDs were freshly resolved at10919bytes on both providers. No existing archive or stage backup was rebuilt or downloaded whole. All-account backup contents were not exhaustively inspected.

## 10. Execution and resource boundary

Native subagent execution: NOT_RUN. Distinct-author review: NOT_RUN. New scientific computation, scientific tests, CAS evaluator, provider/IVP solve, plot, source restoration and ZIP/CRC/archive-SHA execution:0. The metadata-only Python probe actually succeeded in this turn (PYTHON_PASS, Python3.13.5); this is not a science test. C++ was not probed and no unavailability claim is made.

The probe's external coarse timing output was real1.03s/user0.97s/system0.40s. Preserve it as displayed metadata-process accounting, not an exact whole-turn total. Raw-document writes and identity checks are also actual nonzero work; their separately observed counters and unknown tails belong in the closing receipt. Remote/model/network costs remain unmeasured. Historical planning15.929490885 and presentation lower48.263016494 are not silently reset or represented as current exact totals.

The last explicit caps16/47 and original baselines10/30 remain unchanged. Research cap20/reserve3 and ZIP cap60/reserve8 remain unapproved. Main595.225063/600 NO_MORE_IVPs and all foreign-owner allocations are preserved. No executable helper is used to evade these boundaries.

Next substantive step is a distinct-author read of the R5 derivation plus these three source bindings, followed by the same-unit implementation and a single newly authorized bounded test. Repeating the branch census or packaging the old116-file bundle is not a prerequisite. This report is useful partial progress, not completion of the requested full theory/coding loops.
