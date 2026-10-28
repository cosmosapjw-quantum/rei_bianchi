# Phase 1 independent review before preserved test and execution evidence

## Identity, scope, and freeze

- Project: `cosmosapjw-quantum/rei_bianchi`.
- Unit: `finite_thermal_endpoint_20261028`.
- Branch supplied to this reviewer: `research/rei-causal-prefix-consumer-20261027`.
- Review pin supplied to this reviewer: `b77c7b8d45c48a7e4722e733309430d5ba668b0d`.
- Frozen producer: `cosmosapjw-quantum/bass` at `634c3046ffccc5d00f1ab7588b5834a6eb8053ad`.
- Selected stages: R6 independent theory verification and C9 independent code/numerics review, Phase 1 only. `AUTO_NEXT_NODE=false`.
- Date in the supplied environment: 2026-10-28 UTC.
- This document fixes the judgment formed before disclosure of the preserved tests, execution logs, and C6–C8 numerical results. A later comparison must be a separate document; this document is not to be revised to match later evidence.

**Provisional outcome:** the finite caloric map, saved-residual transport, tangent, fixed-heat-capacity interval enclosure, and reference-volume composition are supported by the independent derivations below. Static inspection found no demonstrated algorithmic defect in `finite_thermal.py` on the declared domain. One displayed source-temperature identity needs a narrow exact-representation correction, identified as F1. The implementation already retains the missing representation residual. C9 execution/test-oracle admission remains pending the deliberately withheld evidence.

The actual REI recipient temperature, native25 state, physical error radii, and full state activation are outside the supplied claim and remain null/inactive. Their absence is not a negative review finding.

## 1. What independence and execution identity are actually observable

The message envelope identifies this task as `/root/finite_thermal_blind_reviewer`, with `/root` as its parent. The assignment says the launch used `fork_turns=none`; the advertised collaboration-tool contract says that mode excludes surrounding parent conversation. I did not see the parent's actual spawn call and do not claim independent verification of its hidden parameters. My visible context contains system/developer instructions, the environment context, this task assignment, my own review work, and two subsequent parent housekeeping messages. Those messages acknowledged embedded-source exposure and instructed me to finish Phase 1 before Phase 2 disclosure. Neither supplied a desired scientific verdict.

No earlier parent dialogue, controller review, operational handoff, or Phase 2 outcome was visible or sought. The required packet nevertheless contains embedded historical source status phrases, source completion counts, and old check counts; the exact exposure is recorded in section 8. Consequently this is an independent pre-evidence review with a restricted reading scope, **not a fully isolated blind audit**.

The host filesystem is shared. I confined substantive reads to the named initial-packet files and the selected skill's policy references. Shared access is not filesystem isolation, and I cannot prove that no other agent could access or change these locations. The local full-file Git blob checks below confirm the inspected complete copies against the supplied manifest at the time of inspection; they are not an independent verification of the remote repository history.

Requested role: native independent scientific reviewer, with Astra-tier review specified by the supplied repository policy. The developer instruction labels the assistant “ChatGPT, GPT-6 Astra Pro.” That is an instruction-level model label. No tool result exposed a separate runtime model identifier, backend identifier, or opaque agent UUID. The launch message does not expose an explicit model override or prove which model was inherited. Requested/declared role, instruction-level label, and independently observed runtime identity must therefore remain separate. The producer's `requested_model='gpt-6.1-sol', observed_runtime_model=None` is metadata in producer source, not metadata for this reviewer.

This review was performed by this native agent through source reading and written derivations. No subordinate reviewer, Python scientific subprocess, CAS, numerical evaluator, or parent-authored judgment substituted for the review. I did not import or execute any scientific module, test, source provider, or runner. Tools were used for text reads, line numbering, line counts, read-only Git blob calculation, and writing this report.

## 2. Governing contract and interpretation

I applied the supplied `policy/AGENTS.md` and physmath-research-loop 1.0.0, especially R6/C9 and its RESEARCH_POLICY and EVIDENCE_AND_HANDOFF references. No new physical assumptions or acceptance tolerances were introduced. No security, isolation, or broad provenance infrastructure is required for the scientific claim.

The object is an exact algebraic map of represented inputs. The common reference volume is fixed at V0; N is translational thermal-particle count per V0, and U, Q, W are SI gas energy per V0. The heat capacity cv is constant within each transaction and positive. The declared domain is Na, Ta, cv, D=Na+dN, E=cv Na Ta+Q+W > 0. The saved comparison additionally requires Nb, Ub > 0. Parameter variation of cv is allowed across a differentiable family. It is not unmodelled time variation inside a transaction.

The positive input domain, the already integrated work port, the stated single-temperature bath, and the distinction between model diagnostics and a coupled REI temperature are substantive premises. I did not test stronger assertions such as unknown-history integration, arbitrary EOS completion, general correlated-set sharpness, or a physical error certificate.

In source citations below, local extract lines map to the original paths through MANIFEST.json. R3 and R5 local line k maps to original line k+4; SOURCE_BATH_BODY local line k maps to original line k+16. Complete implementation and producer copies retain their original line numbers.

## 3. Independent R6 derivations and confirmed arguments

### 3.1 Finite endpoint, sign, and logarithmic arguments

Put A=Q+W. The declared gas balance is E=cv Na Ta+A and the declared final count is D=Na+dN. Solving the final caloric relation cv D T=E gives the unique positive endpoint

\[
\widehat T=\frac{E}{c_vD},\qquad
\widehat T-T_a=\frac{A-c_vT_a\,dN}{c_vD}.
\]

