# Non-tilted Bianchi I Sigma–Pi pilot: frozen contract

Controller: /root (Astra, as supplied by runtime). Date: 2026-10-21 UTC.
Goal: deliver actual first preliminary parameter-sweep plots today, with additive code on existing PR198 branch. This is an explicitly scoped self-gravitating collisionless LRS slice of non-tilted Bianchi I, using original REI PR145/147 physics. Full native H/He feedback is a separate unfinished scientific target.

## Immutable inputs and allowed paths

- Publication base: cosmosapjw-quantum/rei_bianchi PR198, branch research/rei-lrs-v14-physical-birth-20261018, expected HEAD 3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8 (recheck before fast-forward).
- Physics source: PR147 HEAD 3b85dedce84d37b3e165da00685a8a984950aafe; PR145 canonical_fv.py SHA256 91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5.
- Copy EXACT original canonical_fv.py, species_hierarchy.py, lrs_boltzmann.py and REI_BACKGROUND_FAMILY_LOCK.json from verified intake into vendor/ in new subtree research/rei_bianchi_sigma_pi_pilot_20261021/. Record original paths, SHAs and attribution. No original native Rust, provider, pin, tolerance or campaign modifications. No new clone/worktree, no owner checkout reset/clean.
- Local implementation root: /workspace/scratch/2fa07aa7079c/bianchi_pilot_20261021/repo_payload/research/rei_bianchi_sigma_pi_pilot_20261021/.

## Physical convention and model

Metric signature (-,+,+,+), cosmic proper seconds; a_perp=a exp(-b), a_parallel=a exp(2b), s=db/dt, sigma=diag(-s,-s,2s). Preserve the repository half-contraction norm |T|=sqrt(T_ab T^ab/2), hence Sigma=sqrt(3)|s|/H. Frobenius norms are sqrt(2) times these values and must have separately named columns if output.

Stress pi=diag(-p,-p,2p), p=(P_parallel-P_perp)/3. In SI cosmic-time equations K=8*pi*G/c^2; Pi=sqrt(3)*K*|p|/H^2. This equals kappa_E*|pi|/(H/c)^2 with kappa_E=8*pi*G/c^4; never confuse the old pressure column with dimensionless Pi or the shear-equation coefficient K/3 with K.

Einstein equations: 3H^2=K*rho+Lambda*c^2+3s^2; ds/dt=-3Hs+Kp; drho/dt=-3H(rho+pbar)-6sp; dH/dt=-K(rho+pbar)/2-3s^2. The constraint propagates exactly under these equations.

Use original cosmology/clock lock, zbar20→4, original dust+Lambda+radiation partition. Nonbaryonic positive canonical massive fraction fm=.1, mass/Tref=30, massive angular amplitude A_m=0, 24x12 cells, Gauss3. Initial massless brightness W=1+k*P2(mu), shared gamma and nu k, no donor/Thomson, no stellar/ionizing sources. This freezes stress composition rather than treating the two tensor magnitudes as complete initial data for general Bianchi I. Reflection-even LRS, gamma/nu L8, their energy histories coincide. Massive anisotropic stress may develop through metric evolution and remains in Einstein feedback.

Grid: Sigma0 and Pi0 nonnegative each 13 values including 0, maximum Sigma0=.004, Pi0=.001; signs eps_sigma and eps_pi independently +/- for nonzero values, only one representative at zero. Thus 25x25=625 distinct signed initial conditions. Explicitly validate that |k|<=.5. Compute target physical Sigma0 and Pi0 from actual initial fields, including any finite quadrature offset. For the ideal normalized isotropic massive input: q=s/Href=eps_sigma*Sigma0/sqrt(3-Sigma0^2); signedPi0=(sqrt(3)/5)*(H0^2*Omega_r/a_ref^4)/H_initial^2*k. Check realized axes to absolute 1e-12. Never plot q or k as physical Sigma or Pi.

## Optimization to implement

An additive reduced solver, preserving original massive-moment helper and energy-matrix even block. For identical collisionless gamma/nu IC, their energy vectors remain equal; odd multipoles remain zero; number multipoles do not feed geometry or energy. Evolve (tau=Href*elapsed_t, b, v=s/Href, E0,E2,E4,E6,E8): 8 instead of 40 states. Original number monopole is analytically conserved; higher number moments are not requested or claimed computed.

