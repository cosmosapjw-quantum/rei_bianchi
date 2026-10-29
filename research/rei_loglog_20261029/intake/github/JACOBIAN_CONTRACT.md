# Frozen prescribed-bath chemistry Jacobian contract

> Acceptance-criteria history: the numerical thresholds below are the initial proposal only. Before execution and before `ROOT_GO_620`, root explicitly replaced them with the frozen componentwise directional bound `1e-6 * signal_bound + roundoff_allowance` and normalized ledger tolerance `1e-12`, as implemented in `implementation/validation_driver.py`. This supersedes only the earlier proposed `1e-7` finite-difference and `5e-13` invariant thresholds, not the source identity, equations, scope or saved-bath boundary. The old values remain below as proposal history; they are not claimed as the criteria used in the completed run. This was a pre-execution choice, not a post-hoc relaxation.

Authority source: rei_bianchi c5ab42c8673db614e7fb16695ad071c65becb81b, coupled.py blob4773d4278e1fa2f1a8a24a9df79f9ba5d46d5771; history.py blob8faef2ce29377c5650515d3b3e23f494910a82c3; old model blob1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc; config blob64c551f5ec23580e19ad1177375ae65e8c1c542f. These exact source texts are sibling files. source17_pr262.py is separate new photo-only counterfactual model and MUST NOT be silently spliced into the old saved IVP.

Scope: exact analytic state derivative of existing23dimensional polynomial prescribed-bath RHS at fixed proper time, plus scaled-coordinate transform. This advances an existing REI-L1 adapter/derivative sub-obligation without closing original node. No IVP, spectrum substitution, bath alteration, dynamic electron-feedback insertion or physical sensitivity claim.

State X=(y[17],B[2],U[2],A_boundary,electron_ledger). Stocks perHref; energies eV/Href; t seconds. S=diag(Coupled.scale), x=S^-1 X.

At fixed t let G,n,hidden,hidden_dot=fields(t); base,M,power0,P,L=new[mode]. M has21rows/19cols: rows0:19 heavy+fast derivatives, row19boundaryA, row20electron. Construct J0:
- J[0:19,0:19]=M[0:19,:]; J[0:17,0:17]+=G.
- J[19:21,0:17]=P; J[19,19]=-L[0], J[20,20]=-L[1].
- J[21,0:19]=M[19,:].
- J[22,0:19]=M[20,:]; J[22,0:17]+=Q17@G.
- All other entries zero (ledgers have no feedback).

For (h,d)=(1,3),(2,4), v=-e0-eh+ed and r=n*C*y0*yh.
J += v outer [n*C*(yh*e0+y0*eh)], with v padded23; only heavy rows change.
The full scaled Jacobian is Js=S^-1 J S. Constant injection, hidden_dot and power0 have zero state derivatives. OFF and ON each use their own actual compile_new arrays; OFF still includes intrinsic decay/capture/selectedT exchange.

Exact linear conservation derivative controls:
b=(A17,1,3,0,0,1,0) gives b^T J=0.
q=(Q17,0,1,0,0,0,-1) gives q^T J=0.
These are state-derivative identities even with prescribed hiddenLi6 because its derivative is independent of X. Normalize residual by sum(abs(weight)*abs(J)) with exact-zero handling; tolerance5e-13 float64 is ample for finite event sums without numerical integration.

Directional finite difference: compare Js*v with [f_scaled(t,x+h*v)-f_scaled(t,x-h*v)]/(2h), signed Newton extension permitted by source. Use3nondegenerate directions and two moderate h values (e.g1e-3,1e-4 timesmax(1,norminf(x))); compare maxabs discrepancy to maxabs analytic directional derivative and roundoff prediction from RHS magnitudes. Since RHS quadratic, central difference has no analytic truncation error. Require relative error<=1e-7 where signal resolvable; tiny cancellation-dominated components must use explicit floating roundoff bound, not floor-based claims. Capture-specific symbolic derivative and state-scaling controls independent of finite difference. No new tolerance for existing IVP adopted.

Source boundary: rec hazards in old_bath are nref*saved_electron_per_Href*thermal(savedT); electron_ledger is explicitly NOT ne bath. This exactJacobian contains no physical electron feedback. Source262missing full source-qualified physicalJy remains missing; no one may promote this conditional23x23 derivative into that claim.

Budget interpretation: AGENTS_BASE.md temporarybudget policy authorizes increases below50% originalbaseline with cumulative debit/restoration and retainsNO_MORE_IVPs. Root-proposed620vs600 is3.333%, fresh bounded<=4CPU unit permitted only under root frozenallocation; sourcehistorycompletedrun allocations cannot be reused/reset. This read-only authority task executes no tests.

Remaining recovery: Coupled.__init__ requires externalangtherm baselineNPZ/backgroundNPZ/angular_model/atomic_network; nested paths404 in currentGit because archivedinput tree not public. Reuse exact archive recovery if available. If unavailable, compilation/operator and algebra can be checked on source-defined fixed coefficients but must label syntheticfixed-field validation, not actual saved-bath validation. Do not fabricate matched bath inputs.

PASS -> store new derivative adapter and source-scoped result for this originalobligation; originalworking33/88central28/88 remain. Actual fullselfconsistentJy, density/clocksource qualification,tangentIC/BC, physicalsourceuncertainty and true causalDy remain separate missinginputs.