The denominator is positive, so the latter numerator determines heating or cooling. The statement that positive gas heat alone does not determine the temperature sign follows directly: in consistent fixture units, Na=Ta=cv=1, dN=2, Q=1, W=0 gives D=3, E=2 and That=2/3 despite Q>0. This is a hand counterexample to a possible stronger heat-sign inference, not to the stated theorem.

Dividing by Ta gives the factorization

\[
\frac{\widehat T}{T_a}
=\frac{E/(c_vN_aT_a)}{D/N_a}.
\]

Both factors are positive and dimensionless on the domain, which justifies the difference of logarithms. The implementation correctly returns their exact rational arguments rather than claiming an exact rational logarithm. The coefficient cv has J/K per particle units; E/(cv D) therefore has temperature units.

Confirmed source: R5 original lines 5–23 (local 1–19); implementation `Endpoint` and `finite_endpoint`, lines 71–113. The zero-port limit dN=Q=W=0 returns Ta. No factor 1/H or additional adiabatic multiplier appears in this balance.

### 3.2 Saved endpoints and the complete residual

I derived the residual relation by introducing dimensionless discrepancies x=rE/E and y=rN/D. The definitions imply

\[
\frac{T_b}{\widehat T}=\frac{1+x}{1+y},\qquad
T_b-\widehat T
=\widehat T\frac{x-y}{1+y}
=\frac{r_ED-Er_N}{c_vD(D+r_N)}.
\]

This establishes the identity without either residual vanishing. The decomposition also follows exactly:

\[
(U_a-c_vN_aT_a)+(U_b-U_a-Q-W)=U_b-E.
\]

Thus an initial mismatch belongs in rE once. Using only the interval balance residual would remove it; adding it again to rE would duplicate it. Nonzero residuals can cancel in the temperature when rE/E=rN/D, so a temperature agreement does not imply separately conserved count and energy. The code returns both the temperature difference and the common-denominator identity, while retaining r0, r_balance, rE, and rN.

Confirmed source: R3 original lines 15–26; R5 original lines 25–39; `saved_endpoint_diagnostics`, implementation lines 130–139. Ua is treated as a separately saved diagnostic input, as specified. The function's Endpoint argument places the ideal comparison inside the declared positive D,E domain; I do not infer a promise to evaluate that comparison outside it.

### 3.3 Count ownership and the source bath

For four fine H stocks (ground, 2s, 2p, continuum), each stock contributes one heavy translational particle and each separately saved thermal electron contributes one particle. The selected H event projection is therefore

\[
dN_H=dg+ds+dp+dc+dc=\sum_i dS_i+dc.
\]

The reduction to dc requires the fine-stock sum to vanish exactly. Keeping that sum is necessary for represented source data. The code does so.

For inert source helium B=NH fHe, the endpoint bath counts are Na=Ha+B and Nb=Hb+B. Direct subtraction gives

\[
r_N=\sum_i(S_{bi}-S_{ai}-dS_i)+(e_b-e_a-dS_c),
\]

so adding the same inert helium count does not erase any retained stock/electron discrepancy. At a fixed event B has no increment; across a parameter family its variation is fHe dNH+NH dfHe. `source_bath_counts_jvp` includes this term.

With driver count Nd=NH(1+fHe+xe), eta_H=sum(Sai)-NH and eta_e=ea-NH xe, Na-Nd=eta_H+eta_e. For epsilon=theta EV, TaE=epsilon/kB_SI and cv=3 kB_SI/2, independent substitution yields

\[
r_0=U_a-\tfrac32N_a\epsilon
=\rho_U-\tfrac32\epsilon(\eta_H+\eta_e),
\quad \rho_U=U_a-\tfrac32N_d\epsilon.
\]

This is exactly the returned `r0_decomposition`. It needs neither the saved stock assembly to equal the driver count nor the saved source energy to equal an unrounded model product. For a positive gas energy and H>0, the prospective denominator bias TH/Tbath=(H+B)/H follows algebraically. It does not evaluate an actual REI temperature.

The producer binding is traceable: `owners_b.py` lines 45–46 assemble fine stocks, line 86 constructs gas0 from NH(1+fHe+xe) Tm EV, lines 110–122 expose separately saved electrons and the declared thermal owner; `native.py` lines 102–112 define fHe, the source temperature calculation, and xe=xHII in the selected model. `phase_b.py` lines 41–47 binds the left operands, fHe, EV, and Clock. Consumer implementation lines 265–314, 425–446, and 455–456 match this ownership and the intended residual preservation.

The earlier phase witness is a source-model convention witness. I did not independently establish the historical source evolution from its unprovided archive or original C code, and I did not reinterpret it as empirical evidence of exactly neutral helium.

### 3.4 Tangents and representation invariance

For a differentiable positive family, differentiating the defining caloric equation yields

\[
c_vD\,\delta\widehat T+D\widehat T\,\delta c_v
+c_v\widehat T\,\delta D=\delta E,
\]

where

\[
\delta D=\delta N_a+\delta(dN),\qquad
\delta E=c_vT_a\delta N_a+c_vN_a\delta T_a
+N_aT_a\delta c_v+\delta Q+\delta W.
\]

Solving gives deltaT/That=deltaE/E-deltacv/cv-deltaD/D. This independently verifies `endpoint_jvp`, including its cv term. In the zero-port family with those ports fixed at zero, the Na and cv variations cancel and deltaT=deltaTa, as required.

