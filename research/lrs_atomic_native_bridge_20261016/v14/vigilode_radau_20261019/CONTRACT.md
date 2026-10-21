# C1-C4 native VigilODE Radau continuation contract (2026-10-19)
Root scientific owner: /root (Astra). Bounded code/run delegated to lower-tier agent. Fresh read-only Astra review required before admission.

## Frozen inputs and boundary
- rei_bianchi PR198 HEAD fa9615a565a10a770eb1768d8f10cd503b0e1336; numerical source publication 339dab4336d1fcfd38106640ee9bf7056dabcfd8 is resolved by the existing /v15_work/final_c10/FINAL_REMOTE_ACK.json and prior manifests.
- Existing native input directory: /workspace/scratch/6af5e9e6c737/v15_work/native_owner/rust/rei_microphysics
- VigilODE immutable 8a8bd409b1d96c7b7421f496d229e119fd3d284e at /workspace/scratch/6af5e9e6c737/v16_work/vigilode_intake/immutable_8a8bd_source. crates/manifests are byte-identical to newest observed research PR71 HEAD 0bab431e1031f86eb3ddb44371240bce49ae2376.
- Rust1.94.1 toolchain: /workspace/scratch/6af5e9e6c737/v15_work/toolchain/bin
- No clone/worktree. Immutable inputs can be staged, preserving prior files. No external push by code agent.
- Production/default/adaptive/checkpoint/MD14/Verner/Grackle/EOS and existing SSPRK2 byte contents remain preserved. Add one transport child module + appended module hook only; put the VigilODE adapter in a standalone research crate, using path dependencies.
- Intended publication directory: research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019

## Scientific goal
Apply actual VigilODE Radau IIA3 as an opt-in fully coupled native reconstructed photon-moment + 4-gas-variable chemical substep. Compare with existing SSPRK2/gas-midpoint at matched small native settings. Outer geometry maps and actual GL2 birth stops remain the existing physical operations. This is a native discrete-system reference, not a rigorous error bound or universal stiff/high-order claim.

## Differential equation and event ownership
For each prepared native quadrature node l in cell c, n_l per total H, q_l reference energy, k_j=c_physical*n_abs,j*sigma_j:
 dN_c/dt=-sum_l sum_j k_j n_l;
 dUref_c/dt=-sum_l q_l sum_j k_j n_l.
Implement direct node sums in a new PreparedAbsorption method; do NOT recover derivatives by FE(state,1)-state subtraction.
Use precisely native photo gamma and heat-per-absorber sums, AxbiProvider.point(gas,nh,nhe,0,2.7255/a,photo), unchanged rates and EOS.
Return independent absorption event/heat/binding rates from node sums as a consistency check.
Record raw P/C/R/D and CE/RR/DR/FF/signed-CMB/escape; all events /H and energies eV/H. Electron e=x+Y(y+2z), Y=nhe/nh. No hidden clipping, floors, moment renormalization, tolerance relaxation or opacity replacement.

## State coordinates and solver
Fixed geometry per chemical segment, fixed moment support. Exclude exactly empty cells (they remain exactly empty source-free) and encode positive cells with affine scaled number and energy-offset coordinates. Point-support cells need only number. Prefer N/Nscale and (Uref-lo*N)/[(hi-lo)*Nscale]; preserve affine decoder and use direct offset derivative to avoid cancellation. Scales are frozen within the step, declared and positive. Gas x,y,z plus w_eV/positive_frozen_w_scale.
No ledger unknowns need be added to the dense Newton dimension. Reconstruct Radau stages Y_i=y0+sum Aij K_j from returned stage_increments; reevaluate actual native RHS/event rates there and accumulate all ledgers with the same positive b_i and actual accepted dt.
Use OdeProblem::new with an honest domain-aware finite-difference explicit Jacobian (one-sided fallback permitted only for invalid perturbations; every actual native call counted), radau_step, radau_iia3_tableau, WorkCounters from the pinned source. Do not supply fake Jacobian/JVP placeholders.
Independently recompute K_i-h*f(Y_i) and ynew-y0-sum b_i*K_i. Scale residual components explicitly, report max norm in addition to library WRMS. Verify affine invariant defect = weighted physical stage residual to floating precision.
All trial stage and final physical states must pass unchanged native domain and support checks. A library residual-domain Err currently aborts Newton rather than backtracking; preserve first actual failure and stop for root's bounded repair decision if it blocks the chosen experiment.
State transaction: failed candidate leaves physical state and accumulated physical ledgers unchanged; charge calls and attempts. No silent auto-subcycling.

## Physical GL2 wrapper
Use exact root-defined chronological endpoints; log1p((to-old_a)/old_a)/H(sqrt(old_a*to)) for existing split segment dt, geometry_map to midpoint and then endpoint. Birth at a0*exp(c*dln_a), native transport.inject at actual geometry and z=1/a-1, proper weight dln_a*w/H(a_birth). Copy exactly the existing SSPRK2 birth rule/clock. No source integral at a midpoint surrogate.
External adapter can operate public Driver/DriverState/PhotonState fields. Require inactive_hi_split=false for this first bounded lane; it has no passive-boundary coverage. Existing last_clock_rhs is not a consumer of this separate adapter; return explicit reports.

## Finite experiment before expansion
Matched configuration: q=0, transport_cells=8, n_mu=8, threads=1, background_panels=128, existing source energy_subdivisions unchanged, gas fractions [.075,.12,.03], T=15000K; seed original MD14 dt_seed=1e16 s (constructed initial packet, not elapsed cosmological history).
Contract correction: initial n_mu=2 was rejected by the unchanged AxbiSource::angular, whose native allowed set is [8,16,32]. Four initialization failures with zero native RHS are preserved. Root chose the minimum supported8; no source quadrature implementation, physical input or accuracy tolerance changed.
1. Build + focused meaningful tests: direct RHS event/energy identity on actual prepared native source, affine coordinate roundtrip and zero/point support, failed-step transactional behavior, actual stage reconstruction/ledger identity, GL2 birth-clock parity. Do not rerun old 76 manufactured cases or unrelated full suites.
2. Tiny first gate: fixed-geometry seeded Radau N=4 over T=1/k_ref20 with newton scaled atol1e-13, rtol0 (root may tighten to1e-14 if residuals dominate), explicit max native RHS 200000/case and 30sec case cap. Run a single initial case and stop if it fails or exceeds resource estimate.
3. If gate passes: fixed-geometry Radau N=2,4,8,16 (reuse completed N4), matched existing SSPRK2 N=8,16,32. Optional one Radau large-optical-depth attempted step and SSPRK CFL rejection is a diagnostic, not blanket stiff admission.
4. Then source-on GL2 and seeded-disabled GL2 at Xend=1e-6, matched N=4,8,16 for each method, if total incremental native wall remains <=180sec. Root reviews results before any larger campaign. Preserve failed/truncated cases, never count them completed.
5. Save complete command, source+binary SHA, stdout/stderr, exit, exact config, wall, total native RHS (including FD and stage replay), accepted endpoints and per-stage event records; low-volume CSV/JSON. No NCP claim.

## Acceptance / stop
Correct native RHS identities, stage residuals and state-domain checks are necessary. Conservation alone and agreeing endpoints are insufficient for time-accuracy or physical convergence admission.
Compare actual finite refinement differences and absolute cross-method errors using finest available Radau as an empirical reference only if its own refinement supports that use. Report HeIII cancellation separately; no inferred order from roundoff.
If any physics/unit/scale/API unknown arises, stop and ask root, not user. Bound native work before proceeding. Code agent does not grant scientific acceptance or rewrite this contract.

