# REI original 26-event nonlinear tick160: executed source-owned point-parent experiment (2026-11-01)

Protected parent: REI PR325 HEAD 71aaf820b865f98218046e72931805874498fa5e, original PR320 owner e5836fc4b8804d1bcdcdcbb97ab33f822703fa46. Source frozen archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b. Original 46,080 nodes, 3 distinct lane names, historical 3 accepted endpoints through tick160 of 131072. Original rejected [160,161] logT full-half cross-box upper 2.1245050576368385e-4 vs unchanged strict 2e-4. Width gate 2e-3 unchanged.

## Actual experiment
Execute PR325's previously NOT_RUN source-locked point probe with full original 26-event MPRK22(1) population, Alexander SDIRK2 thermal, original photon source with four sites, for [160,161]. One element-conserving parent candidate is chosen within the accepted interval coordinate box. On each lane, one full and two half maps return certified output enclosures; the difference is bounded by independently subtracting their OUTPUT boxes at this chosen candidate point. This is not the original complete uncertain parent set, not a new full IVP and not a joint source-correlated difference bound.

Original legacy PR320 JSON recorded a malformed **63-digit** source-array SHA256. First CI failed at the exact SHA check in all lanes without entering the physical step. The diagnostic second execution measured the 64-digit body SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01 in ALL THREE lanes; source archive and source kernel locks still matched. A targeted fail-closed literal correction, no source substitution, fixed this.

**Actual new calculated data**: 3 × 46,080 = 138,240 lane-labelled output rows, 46,080 unique spatial nodes (not independent observed samples). Maximum common-point full/two-half output box difference upper:

| Quantity | maximum | median | p99 |
|--|--:|--:|--:|
| log T | 5.948382018061694e-7 | 6.298201959964446e-10 | 4.991920885544233e-7 |
| xHII | 3.1850899473440115e-8 | 4.798461628041651e-11 | 2.824140810098186e-8 |
| xHeII | 1.8090141229443193e-7 | 1.9958490415916688e-10 | 1.5362120045048225e-7 |
| xHeIII | 5.936515168336599e-12 | 1.4745149545802863e-17 | 1.6235584925083925e-12 |

Previous failed upper / new candidate max logT upper = 357.1567951059602. It is NOT the actual full-parent integration overestimate factor. Original inherited parent logT width max 1.720930111712361e-4. Across original nodes descriptive corr(parent width, candidate logT upper) = 0.9463642366622657; NOT a Bayesian covariance nor proof of shared source uncertainty. Results for PRIMARY and SCRIPT lanes byte-identical; RECOMB differs at most 3.55e-15 on numeric fields.

**Observed execution**: GitHub push workflow 41268654741 3/3 lane SUCCESS, PR workflow 41268658981 3/3 lane SUCCESS, general verify 41268659119 SUCCESS; 6 Python unit tests normal + 6 with -O per lane. Actual original GitHub Actions artifacts (downloaded and independently checked CRC/SHA/46,080 numerical finite rows each):
- PRIMARY ID 13068328626 SHA256 4ef7e0d8faeb55fac440898b27d90f6d811fb06b51fb898d93d57c66d643792d
- RECOMB ID 13067937929 SHA256 73acaa0d4fa2c0128d5e5328231f40e64228a7209690942e382d8e65e564a06d
- SCRIPT ID 13068515996 SHA256 a2c4f367c70b6de8283c38e67c9809343742901b24c0983b254c685c4e92871b

Independent readback script does NOT import REI integrator and validates all 138,240 data rows. Historical failed source-ID attempts are preserved. Same-context hostile review, not independent author.

## Needed next mathematical/physical result
Define D_h(x,theta) = F_h(x,theta) - G_1(G_0(x,theta),theta), where G_0, G_1 are the original consecutive half maps at their correct times and theta includes all shared photon/source/clock inputs. Then D_x=F_x-G_{1,x}G_{0,x}, D_theta=F_theta-G_{1,theta}-G_{1,x}G_{0,theta}. A certified full-parent difference requires joint derivatives plus remainder over the original correlated source set, respecting four source sites, implicit roots and all budgets. No such certificate was executed here. The candidate point may not be reachable within the true source-correlated parent set. Do not promote [160,161] or full canonical interval.

REI CENTRAL=28/88, WORKING=33/88, PHYSICAL_FAST=4/7, canonical Δ=0. FIRST_INTERVAL=BLOCKED_MINIMUM_STEP. PROD HOLD; NO_MERGE; NO_FORCE_PUSH; NO_MORE_IVPS; AUTO_NEXT_NODE=false; no tolerance or budget change.
