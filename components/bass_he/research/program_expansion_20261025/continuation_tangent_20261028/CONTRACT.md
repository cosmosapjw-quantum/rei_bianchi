# TANGENT13 — certified curved-cone aperture minima

Root scientific contract, physmath-research-loop 1.0.0 (the user supplied this exact version), 2026-10-28.
Unit HE-EXP-TANGENT-13. Owned path research/program_expansion_20261025/continuation_tangent_20261028. New branch research/he-tangent13-20261028.
User authorization: inspect current related repositories/branches/conversation-accessible records/backups, then execute one next theory R1–R10 and implementing coding C1–C10 loop, publish/back up every stage, return copyable handoff.

## Baseline and intake
The supplied EXFOR11 handoff is valid history. Fresh actual intake found completed QUARTIC12.
Source baseline 4c71acfa2b8721a0d0b8f9cec8814f75f1c55739, tree 08e11c808d86cdf2a00ceb9feb3de43fc1bf3089; prior execution S05 2f66fbe31e6d52adb19f6701f58c14c67f6ac204.
Latest observed central 7937ed4a842eb1ef6cec562a4224fb0add63d0d6, tree 86f97b882caff8aa6022a97df185ee36a40da1ed. Refresh before publication.
Restored final ZIP:730622 bytes, SHA256 d4b9fa00d2af2597c5574b7608eb602edb02d74761aa3526d3f8f3c7e4643219. All65 restored repository files match their current Git blob identities. Local is a partial source mirror; no local D commit or full clone is claimed.
Related7repo branch census1444heads/18terminalpages; backup/context intake details are in stage S02. No completed predecessor science/test/CAS/plot/ACKed backup is rerun.

## Objective and fixed scientific scope
Close the finite N16 minima gaps at258MeV for HEMISPHERES and CAPS under the SAME full nonnegative even quartic model and nominal-angle sensitivity windows. Target absolute bracket width <=1/10^10 for each true minimum. This is a computational certificate tolerance, not experimental uncertainty.
q(z)=b0+b1 z+b2 z^2>=0 on z in[0,1], f(mu)=q(mu^2), d=(2,2/3,2/5), D=d.b>0, b in nb/sr. Retain (-,+,+,+), c,hbar,kB, inherited target/product rest energies, same-event detector union and declared uniform azimuth.
Reuse exact saved rows and moment enclosures from QUARTIC12 SAVED_PLOT_DATA.json, SHA256 a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45. Original EXFOR M0475 SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f.
Four258MeV windows at46/61/73/87deg are [.05,.11],[.15,.31],[.09,.23],[.18,.32]. They are deterministic coordinate ERR-S sensitivity windows. No total-cross-section interpolation or energy mixing.
Only258MeV free-endpoint minima are newly solved. Other energies, maxima and endpoint-zero exclusions retain their existing evidence.

## Constructive method
Each saved row m_i=(1,zmid_i,z2mid_i) has exact epsilon_i and true nominal row error <=epsilon_i for |b_j|<=160. Use outer L_i-=L_i-epsilon_i,U_i+=U_i+epsilon_i; inner L_i+=L_i+epsilon_i,U_i-=U_i-epsilon_i.
The existing extrema identify61deg lower and73deg upper as the active data pair. This is a candidate choice from saved evidence; exact dual nonnegativity and feasible-witness checks, not that candidate choice, establish the result.
For w_i(r)=r^2-2*m_i[1]*r+m_i[2], define F(r)=U73*w61(r)-L61*w73(r), separately for outer and inner windows. Verify F(4/5)<0<F(9/10) and F'(r)>0 throughout this interval. Perform exactly80 rational bisections (or terminate for an exact root); preserve a containing interval. This isolates a root on the declared interval; no assertion about absent roots elsewhere is needed.
Choose rational r_out as outer bracket midpoint. Set h=m61-(L61_outer/U73_outer)*m73. Every true feasible b satisfies h.b>=0. Set v(r)=(1,r,r^2). Solve the exact3x3 identity
  k_mid-alpha*d=lambda*h+mu*v(r_out)
for alpha,lambda,mu separately for the two detector moment midpoints k_mid. Require lambda>=0,mu>=0 and exact zero residual. Since q(r_out)>=0, this proves k_mid.b/D>=alpha for ALL true feasible b. The proof does not require b to have the witness sign pattern or r_out to be an exact algebraic root.

For a feasible upper witness choose r_in as the upper endpoint of the inner root bracket. Require w61,w73>0 and the scale interval [L61_inner/w61,U73_inner/w73] nonempty. Its rational midpoint a gives b=a*(r_in^2,-2*r_in,1). Verify a>0, r_in in[0,1], |b_j|<=160, D>=49/4800000 and ALL four contracted data inequalities. Then q(z)=a(z-r_in)^2 is exactly nonnegative. Evaluate the sign-aware moment interval of this genuine feasible witness.