For proper coordinates u=E/R and n=D/R, direct differentiation gives deltau/u=deltaE/E-deltaR/R and deltan/n=deltaD/D-deltaR/R. If both are divided by the same positive b, the additional -deltab/b term also cancels in the temperature ratio. These cancellations do not remove those terms from the individual coordinates, and the code retains them in both coordinate JVP functions.

Confirmed source: R5 original lines 47–67; implementation `endpoint_jvp`, lines 150–155, and coordinate functions, lines 164–186. A saved-route tangent must similarly retain the variations of Ub and Nb, including any varying residuals. I do not interpret the event-input JVP as a separately supplied automatic differentiation implementation for every saved-source field.

### 3.5 Error bound, interval image, and conditioning

From the residual identity, |rE|<=eE and |rN|<=eN<D give

\[
|T_b-\widehat T|
\le\frac{e_ED+Ee_N}{c_vD(D-e_N)}.
\]

The derivation uses only the triangle inequality and the positive denominator margin. No lower bound E-eE>0 is needed for this absolute-error expression itself, although saved Tb is still taken on its positive domain. In contrast, the advertised positive rectangular image requires E-eE>0. The distinction is reflected by `temperature_error_bound` versus `endpoint_interval`, which delegates its endpoints to positivity checks.

For U,N>0 and fixed cv, T increases with U and decreases with N. Therefore the full box maps to

\[
\left[\frac{U_{lo}}{c_vN_{hi}},\frac{U_{hi}}{c_vN_{lo}}\right].
\]

Every correlated subset of that box is enclosed without a probabilistic independence assumption. Endpoint attainability is a separate question. On an affine polytope with positive denominators throughout, write z=sum lambda_i vi; then weights wi=lambda_i D(vi)/D(z) are nonnegative and sum to one. The quotient at z is the weighted average of the vertex quotients. This proves the stated vertex-extremum result on that positive domain. The text does not authorize applying this argument to a polytope crossing D=0.

The bound's divergence as D-eN tends to zero and the logarithmic derivative's singularity as E tends to zero are real conditioning limits. The module checks nonnegative radii and the strict count margin, leaves missing radii as None, and rejects a positive-box call if its lower energy endpoint is nonpositive. It does not turn an observed balance residual into a physical uncertainty radius.

Confirmed source: R5 original lines 69–85; implementation lines 189–226. These are conditional enclosures; no physical radii are supplied by the contract.

### 3.6 Composition and geometry work

I derived the conversion from extensive quantities: a local count density dN12 per V1 represents V1 dN12 particles; division by V0 multiplies it by R01=V1/V0. The same derivation applies to each already integrated energy port. Thus

\[
(R,a)\circ(S,b)=(RS,a+Rb),
\]

where a,b may be count, heat, or work increments. Three-segment composition produces a+Rb+RS c on either association. Differentiating a+Rb gives deltaa+deltaR b+R deltab. These are the implemented segment map and JVP, with the second initial state also converted to its local reference in the theorem.

For an ideal gas with alpha=gamma-1, direct integration of dU/dR=-alpha U/R gives U_b=U_a R^(-alpha) and W=U_a(R^(-alpha)-1) when Q=0. The temperature map then gives the correct adiabatic temperature once. Merely changing representation volume with W=0 instead dilutes both proper densities without changing their ratio. These are different premises and both statements are valid.

For weighted heat moments, the second local-reference endpoint is

\[
U_2^{(0)}=R_{12}^{-\alpha}
\left[R_{01}^{-\alpha}(U_0+J_{01})+R_{01}J_{12}\right].
\]

Factoring (R01 R12)^(-alpha) gives J02=J01+R01^(alpha+1) J12=J01+R01^gamma J12. This is not the unweighted-port composition law. The fixed-gamma derivative follows by differentiating that power. The implementation correctly leaves these generic fractional powers outside its rational core and labels its composition inputs as unweighted.

The producer gas energy and work formulas in `owners_b.py` lines 91–99 imply, in the unrounded model, Ub=G(Ua+J2), W=(G-1)Ua+G J2-Q with G=exp(-2h). Their sum is Ua+Q+W=G(Ua+J2). Independently rounded saved fields can have nonzero residuals, and the consumer does not recompute W to force that identity to zero.

Confirmed source: R5 original lines 87–111; SOURCE_BATH original lines 80–116; implementation lines 229–262 and 431–461. No claim of a generic exact-Fraction fractional-power solver is made.

### 3.7 General caloric EOS theorem

For continuous F on a positive bracket and F_T>=m>0, the endpoint values bracket U and the intermediate-value theorem gives existence. The positive derivative gives strict monotonicity and uniqueness. For two solutions at the same z, the mean-value theorem gives |deltaT|<=|deltaU|/m. Differentiating F(T,z)=U on a differentiable branch gives deltaT=(deltaU-F_z delta z)/F_T.

These conclusions have exactly the stated fixed-z or differentiable-branch scope. They do not supply an EOS, a bracket, or an uncertainty bound. No general EOS solver is promised or implemented. Confirmed source: R5 original lines 113–121, local 109–117.

## 4. Findings: proven issue, conditional concerns, and missing evidence

### F1 — A displayed source-temperature ratio omits a nonzero representation term

**Class:** proven local mathematical/representation issue in the written source-bath identity. **Severity:** low for the main caloric algorithm; material to the exactness of the single displayed source-binding equation. **Current-task relevance:** correct or narrow that equation before treating every displayed source-binding equality as exact on the declared frozen encodings. It does not invalidate the R5 endpoint map, the error/tangent theorems, or the inspected adapter implementation.

