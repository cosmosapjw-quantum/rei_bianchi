# REI IGM | Original 26-event four-site photon source and implicit feedback, actual science report

## Original source and true execution

As of 2026-11-01, immutable parent PR #332 HEAD \`2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a\`, parent source tar SHA256 \`a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b\`, original accepted 46,080-node tick160 state SHA256 \`cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01\`. Preserved MPRK22(1)/Alexander SDIRK2, 26-event chemistry, 4 photon groups, original 3 source-owner species moments, positive nuclei and original proper clock. This experiment uses one original declared shape lane and one nuclei-conserving representative of the accepted tick160 marginal interval. It does **NOT** represent all possible globally correlated original parent states.

New source-authentic calculation in PR #337, repaired science HEAD \`194251f365a68e0ec1ad2c1afaf8341c8dda04bc\`: GitHub Actions \`41281584019\` SUCCESS, independent repository \`verify 41281583993\` SUCCESS. 9/9 normal and 9/9 Python -O tests PASS. Actual original source calls during full step, first half, second half are each exactly 4 sites (parent, predictor, gamma, final), all three original map runs certified. **12 actual source sites ×46,080 original cells = 552,960 source-conditioned new physical model rows**. 4 photon groups ×12 sites = **48 original group records**. No independent measured astronomical data, no 12 new IVPs and no new canonical DAG nodes.

### Scientific result