With x=ln(a/a_ref), a=a_ref exp(x), R=Omega_r/a^4, M=moments(x,b), H^2=H0^2*((1-fm)*Omega_m/a^3+fm*Omega_m/a_ref^3*M.rho+R*E0+Omega_Lambda)+(Href*v)^2. p_norm=R*E2/3+fm*Omega_m/a_ref^3*M.pi_s. Then tau'=Href/H, b'=Href*v/H, v'=-3v+3*H0^2*p_norm/(Href*H), E'=(Href*v/H)*M_even*E. Keep DOP853 rtol=3e-11 atol=3e-13. Original full solver retained as reference only.

Reuse read-only matrix/quadrature objects within each worker; use source moment_batch for bounded vectorized history diagnostics where useful. Independent trajectories use a process pool; BLAS/OpenMP threads=1, no solve_ivp(vectorized=True) ensemble shortcut. No detailed timing comparison or speedup claim.

## Minimal validation and acceptance

1. Six cases comparing full source and reduced histories (65 samples): (Sigma0, signedPi0, eps_sigma)=(0,0,0),(0,+.001,0),(0,-.001,0),(.004,+.001,+1),(.004,-.001,+1),(.004,+.001,-1). Compare b, signed s/H, E0, E2 and signed dimensionless Pi: max absolute 1e-8. Source constraint <=2e-13, positive finite energy/H, massive populations nonnegative; compare full source number monopole to 1 <=2e-10. Record all actual metrics, no bitwise claim.
2. Initial physical-axis realization <=1e-12 absolute; reject unrealizable k without altering target.
3. Two largest opposite-sign corners L8 vs L12: endpoint Sigma, b, E2 absolute discrepancy <=1e-7, a scoped angular-truncation check. One corner tolerance /10: <=1e-8 same observables. These are accuracy checks, not a benchmark campaign.
4. Check massive moment directional finite-difference energy identity at interior x for a few prescribed (b,w), where w=db/dx=s/H is the direction, distinct from the state v=s/Href: d rho/dx=-3(rho+pbar)-6w*pi_s. Evaluate moments(x+h,b+w*h) and moments(x-h,b-w*h), relative residual <=1e-7, h=1e-5. Preserve failure and return to controller if substantive. This wording correction follows independent reviewer clarification before execution.
5. Save sampled minimum reconstructed angular brightness; a sampled check only. Isotropic control should retain |s/H| and |b| <=1e-12.

## Execution, shared resources, and stop rule

New user authorization covers this bounded pilot, separate from old V12 cap/debit and prior read-only SSH documentation contract. Preserve V12 cap180 and debit200.39897231891518 without refund. No replay of its remaining100 or AGE completed runs.

Here: max workers=min(available affinity/cgroup CPU quota, memory bound, observed spare CPU, 8). New pilot max wall900s, aggregate child solve wall3600s; no auto retry. NCP command supports max64 workers with same independent caps, memory-reserve and nominal256MiB/worker. Account for cgroup/host memory, use brief /proc/stat CPU sampling; log resource observations and selected slots. Reassess available resources between batches. Other active Codex/jobs are not a blanket blocker. Do not terminate unrelated processes. If CPU fully busy, at most one lower-priority worker can make bounded progress when memory permits; low memory is a resource-specific deferral, not proof that scientific work failed. Avoid nested BLAS pools. Preserve actual child logs/outcomes and completed rows; resume only matching case/config/source identities, no silent retry of failed rows. No overwrite of old results.

NCP preferred connection: ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22. Sandbox key currently absent; Desktop Commander returned monthly usage exhausted. No authenticated NCP execution yet. Produce working copyable commands; do not request user manual downloads or SSH/SCP.

## Deliverables and review

Actual local raw histories + endpoint table, 4-panel Sigma_end heatmap with independent signs and physical Sigma0/Pi0 axes, representative Sigma/Pi evolution plot, execution stdout/stderr/exit/command/environment receipt, minimal validation metrics. Add finite resource-aware NCP command and next-thread prompt. Stages R1–R10,C1–C10/DAG reflect actual work; publish and backup at meaningful intake/contract and implementation/results milestones. Independent nonimplementing Astra reviews actual diff/raw before scoped publication/admission. Pilot is preliminary; no new production admission, general-Bianchi closure, native HHe convergence, 64-core speedup or full positivity claim.