**Original location:** `research/rei_expanded_event_consumer/finite_thermal_endpoint_20261028/review/R6_SOURCE_BATH_RECONCILIATION_20261028.md`, original lines 72–76, especially line 74; packet `theory/SOURCE_BATH_BODY.md` local lines 56–60. Related inputs: literal binding original lines 22–25. Producer operation: `research/bass_b3h_qss_channel_completion_20261027/code/native.py`, lines 102–109. Correctly retained implementation diagnostic: `source_temperature_bridge`, `finite_thermal.py` lines 384–388.

The displayed identity is

\[
T_a^E/T_{m,K}=k_{Boltz,src}\,EV/k_B^{SI}.
\]

Under the packet's encoding contract, theta, k=kBoltz_source, and t=Tm_K are separately decoded binary64 values. The producer multiplication creates a rounded binary64 theta; it is not exact multiplication of the subsequently lifted rational operands. Define rho_theta=theta-k t. Then the exact represented-input identity is

\[
\boxed{\frac{T_a^E}{t}
=\frac{k\,EV}{k_B^{SI}}
+\frac{\rho_\theta\,EV}{k_B^{SI}\,t}.}
\]

The original equation requires rho_theta=0. That condition does not hold for the actual displayed binary64 operands. This can be proved without running the decoder, evaluating a temperature, or using a CAS:

1. The decimal lexeme for k is 8.617343e-05=8617343/10^11. It lies in the binary64 exponent bin with spacing 2^-66. Hand integer multiplication gives

   8617343 * 2^66 / 10^11 = 6358476836654899.54605105152.

   Therefore its nearest binary64 significand is 6358476836654900, and the exactly lifted k is 1589619209163725/2^64, whose numerator is odd.

2. The decoded t from 3003.7478329491555 lies strictly between 3003 and 3004. Its binary64 exponent bin is [2048,4096), so t=M/2^41 for an integer M.

3. The decoded theta from 0.25884325362029575 lies in [1/4,1/2), so theta=P/2^54 for an integer P.

4. If theta=k t, the odd numerator of k would force M to be divisible by 2^51. Then t=M/2^41 would be an integer multiple of 1024. No such value lies between 3003 and 3004. Hence rho_theta is nonzero for the declared fields.

This proof only establishes a nonzero represented multiplication residual; it does not evaluate its sign or magnitude, a source endpoint temperature, or a physical discrepancy. The adjacent source warning about exact represented equality is sensible, but the displayed equality still needs its missing term or an explicit unrounded-model premise.

**Minimal repair:** replace that displayed equation with the boxed identity and define rho_theta, or label the existing equation as the unrounded model relation conditional on theta=k t. The adapter already returns `theta_minus_kBoltz_native_eV`, `energy_temperature_K`, `energy_minus_native_K`, and `kBoltz_EV_over_kB_SI` separately. No production-code change or producer replay is needed to correct this documentation issue. A later evidence comparison should distinguish any demonstrated nonzero rho_theta from the unrelated physical feedback question.

### Conditional concerns

No additional demonstrated defect is reported. The positive-domain, fixed-cv, same-normalization, and same-interface-state conditions are already stated; treating their absence in a different application as a defect in this scoped theorem would change the reviewed claim.

For a future use of the saved-source path, accurate transcription of the eleven literal records and correct association with the frozen source are prerequisites. The declared byte pins and static decoding path are consistent, but this phase did not independently read those fields from their original full JSON objects. This remains an evidence dependency, not an allegation that the supplied transcription is wrong.

The resource wrapper is an operational single-worker guard and explicitly requires external whole-command accounting. I did not infer adversarial isolation, total descendant-process accounting, or scientific validity from it. Those stronger properties are outside its stated purpose and are not added as review blockers.

### Missing evidence deliberately reserved for Phase 2

1. **Preserved test source and independent expected values.** `test_finite_thermal.py` is referenced by the runner but was not disclosed or read. The exact acceptance contract requires independent expected or cross-multiplied identities. Static agreement between implementation and theorem does not establish that the tests meet this criterion. The next read should inspect the actual preserved tests, without rerunning them.
2. **Raw execution results and their scope.** No preserved stdout, stderr, exit status, authorization record, or C6–C8 numerical result was read in this phase. Test outcomes, numerical examples actually executed, and runner accounting therefore remain unadjudicated. The next dependency is the promised preserved evidence, not a new numerical campaign.
3. **Actual source readback and complete-source evaluation claims.** The packet includes producer code and transcribed source lexemes, but not the full 3,554,206-byte finite result or the complete 8,281-byte literal binding. I inspected the consumer's pins and decoder logic; I did not independently verify the full source bytes or evaluate `consume_saved_source`. Any later assertion that the actual frozen source was consumed must point to preserved matching-input execution evidence. Certification of the eleven transcribed fields needs source-linked readback evidence at their named pointers; a new broad provider/source census is not required.
4. **Original HyRec/archive provenance beyond the supplied source.** The source-bath extract cites a paper and the witness cites native C routines and archived CSV metadata. Those originals were not read. The conditional caloric algebra and adapter review do not depend on newly verifying the historical paper retrieval or on rerunning the source solver.

These dependencies are intentionally distinct from physical REI state, general-EOS parameters, and physical radii, which the present task explicitly does not provide or request.

## 5. Independent static C9 assessment

### Equation-to-code correspondence