Original 26-event primary photoheating source at the first parent evaluation was \`8.227132749317620e37 erg/s\` across the 46,080 frozen model cells, corresponding to \`1.4894948981996285e-29 erg/H/s\` normalized to original H nuclei. The last source site (second half final) was \`8.243697202602081e37 erg/s\`, \`1.4924938371265245e-29 erg/H/s\`. This represents a **+0.20133932184132064% change in a stage-evaluated instantaneous source rate**, NOT time-integrated gas heating or an observed IGM thermal change. At the first site original per-node equal-node median photoheating was \`7.725779914613782e-30 erg/H/s\`; last site \`7.725905517899956e-30 erg/H/s\`.

At the initial source site: HI photoionization \`6.104263473411793e47 photons/s\`, HeI \`5.074367728430737e48 photons/s\`, HeII \`0 photons/s\`. At final site: HI \`6.100385665813920e47 photons/s\`, HeI \`5.094846478085250e48 photons/s\`, HeII \`0 photons/s\`. These rates are original source-conditioned evaluations, not observed photons. In all 48 group rows, the independently recomputed maximum photon-count normalization residual was \`1.5677139692516948e-16\`; the 3-moment group Jacobian identity \`J=diag(p)-p p^T\` had maximum algebraic residual 0.

Original point-parent full-minus-two-half maximum independent-output \`logT\` separation \`5.948382018061693e-7\`. The **historical original uncertain full-parent** cross-box separation \`2.1245050576368385e-4\` remains strictly above the unchanged local error gate \`2e-4\`. Width gate \`2e-3\` remains unchanged. There is NO original all-X shared-parent-and-source correlated derivative/remainder certificate, full first interval still BLOCKED at 160/131072 ticks, production HOLD.

### Mathematical result and correct scope

For each original photon group \(g\), the source-owner rates are
\[
r_{isg}=\frac{J_g C_{sg}n_{is}}{E_g+\sum_t C_{tg} S_t},\quad S_t=\sum_j n_{jt}.
\]
On any smooth fixed-forcing branch,
\[
\partial_{n_{jt}} r_{isg}
=\delta_{ij}\delta_{st}\frac{J_g C_{sg}}{D_g}
-r_{isg}\frac{C_{tg}}{D_g}.
\]
The second term is the nonlocal three-neutral-moment feedback, **not** the complete derivative under physically coupled source-parameter perturbations when local numerator changes. Across a single source evaluation, this nonlocal part factors through the three shared neutral totals. An implicit residual \(R(z,x,M(z))=0\) with no other cross-cell coupling at fixed \(M\) has \(R_z=A+B V^T\), with a three-dimensional conditional Schur complement \(K=I+V^TA^{-1}B\). A synthetic 20-dimensional, three-moment linear solve verified Woodbury against dense at maximum absolute \`4.163336342344337e-17\`. No entire multi-stage rank-three theorem or original stage-interval condition number was proved.

The original source share Hessian in log moments was also independently checked symbolically using Wolfram:
\[
H_{s,tu}=p_s[(\delta_{su}-p_u)(\delta_{st}-p_t)-p_t(\delta_{tu}-p_u)].
\]
At fixed forcing, positive moments and a smooth source branch, \(|H_{s,tu}|\le 2p_s\), so \(|R_s^{(2)}|\le p_{s,\max}(\sum_t|\Delta\log S_t|)^2\). This is a valid conditional **photon fraction** Taylor remainder, not a certified remainder for the full nonlinear original \`D_h(X,\Theta)\`. Further work must bound all original source/temperature/implicit-stage dependencies with shared parameters, and table-event branches.

### One-pass self-adversarial review

1. **Source owner and numerator:** the stored \`d_photo/d_lnS_den\` columns are *denominator-only* nonlocal feedback at fixed local population numerator. Using them as a full species derivative is a mathematical error. The direct same-node contribution must be included.
2. **Numerically unresolved photon channel:** 12 of 48 group rows have original current \`4.9406564584124654e-324 photons/s\` (smallest IEEE binary64 subnormal) in the fourth group. Apparent large absorber *fractions* for these essentially zero-current numerical enclosures are **not physically resolved photon absorption**. We preserve the raw values but exclude these 12 rows from interpretations of active photon groups. 36 group rows have non-subnormal current.
3. **Correlation:** original \`representative()\` enforces per-node H/He nuclei and interval membership; it does not prove compatibility with every global cross-site/source correlation of the historical true parent. Nor do point-site interval images prove the shared-source all-X \`D_h\` enclosure.
4. **Interpretation:** first/final stage source rates differ by 0.2013%; this is not total absorbed energy over the tick, cosmic heating history, a Bianchi directional signal or observational posterior.
5. **Execution history:** CI \`41281484405\` failed before physical evaluation on an interval-vs-array argument mismatch in the new helper call. Repair changed only the scoped caller while leaving original source code untouched. CI \`41281584019\` executed the real source calculation; original full-X scientific failure is retained.
6. **Independence:** native subagent NOT_RUN, distinct-author referee NOT_RUN. Mathematica, synthetic Schur, Python source tests and GitHub CI are separate checks but remain same-model/same-author science.

### Evidence and preservation

- GitHub Actions science \`41281584019\` (success), 9/9 normal + 9/9 optimized tests; source archive SHA lock and original stage map same-parent original physics.
- Actual binary Actions artifact #\`13073074438\`: 70,947,595 bytes, ZIP SHA256 \`41105018944d7b7bab3a7be84741cb47aeb3758aac1aff1fe44bb925fdb04d73\`; CRC PASS, 2 entries: full original stage CSV.gz and \`RESULT.json\`.
- New 552,960-row CSV.gz SHA256 \`acb3fa92d081aeb372ef5194b9c12a063604673916397c22fd26936072b4d0e2\`; counted every original node/site row, original \`T_K>0\`, source bounds and source group rates checked.
- Independent postprocessing produces sitewise table, 2 physical science PNG, numerical self-audit \`SCIENTIFIC_CROSSCHECK.json\` and an independently executable analysis code. These are distributed in the user's source-free science package and do not retroactively replace original source result.
- GitHub PR #337 source code, theory, tests, pipeline and 20-stage scope/progress ledger preserved. Git source publication, Actions data artifact and user-visible local download are distinct. **No verified Google Drive/Dropbox double binary backup**, and connected remote desktop \`cosmosapjw\` remains OFFLINE.
- Every stage references reported CENTRAL **28/88**, WORKING **33/88**, F4 FAST **4/7**, canonical delta **0**. Completion of a staged source science unit is **not** completion of the original 88-node central DAG.

### Next actual central physics step

Use these twelve original source-site derivative/energy records plus PR332's original three-species/four-group global photon susceptibility to construct an **actual entire-parent** \`D_h(X,\Theta)\` Jacobian with common source history and rigorously bounded second-order remainder, including nonlinear MPRK/SDIRK implicit population/thermal roots, four source evaluation sites and table-event logic. Only then reapply the *original* local error \`2e-4\` and width \`2e-3\` to one original [160,161] trial for all three lanes; never resume 131072 ticks or increment REI 28/88 based on point-source data alone. Source-matched B2D/REI-to-BASS observable work remains an independent authorised path if this blocker persists.
