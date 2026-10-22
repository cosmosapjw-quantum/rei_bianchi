# D9 component shear budget — frozen scientific and execution contract

Controller: Astra; date: 2026-10-21 UTC. This is the next bounded research unit requested by the owner, after recovering actual newer D8 results. It is not a replay of the completed pilot.

## Baseline and question

Repository `cosmosapjw-quantum/rei_bianchi`; intake PR199 HEAD `eb8042b729051f4700bd5d88d6781c4620009bcb`, two commits after the previous delivery `744438f4512c7df1646aad0136ddc435b27200b0`. D8 data-only adjacent-sample brackets were already published at `a3cb0606341688affb6aea29990e960e53188d32`. Its task-local DAG is complete. The stale central D8 ready flag will be corrected from that evidence, with no D8 execution.

Question: on each of the 175 existing nominal component-grid trajectories, how do the accumulated matter and radiation stresses combine with the initial shear after removing the expansion damping? In particular, why do four of the five points with Sigma_F,i=0.003 and P_r,i=-0.001 cross signed shear zero before z=2, while P_m,i=+0.0003 does not?

Inputs are the already verified B pilot, 175 nominal unique case IDs selected from its existing manifest, 153 stored epochs per case, z=20 to 2. Use the 35 exact references already identified by the manifests. Do not count aliases as new cases. All 237 histories and the six existing refinement controls remain preserved and are not re-integrated. Read the existing case receipts/manifest and bind each selected raw file to its recorded SHA256. If an identity is absent or contradictory, return the specific case to the controller before claiming completion.

## Fixed physical definitions and exact derived identity

Signature (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot(b), H=dot(a)/a>0. In the common normal orthonormal frame, sigma_ij=diag(-s,-s,2s), pi_X,ij=diag(-p_X,-p_X,2p_X). Energy-density stresses p_X are in J/m^3; K=8 pi G/c^2; proper-time H is in s^-1.

S_F=sqrt(6)*s/H; P_X=sqrt(6)*K*p_X/H^2; Sigma_F=abs(S_F); Pi_tot,F=abs(P_m+P_r). The already checked shear equation is dot(s)+3 H s=K(p_m+p_r). For x=ln(a/a_i),

S_F' = -(3+H'/H) S_F + P_m + P_r.

Define M(x)=(a/a_i)^3 H/H_i=exp(3*(x-x_i))*H/H_i>0, Q=M S_F, and I_X(x)=integral[x_i,x] M(u) P_X(u) du. Then exactly, along this one coupled solution,

Q(x)=S_F,i+I_m(x)+I_r(x),  S_F(x)=[S_F,i+I_m(x)+I_r(x)]/M(x).

Where the stored gamma and neutrino signed stress arrays are available, integrate them independently and record I_r=I_gamma+I_nu. Their common initial brightness/operator restriction remains unchanged. This is an additive accounting identity on a solved, coupled trajectory; it is not a claim that trajectories with altered component initial data superpose.

At a simple zero S_F=0, S_F'=P_tot and dS_F/dz=-P_tot/(1+z). A nonzero slope gives a cusp in abs(S_F), not a physical singularity. D8's actual stored sign brackets remain authoritative; D9 does not estimate a continuous root or add dense output.

## Implementation and meaningful checks

Use direct saved a,H,s,P_m,P_r (and signed gamma/nu) arrays. Reuse source diagnostics without importing or calling an ODE RHS, solver, or momentum quadrature. Load each selected raw file once; check finiteness, positive a/H, strictly increasing x, identical common epoch grids, initial-axis mapping, and normalized-component sum to roundoff. Stack arrays and use NumPy broadcasting plus SciPy `cumulative_simpson` over the epoch axis. Record actual NumPy/SciPy versions. An existing dependency is preferable to a new integration backend.

The scientific approximation is sampled-data quadrature. Record the signed residual R=Q-S_F,i-I_m-I_r at every stored epoch. Define scale=max(abs(S_F,i), max_x(abs(I_m)+abs(I_r)), 1e-12) separately per case. The pre-fixed diagnostic acceptance is max_x(abs(R))/scale <= 2e-5. This is an observed consistency threshold, not a rigorous global error bound. Never normalize an error only by a near-zero final shear. Also report the endpoint Simpson/trapezoid difference as a sensitivity diagnostic; it is not a convergence certificate or additional IVP.

For the four previously established D8 brackets, require the reconstructed Q signs at both stored endpoints to agree with the saved Q, and require abs(R) < 0.1*abs(Q) at each bracket endpoint before making a budget-resolved sign-crossing interpretation. If this fails, retain the raw bracket, mark the budget interpretation unresolved at that resolution, and report to the controller without changing the tolerance or re-integrating.

Minimal software controls: an analytic polynomial weighted-source primitive on a nonuniform grid (quadratic source), source-free decay identity, and opposite signed sources that cancel exactly on the same prescribed geometry. Test nonmonotone-grid rejection because it invalidates the quadrature. These verify the new transformation/quadrature path, not the historical ODE campaign. One production/verification pass and at most one fresh, complementary Astra review of physics, code, and the actual figures; targeted repair only for an observed defect.

## Outputs, scope, and resources

Write only within `rei_unified_20261021/continuation_20261021T1316Z/D9_COMPONENT_SHEAR_BUDGET/` until the root integrates central metadata. Provide complete executable analysis/plot CLI, readme with exact invocation, minimal tests, run receipt, source/input hashes, 175-case endpoint CSV/JSON, five focus histories, sampled residual diagnostics, and two or three readable PNG/PDF figures with their plot data. Include all signed sources; do not add an epsilon or clip signs for logarithmic plotting. Use saved samples and clearly label connected lines as visual guides. Reference D8 brackets; do not recompute its full analysis.

Light sandbox budget: 0 new IVPs, 0 ODE callbacks, 0 momentum-moment recomputations, <=2 process workers, one BLAS/OpenMP thread per process, analysis+tests aggregate process CPU <=120 s and individual command wall <=120 s. Main vectorized analysis should use one process; extra worker capacity is only for independent file/figure work. Do not benchmark or assert a speedup. Stop if the cap is reached, preserving completed outputs. No NCP dispatch is needed for this unit.

NCP preparation: the same CLI must run from a normal repository checkout with only NumPy/SciPy/Matplotlib, read restored raw data, and create a new output directory. Provide `run_ncp.sh` for this data-only unit with inner threads fixed to one, a finite timeout, no global environment changes, no dirty-checkout reset, and no process termination. Mark actual NCP execution NOT_RUN. The newer PR215 NCP warm-kernel receipt is a different physical lane and is not current live machine availability or D9 execution evidence.

Publication remains owner-authorized, additive under `research/rei_unified_sigma_pi_20261021/`, expected-head fast-forward only, draft/no merge/no force. Raw data already durably stored are referenced by their exact archive/provider/manifest rather than needlessly replicated. Create-only new checkpoint/final delta archives and actual provider acknowledgements/readback will be recorded by the controller. Preserve PR198 scoped PASS, AGE convergence HOLD, Grackle bound NOT_ESTABLISHED, production admission NOT_ISSUED, and V12 restrictions.

Selected work: R2 existing-evidence intake; R5/R7 new derived identity and bounded calculation; C2–C7 implementation and targeted validation; R6/C9 one independent review; R8–R10/C10 scoped scientific decision, publication and handoff. Prior completed loops remain unchanged; no further cycle is automatically started after D9 closes.