| Surface | Inspected code | Static conclusion on the stated domain |
|---|---|---|
| Exact scalar inputs | `finite_thermal.py` 38–68 | Explicit Fraction or decimal/rational string path; accidental floats, bools, and ints are rejected in the core. |
| Finite endpoint and log arguments | 71–113 | Positive Na, Ta, cv, D, E enforced; correct exact rational quantities. |
| Saved residuals | 130–139 | r0 and balance split sum to the aggregate residual; no clipping or repair. |
| Endpoint/coordinate tangents | 150–186 | Product and quotient terms, cv direction, volume direction, and normalization direction agree with the derivation. |
| Bounds and intervals | 189–226 | Domain margins and positivity are checked in the appropriate routines; missing physical radii stay absent. |
| Local segment composition | 229–262 | Correct local-reference multiplier and product-rule terms. |
| H and complete source-bath count | 265–314 | Fine-stock residuals, saved electrons, inert He, and parameter He direction retained. |
| Gas sector extraction | 317–320, 431–435 | Exact five-sector order checked; gas uses index 2, matching producer output. |
| Typed source decoders | 323–347 | JSON noninteger numbers pass through binary64 before Fraction; hex passes through `float.fromhex`; saved MP strings retain decimal meaning. |
| Input identity | 350–371, 417–424 | Raw size/SHA/Git-blob binding and declared source/schema/order checks are present. Full source input was not available here to exercise them. |
| Source temperature and decomposition | 384–388, 438–456 | Energy/Kelvin conventions are separated; the representation residual missing from F1's printed equation is retained by code. |
| Proper source energy | 436–437, 460–461 | A saved common-volume/proper-volume discrepancy is reported instead of overwritten. |
| Serialization and activation boundary | 403–407, 447–487 | Fractions serialize as numerator/denominator strings. No physical client activation is present in this module. |

The producer decoder path confirms why direct decimal parsing would be wrong for the declared JSON numeric fields: `phase_b.load` returns `json.loads` values (lines 18–21); the relevant fields flow through `mp_b.exact` or mpf on those floats (`phase_b.py` 41–43, `finite_b.py` 8–9, `mp_b.py` 13–17). By contrast, `mp_b.plain` uses `mp.nstr(v,70)` for saved mpf outputs (lines 18–23), matching the consumer's decimal-string semantics. Exact rational operations on these represented values do not claim equality with unprinted MP internals. I found no decoder path that applies EV a second time to the saved SI Q/W/U fields.

### Independent hand controls fixed before seeing tests

These controls were derived on paper during this phase, not executed. All values use a consistent manufactured unit convention and are not physical source inputs.

For cv=2, Na=3, Ta=5, dN=1, Q=7, W=-3:

- D=4, E=34, That=17/4.
- Log-energy argument=17/15, log-count argument=4/3, temperature ratio=17/20.
- Direction (dNa,dTa,dcv,ddN,dQ,dW)=(1,2,3,-2,5,-7) gives dD=-1, dE=65, dlogT=45/68, dT=45/16.
- Saved Ua=31, Ub=35, Nb=5 gives r0=1, r_balance=0, rE=1, rN=1, Tb=7/2, and Tb-That=-3/4. The common-denominator expression is (4-34)/(2*4*5)=-3/4.
- Supplied eE=eN=1 gives the box [33/10,35/6] and error bound 19/12. The upper corner attains That+19/12. These numbers also distinguish a count-denominator error from an energy-only perturbation.

For two unweighted segments a=(R,count,heat,work)=(2,1,3,-1) and b=(3,4,5,-2), composition is (6,9,13,-5). This tests actual local-reference conversion rather than adding increments from different reference volumes unchanged.

These provide prior independent targets for Phase 2 comparison. Their absence from the preserved suite would not by itself be a defect if equivalent independent coverage is present.

### Runner review

I inspected all 282 lines of `run_once.py`. The wrapper separates an explicitly authorized tests mode from source mode, pins the implementation/test/runner hashes in the authorization comparison, marks one use before worker launch, and records observed worker termination and accounting separately from scientific admission. Its success string is expressly `EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION`. `classify_outcome` distinguishes unobserved terminal usage and ambiguous signals instead of treating them as proven science failure or inventing a signal sender. The final record expressly leaves exact whole-command CPU unmeasured and requires external accounting.

No observed execution is inferred from this source. I found no concrete wrapper defect affecting the algebraic claim by static inspection. Whether the preserved invocation obeyed its authorization, returned the expected source/test output, and met the actual accounting boundary remains a Phase 2 evidence question.

## 6. Separate provisional stage assessments

### R6

**Assessment:** `pass_scoped` for the independently derived R5 caloric endpoint, residual, tangent, enclosure, composition, and bracketed-EOS statements on their stated domain. The source-bath count/work construction is also supported as a conditional construction. **Localized correction remains:** F1 prevents admitting the source-temperature ratio in SOURCE_BATH original line 74 as an exact equality of the declared represented operands. Replace that identity or state its unrounded-model premise. The correction does not require weakening or withholding the valid core theorems.

No new strong physical no-go claim is proposed. F1 is a local refutation of one represented-input equality, not a literature novelty or a global physical impossibility result. The skill's NG1–NG7 research-result admission process is therefore not used to inflate this correction into a new no-go result.

### C9

**Assessment:** `partial` overall at this pre-evidence stage. Static code/theory correspondence is supported and no demonstrated production-code defect was found. The exact source-temperature residual is already implemented, so F1 is not presently a code repair request. Independent test-oracle quality, actual execution results, numeric source readback, and preserved C6–C8 conclusions remain to be reviewed. A count of passing checks or an exit-zero status alone would not discharge those obligations.

