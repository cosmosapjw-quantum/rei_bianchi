# Original REI 26-event 46,080-node common-source physical-mode responses, tick160

Purpose: progress toward B2C2_FIRST_INTERVAL, whose source-original first canonical interval remains BLOCKED at tick [160,161] after 160/131072 accepted ticks. Original strict local-error <2e-4, width <2e-3, conservation and Hummer-Seaton event policies remain unchanged.

Immutable base: PR327 HEAD bedcc1d740fec8c75bb356bbb8c803236bc1b64a, original PR321 HEAD 9afee1ab4a45a7b4b277e183e7e18c59a8d39f4d, original source tar SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, original state array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01.

## Construction and physical conservation

At each actual original node choose a nuclei-conserving point p0 inside the original accepted marginal parent population enclosure and the source logT midpoint x0. Construct four one-parameter coherent curves y(a)=y0+a*v, a in [-1,1]: H I -> H II, He I -> He II, He II -> He III, and logT. For each species transfer, use 0.2 times the minimum slack to every affected original bound in both signed directions, ensuring all curves reside within the parent box and conserve H and He nuclear totals exactly. For logT take 0.2 times each node's minimum x0-to-bound slack. Each mode is controlled by ONE shared scalar a across all 46080 original physical nodes.

For the original thermodynamic state, x_e=(N_HII+N_HeII+2*N_HeIII)/N_H, U_thermal/H=(3/2)*k_B*T*(N_H+N_He+N_e)/N_H, and U_ion/H=[chi_H*N_HII+chi_HeI*N_HeII+(chi_HeI+chi_HeII)*N_HeIII]/N_H. These equations are dimensionally explicit and use the original nuclear/energy source conventions. Under either a H or He transfer at fixed temperature, d U_thermal/d (N_e/N_H)=(3/2)*k_B*T, confirmed symbolically with Wolfram.

At nine physical source parents per original lane (center and ± four modes), evaluate the immutable 26-event source electron production and photon heating plus exact interval photon/energy and nuclei identities. Separately evaluate actual original MPRK22(1)/Alexander SDIRK2 full, first-half, second-half for [160,161] at the SAME physical parent. For each point, D_h lies in original model output intervals [F_lo-H_hi, F_hi-H_lo]. Compare *physically coherent mode sensitivity* to the center, not independent extremal parent boxes.

Do not infer a rigorous derivative over X from differences of independent source flux interval midpoints. The union of four 1D curves does NOT cover all admissible 46k-dimensional parent or shared source uncertainties, and the original three shape lanes share an accepted numerical state; they do not represent three measured samples. No accidental `D_h(X)` certification, tolerance change, all-type Bianchi observable, or production promotion.

## Execution and publication

One isolated Draft PR from immutable parent #327 with source mode code, tests, this theory and one 20-step R1–R10/C1–C10 ledger. A 3-lane GitHub Actions matrix executes the actual full source, attempts map on all nine physical source points, and preserves CSV + JSON and exact SHA for each lane. Existing original code, source archive, production IVPs, main, sibling PRs and budgets remain read-only. A new scientific result is admitted only to the precise scope demonstrated by real CI and binary readback.

Before admission: REI central 28/88 reported, working 33/88 reported, F4 4/7 reported; canonical delta 0, full first interval HOLD, auto-next false. After this bounded source experiment, the next most decisive step remains constructing an all-X joint correlated original 26-event difference-map Jacobian/remainder and testing the locked [160,161] step for all original shape lanes. No PR factory or repeated process audit.

Primary methods background: validated ODE interval/affine arithmetic and Lohner techniques, and Izgin et al. on positivity-conserving modified Patankar Runge Kutta dynamics. The live original REI 26-event implementation, not these papers, is the physical source owner for this run.
