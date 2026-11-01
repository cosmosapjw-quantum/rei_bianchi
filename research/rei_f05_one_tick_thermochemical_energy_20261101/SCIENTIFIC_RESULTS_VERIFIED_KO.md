# REI Physical Fast F05 | Native original-26-event discrete thermal-energy experiment (verified 2026-11-01)

## Source, goal and exact immutable scope

Draft PR #347, code commit e3e8ba08b3a6a0d8873549bf47e8fadd435ac83c, baseline PR #343 exact SHA 84dde55018273a63fad0f49183a4ace09e7a63bb; original parent PR #328 exact SHA a85312cde63e5c0b0a7c0e5d182e79fe593bcf53. Original frozen 2026-08-29 source archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b; original accepted numerical array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01; original 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644. Accepted tick160/131072; exactly 46080 unique H/He spatial cells, three originally labeled source lanes sharing original matter state. Four original source evaluation sites per nonlinear MPRK22(1)+Alexander SDIRK2 full/half/half map, original clock and gates unchanged.

Scientific objective is ORIGINAL ONE-TICK INTEGRATED GAS THERMAL ENERGY and native source/rhs bookkeeping, not another instantaneous photon-source Jacobian or point-parent atlas. Scope is an enabling physical science experiment, not completed F05. Exact original logT first full-parent cross-output 2.1245050576368385e-4 exceeds unchanged strict 2e-4; public box-width gate 2e-3, production HOLD.

## Derived discrete identity and what it does NOT imply

With gamma=1-1/Sqrt[2], N_particles=HI+HII+HeI+HeII+HeIII+HII+HeII+2HeIII per original cell, U=3/2 k_B T N_particles in erg/cell, original native SDIRK2 final root solves U_final=U_initial+h[(1-gamma)R_gamma+gamma R_final], where R=Q_primary+Q_OTS_nonnegative-C_nonphoto-expansion in erg/s/cell. Full minus two half maps yields formally Delta U = Delta I_photo - Delta I_sink for a common source/parent history. Wolfram exact symbolic residual was {0,0,True}. Separate interval-box midpoint solutions are NOT coupled realizations; do not apply that algebraic identity to their independent interval centers as if it were a measured thermodynamic equation.

## Real physical execution and independent verification

GitHub source science CI https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41286683981: SUCCESS all 3/3 original physical lanes. Independent repo verify https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41286684032 SUCCESS. Each lane: original full, half1, half2 maps native PASS; 4 physical source evaluation sites per map (12 sites per lane); two final gamma/final thermal roots per map (6 relevant native roots per lane); each native thermal-root residual interval contains 0 at all 46080 nodes for each of 3 maps. Test step 8/8 ordinary and 8/8 python -O, inherited 5/5 tests all PASS. Each downloaded ZIP CRC PASS, embedded model CSV.gz SHA256 checked, all 46080 rows and 40 columns, all finite. 3 lane-labelled calculations do NOT constitute independent observational/cosmological samples.

Primary lane 46080-cell aggregate of interval MIDPOINT discrete integrals, units erg, for full vs two half steps:
- total primary+OTS photoheat: full 4.413031346491929e47; twohalf 4.413032685138288e47; signed center difference -1.338646359082138e41
- primary UV heating: full 4.01217202440334e47; twohalf 4.0121724077847785e47
- original OTS resolved: full 4.008593220885895e46; twohalf 4.0086027735351026e46
- nonphoto thermal sink (Q_photo - native RHS): full 3.092297196991433e49; twohalf 3.0922976603640036e49
- native integrated thermal RHS: full -3.0481668835265134e49; twohalf -3.048167333512621e49
- gas thermal energy increment (independent interval center, not a coupled physical trajectory): full -3.048154916562155e49; twohalf -3.0481391099844207e49.

Important: the center thermal-energy difference is not equal to center RHS integral difference. This is NOT a demonstrated physical energy conservation violation: componentwise outward interval images and subtraction do not maintain state/source correlations, and midpoint of an image need not satisfy the original nonlinear equation. Zero inclusion of each original native root residual is necessary for enclosure but does not prove whole-uncertain-source D_h correlation or independent numeric admissibility of those midpoint states.