Phase 1 is complete when this immutable report is returned. The next authorized review step is disclosure and inspection of the promised preserved evidence, compared explicitly with this initial judgment. No fresh solve, suite rerun, CAS run, source/provider replay, or production edit is requested by this report.

## 7. Read ledger and identity checks

All paths in this table are relative to `/workspace/scratch/cc0531120bc9/finite_thermal_native_review/initial/`. “Original” means the source range declared in MANIFEST.json. I read every local line shown. The manifest's end ranges for the three excerpts are one boundary line longer than their local newline-terminated file counts; the location translations in this report use the stated starting-line offsets, not a claim to have read an extra original line.

| Packet file | Local lines actually read | Original source span from manifest | Method/status |
|---|---:|---:|---|
| `MANIFEST.json` | 1–165 | Packet metadata | Entire file read; no repository history lookup. |
| `SCIENTIFIC_CONTRACT.json` | 1–36 | Packet contract | Entire file read, including physical-output scope. |
| `policy/AGENTS.md` | 1–137 | 1–137 | Entire copy read; full Git blob matched. |
| `theory/R3_DEFINITIONS.md` | 1–24 | 5–29 | Entire supplied extract read. |
| `theory/R5_BODY.md` | 1–117 | 5–122 | Entire supplied extract read; initially truncated tool output was reread to completion. |
| `theory/SOURCE_BATH_BODY.md` | 1–114 | 17–131 | Entire supplied extract read. |
| `inputs/LITERAL_BINDING_EXCERPT.txt` | 1–66 | 1–66 | Entire supplied excerpt read, including metadata/evaluation qualifications. |
| `implementation/finite_thermal.py` | 1–487 | 1–487 | Entire copy read; full Git blob matched. |
| `implementation/run_once.py` | 1–282 | 1–282 | Entire copy read; full Git blob matched. |
| `producer/code/owners_b.py` | 1–122 | 1–122 | Entire copy read; full Git blob matched. |
| `producer/code/native.py` | 1–159 | 1–159 | Entire copy read; full Git blob matched. |
| `producer/code/phase_b.py` | 1–57 | 1–57 | Entire copy read; full Git blob matched; embedded status/count exposure recorded below. |
| `producer/code/mp_b.py` | 1–55 | 1–55 | Entire copy read; full Git blob matched. |
| `producer/code/finite_b.py` | 1–105 | 1–105 | Entire copy read; full Git blob matched. |
| `producer/inputs/EARLIER_H_ONLY_PHASE_WITNESS.json` | 1–55 | 1–55 | Entire copy read; full Git blob matched. |

Read-only `git hash-object --no-filters` on the complete copies returned, in that command's order:

| File | Observed local Git blob |
|---|---|
| policy/AGENTS.md | `6464cd96b7023e3e91e30246bc93650d4e435a10` |
| implementation/finite_thermal.py | `880a074f793ba6bb3aa3e1d7958d8116eb239c0e` |
| implementation/run_once.py | `3dd1b2428c41515139ecfe3e5c60ecc8988236f2` |
| producer/code/owners_b.py | `cfe9a7c07f1e3d42c17f86a265cd5cfeffc080fd` |
| producer/code/native.py | `98b581a592b86432807d5f79269caeaa4a974ba3` |
| producer/code/phase_b.py | `b954722915fe532211bce124ab1bf98cb95a2efb` |
| producer/code/mp_b.py | `928c7905e5fb13e1867a820b0662cf1e47308e32` |
| producer/code/finite_b.py | `acc8431e6ce7d054801d237bc9f16ba50f6a2806` |
| producer/inputs/EARLIER_H_ONLY_PHASE_WITNESS.json | `d18b22c1dd7cba3d636c0557c243fdd35f6201a9` |

All nine matched the supplied manifest. No digest of a scientific result was used as an accuracy criterion. No hash of an unavailable original input was recomputed or claimed.

The following skill resources were read in full through `skills.read`, under package `e1/skill-6aa0657100b08191b7d67482d1f97c1d`: `SKILL.md`, `references/RESEARCH_POLICY.md`, `references/THEORY_LOOP.md`, `references/CODING_LOOP.md`, `references/EVIDENCE_AND_HANDOFF.md`, and `references/RUNTIME_AND_LEGACY.md`. The provider returns resource content rather than original line-number locators; all returned sections were read. The truncated RESEARCH_POLICY and EVIDENCE_AND_HANDOFF displays were reread to completion. I did not read REI operational execution-history references, legacy harnesses, or workflow completion records.

### Material not read

- Preserved tests, raw execution logs, C6–C8 results, controller reviews, operational handoffs, prior audit verdicts, and full original review documents beyond the supplied extracts: intentionally excluded from Phase 1.
- The original finite result, full literal-binding JSON, SOURCE_OPERANDS.json, TUBE_RESULT.json, FINITE_TUBE_INPUT_SLICE.json, NATIVE_QSS_STORED_INPUT_5126_5127.json, old consumer FIRST_RESULT.json, and any saved reference file named within them: not in the disclosed initial packet; no restoration or alternate source lookup attempted.
- `channel_maps_b.py`, `core_bridge_b.py`, native HyRec C/header/data files, referenced historical ZIP/CSV originals, and the cited HyRec paper: outside the packet. The present derivations use the supplied conditional bath model and inspected producer interface, not an independent validation of the whole upstream solver.
- No workspace-wide listing, repository-history search, full source census, browser retrieval, scientific execution, or CAS was performed.

