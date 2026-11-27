# THEORY16 R7: source-bound current and material-age clock discriminator

2026-10-14 (Asia/Seoul). Selected stage: R7, following the actual immutable R6 NEXT_ACTION.json. R6 original backup/publication was completed first in commit9617376418b9de61eaaf5ce54a25127f70d337c3. This result does not run R8-R10, promote the production source, or complete the source-owner moving-geometry node.

## Result and actual consumer

A new executable exact-rational reference consumer reads the preserved source52/R6 certificate, constructs the integrated electron current and evaluates six optical-depth intervals. It does not invoke the source RHS, ODE, collision generator or native receiver. It keeps total free-electron count (initial3), not thermal-only count (initial1).

Signature(-,+,+,+), x0=ct, u.u=-1, U=c*u, dx^a=c*k^a*ds. The source age theta(x) is in proper seconds. Define q_a=c*nabla_a(theta), with u^a*q_a=1. The ray has two distinct scalar factors:

    D = -u_a*k^a > 0,
    A = q_a*k^a = dtheta/ds.

Proper ticking u.q=1 does NOT imply A=D. Indeed, b_a=q_a+u_a is spatial to u, and A=D+k.b. The reference consumer requires A>0 and exact age coverage0..h.

For the same prescribed bulk flow and fixed proper volume V, J_e^a=c*N_e(theta)*u^a/V, and

    d tau_T = -(sigma_T/c) J_e,a dx^a
            = c sigma_T (N_e/V) D ds,
    tau_T = c sigma_T integral_0^h [D/(V A)] N_e(theta) dtheta.

For constant u,k,q,V this gives tau_T=(D/A)*tau0. The source-bound donor radius transforms with the same factor. This is the new executable reference contract; it is not a claim that a production call site has been changed.

Units: q,u,k,D,A dimensionless; s and theta in seconds; J_e in m^-2 s^-1; integral J_e ds in m^-2; tau dimensionless. Constants c,hbar,k_B retain their physical conventions. k is a dimensionless parametrized null tangent, not an unqualified photon four-momentum.

## Two physically different age fields

Let n=(1,0,0,0), u=Gamma*(1,beta,0,0), k0=1 and ray cosine mu. Then D=Gamma*(1-beta*mu).

1. Fluid-orthogonal homogeneous age: theta_perp=Gamma*(t-beta*x/c), q=-u_flat. Here A=D, D/A=1 and normal-time span=h/D.
2. Normal-slice homogeneous age: theta_n=t/Gamma, q=-n_flat/Gamma. Here A=1/Gamma, D/A=Gamma^2*(1-beta*mu), and normal-time span=Gamma*h. For arbitrary ray normalization Omega=-n.k, A=Omega/Gamma and weight=Gamma*D/Omega.

These prescribe different initial synchronization/homogeneity surfaces. They are not the same physical source under a mere change of observer. Both are constant-flow, prescribed test fields, not self-consistent Einstein/Euler or tilted Bianchi histories. In a general congruence, q=-u_flat need not be an integrable global scalar gradient.

For beta=3/5, Gamma=5/4 and mu=+1,0,-1 respectively:

    D=(1/2,5/4,2), A_normal=(4/5,4/5,4/5),
    weight_normal=(5/8,25/16,5/2).

All normal-clock ray spans are125000s for h=100000s. Orthogonal-clock spans are200000,80000,50000s, respectively; all orthogonal-clock weights are1. These compare matching SOURCE-AGE endpoints, not identical observer-time endpoints.

## Invariant coordinate transformation and negative control

Transform all physical fields: u'=Lambda*u, k'=Lambda*k, q'=(Lambda^-1)^T*q. In the fluid rest chart the normal-homogeneous clock becomes q'=(1,3/5,0,0), while u'=(1,0,0,0). D, A and their ratio remain invariant. Resetting q' to(1,0,0,0) changes the physical age field and gives a different result.

The actual checks include that transformation, reparameterization k->7k with span/7, and normalization k'^0=1 with the corresponding span transformation. They preserve the source-bound optical interval and the correlated integrated-current endpoints.

A deliberately incomplete initial reference candidate assumed A=D and returned1. Its focused test failed for all three normal-clock rays; replacing it by D/A made the identical test pass. This is a manufactured discriminator, NOT a bug asserted in any upstream repository. Multiplying only by D in this example would yield4/5 of the correct normal-clock value, a20percent underestimate.

## Actual source-bound intervals

The source remains bass_cr PR52 commit110724bf8e4fc0d937d3098ee78f441aa22802c2, its fixed h=100000 proper seconds, V=1257522545067581081/1250000000000000000m3 and Bmin=7659328181264345/562949953421312eV. Parent central constants c=299792458m/s and sigma_T=6.6524587051e-29m2 are unchanged. Measurement/atomic-model uncertainties are separate.

The preserved R6 integrated donor bound is0.00018187761805176316854285108760283277eV s (the complete rational is used). Equal total energy gives R0=c*sigma_T*I_B/(2*V*Bmin), approximately1.32502933987391672344507453423e-25. The separated stopping-event l1 norm is still2Eparent; no invalid old2DeltaE certificate is restored.