## Moment uncertainty and inherited certificate reuse
Read the already certified258MeV free_N16 outer vertices; do not call an optimizer, geometry solver, trigonometry or predecessor campaign. For each j compute exact M_j=max_v |v_j|/D(v). The denominator-weighted convex representation proves |b_j|/D(b)<=M_j for every member of this containing polytope, hence the true family. Save the vertices used and maximizers; check D>0 and every stored vertex against its saved inequalities as part of changed-evidence intake, without recomputing enumeration.
Let Delta_k=sum_j M_j*(k_j_upper-k_j_lower)/2. The true ratio is >=alpha-Delta_k. Let U be the sign-aware upper ratio of the feasible square witness. Publish [max(0,alpha-Delta_k),min(1,U)] with exact fractions, outward decimal endpoints and width. Require ordered endpoints, width<=1e-10 and inclusion in the saved predecessor minimum bracket for both geometries.
This is a global minimum bracket within the fixed full quartic/data family. It is not a strong no-go, physical production rate or uncertainty interval. No novel general optimization theorem is claimed.

## Implementation and validation contract
Use standard-library Python Fraction exact arithmetic. No scipy/sympy optimizer or prior scientific modules required at runtime. Code consumes the pinned saved JSON and official source bytes by explicit paths. No computations on import.
Implement source binding, fixed case extraction, root isolation, rational3x3 elimination, dual certificate, witness construction, normalized-coefficient envelope and independent saved-certificate verification. Reject missing/mismatched inputs, singular dual systems, wrong root signs/monotonicity, negative multipliers, infeasible witnesses and target violations with explicit reasons.
Meaningful controls: known rational double-root polynomial and root isolation including exact-root/invalid-bracket cases; known linear system with exact residual and singular rejection; manufactured nonnegative-cone dual including rejection of a negative multiplier; signed moment rounding with independent manual reference; saved input identity and outer vertex constraints; actual dual identity/positivity; actual feasible square witness/all windows; both final brackets, tolerance and predecessor inclusion. The certificate reader validates outputs independently of candidate search and is not advertised as a second optimizer.
Source S05 is actually published and an execution pin saved before the one primary campaign. C6–C8 refer to different portions of this one campaign; they do not cause repeat execution. A fresh nonauthor review covers the contract, actual code, results, saved-only figure and final source/central claim boundaries in one pass with staged checkpoints.

## Resources and routing
New primary campaign: whole runner+waited-child CPU120s/wall300s/AS768MiB/threads1, one initial execution. At most one diagnosed targeted repair within the same remaining cumulative cap, root authorized, with original failure preserved. This new-unit allowance does not replenish any predecessor reserve.
New Wolfram evaluator: one bounded20s call for polynomial factorization/root equation/dual and moment-envelope identities. The current context call returned SERVICE_ERROR; record it separately from evaluator outcome. Remote CPU/wall remain null unless supplied.
One saved-only PNG/SVG render: CPU10s/wall30s/AS768MiB/threads1. No scientific imports/calls in plotter. Inspect the actual image.
Root owns equations/admission; mechanical implementation/execution goes to a lower-tier coding agent under this frozen contract; requested/observed model identities are distinct. The repo survey agent is nonauthor and performs independent review.

## Publication and counters
Reuse the established10paired checkpoints S01=R1/C1 through S10=R10/C10; each contains two actual workproducts, total20. Each stage gets an actual source commit/ref readback and Drive/Dropbox backup ACK, with creation-time metadata explicitly scoped.
Append exactly one local node TANGENT13-CURVED-CONE-MINIMUM-REFERENCE to inherited16nodes. Start12complete+1inheritedpartial+3physicalopen+1pending/17; accepted13complete+1partial+3physicalopen/17. Central28/88,HEdelta0 unless new physical owner evidence actually closes a central obligation. Current intake supplies none.
Drive folder1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI; Dropbox ns:183516487//BASS_DERIVATION_DOSSIERS_20260912. New unique archives BASS_HE_TANGENT13_Sxx_20261028_<hash12>.zip. Do not reupload existing completed archives.
Central update limited to the established HE observational paths, with fresh expected_sha,force=false and actual readback; preserve unrelated source ownership,88nodes/17edges/15authorities/85nonHEstates.
Final external metadata_scope=POSTPUBLICATION_EXTERNAL_DELIVERY, separate from the S10 creation snapshot. Publish four authority documents and final transport receipt without inserting future ACKs into sealed archives.

## Physical boundaries and history
Open: event/inclusive normalization+liquid-He electron/target-motion/response projection; actual full angular/polarization law+photon encounter history; named nonthermal birth/deposition/thermalization+global species binding.
population_rest_energy_witness sole binding owner; independent_binding_RHS/Gamma_thermal/Cv/species_heating/thermal_deposition=null;birth_pool=UNASSIGNED;global_physical_completion=null;L4=false;production=NOT_APPROVED;activation=false.
Preserve QUARTIC12 and EXFOR11 COMPLETE_SCOPED, HARMONIC10 initial24PASS+1FAIL and targeted1PASS with reserve0, KINEMATIC08 inheritedpartial, PHOTON05 plotCPUfailure. New no-go admission is not sought; NG1–NG7 are screened at R8 against the actual constructive claims.
Stop after this single new theory+coding loop and actual final delivery unless another explicit task is given.