## 8. Embedded evaluation and historical exposure ledger

The following wording reached me through required packet content. These quotations are source assertions or code literals; they were not counted as independently observed test outcomes, reviewer verdicts, or proof. Mathematical claims listed here were assessed through section 3, with F1 treated separately.

### 8.1 Exposure that limits the blind-review description

1. `producer/code/phase_b.py` lines 11–15 includes the exact literals `status='STARTED'`, `original_DAG=dict(completed=27,total=88,delta=0)`, `requested_model='gpt-6.1-sol',observed_runtime_model=None,old_source_runs_replayed=0`, and the statement: `All new truncation/quadrature/MP bounds are conditional on admitted saved moments. 65-digit half-unit is representation rounding only, not a bound on old quadrature/source accuracy. Physical and total inherited input errors remain null.` These disclose historical source count/status metadata in code. I did not seek or use those counts as evidence of completion.
2. The same file, lines 52–56, contains `TRANSACTION_CHECKS_PASS_BEFORE_ONCE_RHS`, `NUMERICAL_FINITE_TRANSACTION_PASS_AWAITING_INDEPENDENT_ROOT_ADMISSION`, and `FAILED_PARTIAL_RESULTS_PRESERVED_RETURN_TO_ROOT`. These are potential assigned status strings, not an observed executed outcome in this review.
3. `inputs/LITERAL_BINDING_EXCERPT.txt` line 53 says: `Read existing num/den representation and original source/control identities; no replay of its 14 tests or 10 source controls`. Thus old check counts were exposed despite the deliberate withholding of current tests/evidence. No associated old result file was opened.
4. That excerpt's lines 37–39 include `"ACTUAL_DECODING_EXECUTED_HERE": false`, `"actual_binary64_numerators_denominators": null`, and `Within the existing source-identity/representation tests, contrast typed binary64 import with direct decimal import; do not weaken the scalar core's accidental-float rejection. This is NOT_RUN.` Line 64 contains `"independent_transcription_or_science_review":"NOT_RUN"`. These are historical packet statements, not a finding about later execution.
5. The required manifest names the source extract `review/R6_SOURCE_BATH_RECONCILIATION_20261028.md`. The name reveals its provenance category; no undisclosed verdict section was accessed.

I notified the parent of items 1–3 during Phase 1. The reply asked that the exposure be preserved and distinguished from parent dialogue/Phase 2 outcomes; it did not give a scientific result. The source copies were not edited to remove these phrases.

### 8.2 Evaluative wording in scientific extracts

- R5 local 17: `The algebraic map is exact conditional on its caloric law and supplied integrals; it is not an exact time integrator for unknown Q or W.`
- R5 local 35: `This proof needs no assumption that either residual vanishes.` The same paragraph states: `The identity diagnoses a discrepancy; it does not alter any saved stock, energy or residual.`
- R5 local 55 and 59: `An independent algebraic check within this derivation is the cross-multiplied identity` and `This is a different algebraic form, not an independent external review or an executed test.`
- R5 local 71: `The displayed bound is a sufficient enclosure, not a universal optimal error constant.`
- R5 local 77: `For a correlated admissible subset of that box the same interval remains an enclosure, but its endpoints need not be attainable. No probabilistic independence assumption is needed for enclosure.`
- R5 local 79: `Its extrema are attained at vertices. Physical sharpness additionally needs those vertices to be physically admissible; an outer polytope alone does not establish that.`
- R5 local 81: `A small arithmetic or saved conservation residual does not provide eE or eN for model, transport, rate or EOS error. Missing physical radii remain null.` The paragraph also says: `These are conditioning/domain limits, not global physical impossibility results.`
- R5 local 99: `Associativity of repeated composition follows from multiplication of volume ratios and distributivity of scaled extensive increments. It does not establish closure when intermediate physical states or sources are inconsistent.`
- R5 local 117: `This is not a supplied general-EOS implementation.` and `EOS uncertainty requires its own bound; the inverse theorem does not manufacture one.`
- SOURCE_BATH local 13: `The first three code files and phase witness were read, not imported or executed.` The same paragraph says its pins are `source-declared pins, not newly computed whole-file hashes.`
- SOURCE_BATH local 15: `No full-result restoration, provider solve or original calculation was repeated.`
- SOURCE_BATH local 19: `Primary literature support is limited and explicit:` and `This literature supports the caloric counting convention, not this consumer's independent validation.` Its statements about Exa, SciSpace, and arXiv retrieval were not independently reproduced.
- SOURCE_BATH local 44: `This is an algebraic diagnostic, not a residual correction.`
- SOURCE_BATH local 52: `This proves the prospective positive bias for B>0. No numerical bias or actual endpoint temperature has been evaluated here.` The paragraph calls its ratio 9/8 control `a manufactured algebraic example, not the source helium abundance.`
- SOURCE_BATH local 62: `This report identifies the construction of (b), without evaluating it or activating (c).`
- SOURCE_BATH local 74: `The last identity follows by cancellation of Q, not by a new solution of the history.` It also says: `Do not redefine W from the left identity and then call the resulting zero an independent verification. Nor reconstruct G from U_b/(U_a+J2) for that purpose.`
- SOURCE_BATH local 76: `This confirms the original R5 instruction to apply the saved W once.` and `the displayed energy balance is not a proof of a newly self-consistent matter-temperature trajectory.`
- SOURCE_BATH local 98: `This is hand algebra, not an executed test, and no physical source value is inferred from it.`
- SOURCE_BATH local 100: `The exact-Fraction core is still the unweighted U/Q/W route.`
- SOURCE_BATH local 102: `Additive implementation binding, not an implementation claim`.
- SOURCE_BATH local 114: `These requirements refine existing acceptance cases for count ownership, normalization, residuals and two-segment composition. They do not require another broad test framework or changes to the original provider. No finite_thermal.py, tests or runner were authored in this continuation.` This is a historical statement in the extract and is not treated as a statement that the separately disclosed current implementation is absent.
- Literal excerpt line 47: `All formulas are prior direct derivations with newly read field bindings; B, T, residuals, differences and bias were not numerically evaluated`.
- Literal excerpt lines 55–56: `NOT_OBTAINED: fetch_file returned empty content with blob; raw fetch returned HTTP400 size/unsupported error` and `"substitute_full_source_claim":false`.
- Witness line 54: `Earlier actual native index3161 has exactly equal xe and xHII; in simultaneous H/He loop xHeII>XHEII_MIN=1e-6 would be separately present. The source advances one-way to H-only and never re-enters helium evolution. Knots5126/5127 are later. Preserve this as source-model He-neutral convention, not physical assertion of exactly zero helium ionization.` This argument was received, not independently checked against its unprovided originals.