Conservative short outward displays:

| Clock/ray | weight | full Thomson interval |
|---|---:|---|
| fluid-orthogonal, all3rays |1|[5.94727990838680e-15,5.94727990865181e-15]|
| normal homogeneous,mu=+1 |5/8|[3.71704994274175e-15,3.71704994290739e-15]|
| normal homogeneous,mu=0 |25/16|[9.29262485685438e-15,9.29262485726846e-15]|
| normal homogeneous,mu=-1 |5/2|[1.48681997709670e-14,1.48681997716296e-14]|

Corresponding donor radii are w*R0. Each same-clock initial3-electron baseline is multiplied by w too, so the full-minus-initial lower bound remains positive. The full-minus-surrogate sign remains undetermined. Full exact rational endpoints, current components and32-significant-digit outward tables are in the evidence package.

The constant cross-section assumption is essential to this simple scaling. Do not apply it unchanged to fixed observer-energy Klein-Nishina diagnostics: rest-frame photon energy and kinetic stress/spectral dependence must also be transformed.

For a changed source with its own valid state bound B_D and total-energy difference DeltaE, the corresponding conditional bound is

    |delta tau_T| <= c sigma_T/(2Bmin) integral D/(V A) * (B_D+|DeltaE|) dtheta.

This identity does not certify the old B_D on an expanding or differently forced source. Spatial electron-current differences or different geometries require their own terms.

## Actual verification and scoped status

Python standard-library reference:111 named checks, including5input identities and106consumer/arithmetic/domain/covariance checks. Six source-bound intervals are actually evaluated. Core focused red: exit1 with3failed subtests; corrected same command exit0. Other auxiliary validation is not relabeled as a full TDD campaign.

Two actual cloud Wolfram15.0.1 calls:15new scalar groups,3negative-control groups and8actual xTensor zero residuals. Official xAct1.3.0 archive SHA2567a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be; xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Scripts were saved before submission; observed outputs are normalized transcriptions, not raw transport bytes. No new failed scalar/tensor check returned. The intentional first failure and shell-only TERM diagnostic remain recorded.

Same author, separate exact arithmetic and CAS paths; external independent review NOT_RUN. Native subagents NOT_RUN because host dispatch was not exposed. Existing R6/source suites were not replayed. No source RHS/ODE, full generator, native production or HPC execution.

## Current cross-repo reuse

Verified CR52 and REI114 heads unchanged. REI114 retains proper event-rate units, comoving photon stocks, geometry/redshift/shear-work ownership and CR/RCT/HH OFF. Current conservation does not replace exactly-once event-consumption testing.

Read the NEW HH PR58 at0fad7e43b5131440ee15863e4295341c42c78f80, actual R5_RESULT and NEXT_DAG. PHYS26's converged near-rate7.63235883e-12cm3/s is distinct from its wide conservative interval[3.51310e-12,2.46532e-11]; tight certification remains the owner's next work. No HH coefficient or threshold ratio is inserted into the CR source.

Exa primary full-text passages and web primary metadata: Younsi, Wu and Fuerst2012, arXiv1207.4234, Eq17 for invariant optical depth. SciSpace plus primary arXiv abstract: Coley, Hervik and Lim2006, gr-qc/0605128 for two-congruence context. The material-age formulas above are directly derived; no unread theorem is attributed to those papers.

## Durable files and next action

[Full Korean report](https://drive.google.com/file/d/1MVfr97p0pk75g2TxdagzqSuLp7KaHvsM/view).

[Complete executable evidence archive](https://drive.google.com/file/d/1VeVrQLmjg0tykBVJx3uGn3kLWMmf5geY/view): BASS_HE_THEORY16_R7_CURRENT_CLOCK_20261014_v1.zip,93099bytes,34members, SHA25624ad2cd5b8b45de0a602fa9a5a45565279cc647ebb17a920a2f4e5c61cf78d94. Local ZIP CRC and33manifest-bound payload hashes verified. Dropbox completed the same93099-byte file at the existing BASS_DERIVATION_DOSSIERS_20260912 destination, ID id:BSpOijBcT10AAAAAAD47LQ. Drive upload acknowledged the correct name and parent; no R7 remote restore test is claimed.

The Git result is a complete compact proof/entrypoint. Full tested source, exact inputs, original red/green logs, CAS scripts/outputs, table, manifest and next action are in the immutable linked ZIP. Reproduce with python checks/test_clock_red.py and python checks/run_r7.py from its extracted BASS_HE_R7_20261014 directory.

Next selected stage: R8 scoped judgment using this evidence. Project execution still requires actual receiver clock/current binding and source-owner NT_GEOMETRY_TEMPORAL_BINDING for moving-volume/work/coupled-source claims. Original HE native provider/moments/moving-stage/certificate-adapter, RUX and all-Bianchi/D2.3 obligations retain owners. No new global gate, merge, force push or production activation.