## Quantitative same-author blind-style hostile audit and drift watchdog

Independent raw ZIP+CSV scientific reanalysis on primary lane:
| Channel in erg/H | Max absolute center full-minus-half | Max independent outer bound | Median outer/center ratio |
|---|---:|---:|---:|
| Integrated photoheating | 1.1304235123136363e-23 | 1.084178280316283e-18 | 2.523057218494304e5 |
| Integrated native thermal RHS | 4.879110481037623e-21 | 6.253870059621455e-17 | 1.2426040224997108e5 |
| Nonphoto thermal sink | 4.868418148932469e-21 | 6.299056766438948e-17 | 3.695502105265991e8 |
| Integrated gas thermal increment | 1.050384294915548e-19 | 1.1098068321783525e-14 | 1.3431754973017048e7 |

BLOCK_NOW applies **only to false promotion to canonical F05:** independent interval bounds grow orders of magnitude beyond center defects; fixed common parent/source and full stage/time correlations, coupled OTS/cooling/implicit roots and table partitions were NOT retained in a validated uniform remainder. Do not claim 2e-4 PASS or physical causal contribution from a midpoint thermal energy balance. The fourth photon group uses subnormal/zero current; it cannot be interpreted as an active resolved photo-source. Same-author hostile review is NOT independent-author blind referee; native subagents intentionally NOT_RUN. The remote global Python gave NumPy-1.x extension compatibility warnings but source calculation exited 0; pinned original CI ran green. These are distinct execution/environment vs physics states.

**Progress-first decision:** New source-authentic integrated-energy data and necessary implicit-root consistency check were actually produced. This is NOT original F05 closure, and the source-only/slice budget expansion path is now TERMINATED to avoid drift and meta-gate inflation. Next only the common-parent/common-Theta original 26-event all-X joint D_h Jacobian with validated remainder can establish the original [160,161] gate; separately source/clock-matched Bianchi-observer physical adapter may progress only if independently authorized.

## Evidence, identity and limits

Primary original Actions ZIP #13075408315 15950424 B SHA256 56135b2e850628f000083e3e2a583482930216543b06406e9d269da33c830c0e, original CSV.gz SHA256 48cf86b594afeaee1916820ea9ff9cb36b178ce8ffa31daf4c84bfc5feea9659.
Recombination original Actions ZIP #13075846721 15949809 B SHA256 3a38f73d97d67f396831bc2cb679ca7ccbef371c9f7901612e8166df2815863a, CSV.gz SHA256 bdb8d8c7518487b6c394f5b26a62509486453b8799065cf50bc8ad6e69af417e.
Shielding original Actions ZIP #13075058717 15949811 B SHA256 6eb79d65fb3dd89b00bbd7173a05dbb173ba85f84777db9f8363235ccabd94bd, CSV.gz same SHA256 bdb8d8c7518487b6c394f5b26a62509486453b8799065cf50bc8ad6e69af417e.
Independent reanalysis JSON can be rerun from source-free ZIP and companion analysis, its raw archive bytes and CRC are not represented by Git source commits.

Original kernel and owner source NOT changed, original main/other active worktrees untouched. Published parent science theory checkpoint 1949da5732f561d2d3d50791ea2197e10622068c and code/CI checkpoint e3e8ba08b3a6a0d8873549bf47e8fadd435ac83c, with remote branch readback. GitHub Actions artifacts have limited retention; this text/report/source-free package preserve independently downloadable copies, but do NOT claim Google Drive or Dropbox second-provider binary readback without actual provider ACK.

Current reported DAG in every R/C stage: CENTRAL 28/88, WORKING 33/88, Physical Fast 4/7, canonical delta 0; original first canonical interval BLOCKED_MINIMUM_STEP, PRODUCTION HOLD, NO_MERGE, NO_FORCE_PUSH, NO_TOLERANCE_RELAXATION, NO_BUDGET_RESET, AUTO_NEXT_NODE=false. No true physical node acceptance from 20 stage ledger entries.
