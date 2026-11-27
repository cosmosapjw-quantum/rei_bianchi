# HE18 warm P01 stored-source 16-cell optical-depth history

2026-10-15 KST. Actual local coding + source-scoped scientific execution.

## Scientific result

BASS_HE previously certified 7 finite-source warm P01 slabs. In this continuation the remaining 9 slabs 8–16 were actually evaluated, assembled and strictly checked, yielding all 16 stored source time intervals, proper t from0 to1e11 seconds. Each slab has width6.25e9 seconds, original global Bianchi-I shear clock, four gas and2904 photon error variables.

Final cumulative Thomson scattering-out optical depth:

1.27998310917642936032734511983425822491e-7
  <= tau_16 <=
1.27998310917643067537790506329945423459e-7.

The first-scattering probability is 1-exp(-tau). Its numeric midpoint is approximately 1.27998302725859553e-7. Exact positive successive photon/gas error transport confirms all 2904 source photon components at the 16th saved boundary. Last comparison gain about0.002305235723489<1; full original gas-domain occupancy about0.3501393721241<1. 784 exactly zero-opacity channels persist in the source data.

## Frozen source/physical conventions

Original rei_bianchi finite warm source commit a5c958c414dea41216b445c05f58df837f05cacb; BASS_HE predecessor PR63 commit a3eeff91eb9d0c2ba42d553cfda7eab7ecbc53ef. Non-tilted LRS Bianchi-I, metric(-,+,+,+), explicit c,hbar,k_B and CGS source conventions, HM12/FT03 Case-A: 3CI 3RR 2DR and photoabsorption. Ray redshift uses original epoch integrated shear b(t)=integral_0^t sigma dt, not restarted per saved slab:

E(t)/E_init = sqrt(exp(2b)*(1-mu_init^2)+exp(-4b)*mu_init^2)/a(t), a(t)=V(t)^(1/3).

Two previously saved P01 source endpoint RHS calls per slab generated Hermite slopes. The full source ODE was NOT re-integrated. The code performs source-scoped rigorous-conditional interval/Taylor photon processing and positive rational error comparison over the saved original trajectory, rather than a new coupled cosmological time evolution.

## Execution and verification evidence

1. Cells 8–16 each passed eleven exact-rational/scoped scientific checks, all upstream hash, proper-clock, positive comparison-gain and gas/photons constraints. Every end output has length2904 photons plus four gas error components.
2. Independent full-source chain verification validated 9 of9 new slabs against the correct predecessor certificate and outgoing SHA256, original data, exact accumulation of individual tau intervals, and contiguous original proper-time steps. All 16 saved source slabs are now accounted for with the earlier C1-C9 evidence.
3. Two independently running capped processes executed midpoint/whole per slab, one OMP/BLAS thread each. Mean measured wall for these two scientific domains was about12.8425s per new slab; exact Fraction assembly mean about15.0957s. Total time for the new nine source-scoped slabs with staging/verification ~462.55s. Original source ODE runs0. The accurate per-cell resource ledger is in results/PERFORMANCE_AND_CROSSCHECK.json and the private runtime.
4. Public regression tests7/7 pass. Local Wolfram15.0.0 with genuine xAct/xTensor1.3.0: eight kinematic tensor groups and nine exact-zero residuals (null rays, screen projection, LRS shear/redshift). This is a sign/kinematics check, not an independent proof of the mpmath.iv numerical backend.
5. Full numerical history CSV + two independent 2-D source-scoped figures are provided publicly. They do NOT show physical ionic fractions; separate true EoR H/He abundance plots still require rei_bianchi AXBI source/history validation.

## Important independent numerical scale check

Using the original stored 17 electron-density snapshots and a plain trapezoid integration gives tau_trap =1.27998310917657906836026022388521941006e-7. This differs from the source-scoped rigorous-conditional midpoint by approximately1.49050507635e-20, relative1.16447246e-13. This alternate approximation lies OUTSIDE the exceptionally narrow 16-cell source-scoped interval: it is therefore solely a scale sanity check, not a claimed independent interval containment or exact equality. See numerical crosscheck receipt.

## Scientific status and next work

SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES. All16 finite P01 stored cells were processed, but the actual cosmological H I/H II and He I/He II/He III and Tgas histories, physically calibrated emissivity, matched signed-shear versus FLRW scenarios, observer visibility, source-model uncertainty, independent mpmath.iv backend correctness and native binary64/provider roundoff are NOT completed or claimed. The live rei_bianchi owner PR117/118 remains separate and unchanged; use the completed P01 optical integral only when physical source/clock/closure relations are explicitly justified.

Source-private evidence is preserved separately and should not be published as unredacted 2904-dimensional radiation tables or NPZ on GitHub. Native subagent NOT_RUN (unavailable), separate local Codex NOT_INVOKED. The user-requested current physical research next targets independent AXBI abundance history/scenario convergence rather than silently promoting this optional warm source-scoped optical result.