### 8.3 Evaluative wording in code comments/docstrings and related literals

- `finite_thermal.py` lines 1–6: `Exact represented-input caloric maps; no ODE, provider execution or activation.` and `C5 is code authoring only: tests and scientific admission are pending.`
- Its lines 131–132: `Preserve initial-EOS and interval-balance residuals; never repair them.` and `Independent saved initial value, including a diagnostic mismatch.`
- Its line 253: `Only UNWEIGHTED increments per V0 then V1; J2 is not an input port.`
- Its line 324: `Opt-in source bridge. Does not relax exact() for accidental floats.`
- Its line 361: `Pin the transcribed 11-field packet; not a substitute for full source.`
- Its line 404: `The algebraic module has no operation that activates a physical client.`
- Its lines 411–415: `Complete opt-in byte-pinned source path. No provider imports or solves.`; `Calling this is a new scientific evaluation and needs separate authorization.`; `The returned caloric temperatures are source-model diagnostics, not target temperature updates. Original decimal residual lexemes are returned intact.`
- Its line 471: `Lossless Fraction records; no float formatting of scientific outputs.`
- `run_once.py` lines 1–5: `One explicitly authorized C6 attempt. Authored in C5, NOT EXECUTED.`; `This wrapper is an operational replay/budget guard, not a security boundary.`; `A truthful operator authorization is required; no budget is granted by this file.`
- Its line 48: `Pure validation only. Does not execute a command or manufacture approval.`
- Its lines 86–90: `Classify observed process evidence, not the truth of the science.`; `A missing observation is not a measured budget overrun.`; `Timer-related worker signals are recorded as signals, without inventing their sender.`; `SIGKILL alone cannot identify CPU exhaustion, OOM, or an external kill.`
- Its line 149: `One use of this authorization file, even if a later launch fails.` Its output vocabulary includes `NOT_ISSUED`, `EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION`, and `whole_turn_budget_compliance="NOT_CLAIMED"` (lines 108, 154, 268). None is treated as an observed present execution.
- `producer/code/mp_b.py` line 1: `MP70 serialization, sparse elimination and bounded positive quadrature.` Lines 25–27 implement printing `PASS ` or `FAIL ` and raising `frozen Phase B check failed: `; these are code branches, not observed review outcomes.
- `producer/code/finite_b.py` line 1: `Constant activity matrix finite endpoint and exact integrated moments.` Lines 60–61: `The exact clock count identity is algebraic, evaluated separately from incoming integrations, which are preserved rather than replayed.` Lines 20–22 describe saved-reference rounding as `saved65-significant-digit reference-string representation rounding only; not old quadrature or source accuracy`, with `prior_acceptance_is_rigorous_error_bound=False` and `physical_error=None`.
- `producer/code/owners_b.py` lines 22–23: `Planck-Wien is a positive exponentially convergent series, integrated analytically with an explicit positive geometric tail bound.` Lines 95–96: `Independently derived adiabatic work in the common V0, rather than a subtraction of densities at unequal volumes. Dust/internal have no work.` The embedded check names include `total hydrogen inventory exact conservation` (83), `all propagated sector energies positive with conditional numerical margins` (105), and `common V0 total event plus independently adiabatic geometry-work identity` (108). These names were not accepted as proof of an executed check.
- `producer/code/native.py` lines 1–4: `Transcription of the pinned original HyRec coefficient routines only.` and `No history integration, source exporter, validation snapshot, or old result program is imported.` Line 106: `Original rec_Tmss source operation order, fsR=meR=1.` These establish the source's stated role, not an independently checked provenance chain.
- `producer/code/phase_b.py` line 1: `One new finite-source completion, saved operands only; no Phase A replay.` Line 33: `Explicit known diagonal solution retains the initial finite layer.` Its status/model/count literals are quoted in section 8.1.

No embedded assertion of “exact,” “independent,” “PASS,” “admitted,” or “NOT_RUN” replaced a derivation or observation in this report. General repository policy words such as PASS/HOLD/NO-GO are instructions, not historical reviewer verdicts.

## 9. Return boundary

This document is the complete Phase 1 judgment and read/exposure ledger. The only local mutation performed for the review is creation of this report in the requested reviewer directory. Production code and the initial packet were not changed. Scientific execution status for this reviewer is **not_run**. The report is to be preserved unchanged when Phase 2 evidence is compared.
