# Root frozen implementation and execution contract

Unit REI-THERMAL-ASSIMILATION-20261027. Root freeze 2026-10-27. Baseline ee94bef85b56d879dc38f184856a5c613575e9e1; additive branch research/rei-thermal-assimilation-20261027 current8057f121d7ba6adc4abebd96b06ed3ab2c38092f. Latest working AGENTS blob6464cd96b7023e3e91e30246bc93650d4e435a10 re-read. Centrala5db4bac remains27/88, working32/88; no original-node completion from this unit. Three parallel intake/theory returns and R1 Drive/Dropbox ACKs have been read. Native desktop remains offline.

## Frozen model and exact reuse

Adopt theory/THERMAL_JOIN_DERIVATION.md sections1–9 and theory/R6_PREFLIGHT_REVIEW.md, with the clarifications below. Keep the native21 Y plus zeta,w_nt,w_ext,logT coordinates. Proper-time source only; homogeneous expansion and transport remain owned by their original callers. Use the saved PW19 HeII z=2.479 background and the existing source class/25-state photo component/JVP. Reuse existing moment/snapshot bytes without any quadrature or interpolation.

Declared relaxation is constant in energy: partial_t mu_nt=−nu mu_nt. Freeze nu*=8.160348695705333e-18 s^-1, numerically equal to the saved H but an independent prescribed parameter for all derivatives. This is a CONDITIONAL_SELECTED_CLOSURE, with physical rate/uncertainty null. Freeze the constructed fast pool zeta*=q·Y/4 and w*=zeta*K_J/Gamma; its moments are manufactured on the real saved background, not a recovered cosmic trajectory. Source support remains0..49945.58eV.

Freeze native RR kinetic closure mao2017 (existing hybrid), native DR kinetic-loss fit and all original masks/domain; use unchanged ThermalSources.coefficients(T). Freeze native planck_reference Compton with Tr=2.7255/a, its own blackbody energy density and constants. No UV Compton branch. Do not call ThermalSources.evaluate, whose prompt heat/all-electron assumptions do not apply. The old photo helper's full-network RR/DR side outputs must not be used in the joint thermal rates.

Bind the actual unchanged HE monatomic_caloric and temperature_rhs with21 ion rows plus one thermal-electron row, common rest frame, zero expansion/shear/divq for this increment. Ion sources are nb(P+R); thermal electron source is nb(q·R+nu*zeta); centered thermal power is nb(nu*w+qC−L). Compare returned Tdot/T to the new source row. Binding, nonthermal energy, and signed external photon ledgers stay separate and single-owned. Inherited WU event/REC opacity/CR source/BASS transport/VigilODE client results remain reusable within their exact existing domains; do not call a new25-state derivative certificate a reused V6 result.

## Domain and maps

Accepted points have nonnegative finiteY, A·Y=1 at inherited2e-14 scaled tolerance, neutron/tritium indices0,5,6 exactly0, T in[100,1e6]K, nb,a,H>0, nu/lambda>=0, 0<=zeta<=q·Y, 0<=w<=Emax*zeta, chi=(1+q)·Y−zeta>0. No clipping or renormalization, no nuclear decay activation. Positivity of every signed DR fit summand is not required; preserve native total positivity/absent/underflow distinctions.

Reference normalization is r=r0*a^-3, nb=beta*r; x=betaY, xi=beta*zeta, omega=beta*w. Multiply only density-like first24 source rows by beta or nb. Leave logT unchanged. Apply 1/H to all25 rows in eta time. For reference-input tangents use dY=(dx−Y*dbeta)/beta, dzeta=(dxi−zeta*dbeta)/beta, dw=(domega−w*dbeta)/beta (and analogous signed external ledger). dbeta=A·dx. Preserve the general physical-reference correction Fx=(S−xRr)/r and dFx=(dS−Rr*dx−x*dRr)/r−Fx*dr/r in a labeled algebra control; it does not activate an alternate cosmological background or infer omitted kinetic pressure work.

## Changed-unit controls and fixed residual scales

One prepared network, one coefficient helper, cached inputs only. Source-off, nu0, empty fast pool, g0 boundaries; reject unsupported T, wrong owner, invalid reservoir support and nonzero n/T. T=Tr zero-Compton control uses native Compton helper ALONE, since the actual9.48K lies below RR/DR support. Do not evaluate the joint REC system at that temperature.

At the controlled positive state choose isotope-preserving abundance direction: for H1(1,2), He3(8,9), He4(11,12), v_lower=0.1*min(Y_lower,Y_upper), v_upper=−v_lower, all other entries0. Set dzeta=.1*zeta, dw=−.07*w, dell=.04, dnu=.08*nu, dlambda=.05 (lambda*=1), da=.02*a, dH=.06*H. For the fixed-r0 normalization choose dbeta=.07*beta, dr=−.06*r, dnb=.01*nb, which satisfies dnb=r*dbeta+beta*dr. Reference directions are constructed from these independent native tangents. No assertion nu=H is made under these variations.

Freeze centered FD h=2e-4. A second h=1e-4 on the SAME direction is authorized to report local step sensitivity and distinguish cancellation/truncation/implementation error; no full Jacobian or inherited-suite replay. Both use the unchanged2e-8 criterion. Algebra/invariant/native-component/HE checks use inherited2e-14, scaled by the sum of absolute nonzero contributing operands in the SAME row units. JVP/FD scales must be built in advance from absolute analytic contributing tangent terms, with the same scale at both FD steps, not a scalar count norm or max(1,tiny). If that contribution scale is exactly0, compare the corresponding exact-zero expectation explicitly. Do not change acceptance tolerances after viewing output.

Discriminators must expose all-electron instead of thermal-electron RR/DR/Compton, omitted caloric particle-transfer term j/chi, wrong multiplication of the nonzero logT row, and omitted density/reference/clock derivatives. Retain the two-measure energy-dependent-rate counterexample as a conditional moment limitation, not a strong no-go.

## Execution limits, cumulative accounting, stopping

C5 code authoring is authorized after this freeze. Scientific execution requires root's separate GO after preexecution source/checker hashes are recorded and the preimplementation stage package is acknowledged. Exact command from the recovered repository root:

    /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 research/rei_expanded_event_consumer/thermal_assimilation_20261027/implementation/run_bounded.py

Only new check_thermal_join.py is invoked. No pytest discovery, cargo, old83/new83/NCP/IVP, spectral integration, old source reconstruction or repeated completed checks.

Combined bounded wrapper+child CPU allowance<=1.5 s; predicted<1s. Child profiling timer<=1.25CPU s with OS RLIMIT_CPU2s backstop; wrapper profiling allowance<=0.20CPU s, preserving a small timer/tail margin within1.5s. Whole wall8s, child address-space512MiB, one worker and all BLAS/OpenMP threads1. Use completed-child rusage/wait4 and wrapper process CPU, not /proc parsing. Record actual measured child+wrapper debit and explicit conservative tail reserve; unexplained unmeasured work remains UNKNOWN_NOT_ZERO. Failure or overrun stops the unit; return root with raw bytes, no blind retry. A diagnosed repair needs one bounded root authorization.

Prior planning debit12.196274495CPU plus measured vendor-copy0.005487141 remains. New temporary planning cap14.9 is49% above ORIGINAL10; restore10 after unit without resetting debit. Presentation cap44.5 is48.333% above ORIGINAL30, prior30.360058297 preserved; stage ZIP/figures tracked separately. Main595.225063/600 NO_MORE_IVPs. Other historical campaign usage/reservations, including HE101reserve0 and unknown new83 costs, remain unchanged.

Mechanical executor is the existing compatible agent rei_baseline_intake, actual inherited Astra, reused after previously observed thread-limit rejection. No new lower-tier identity is claimed; root does not implement code. Theory/source reviewers independently inspect the changed code and raw outputs. Required next transition: successful new check and independent review → conditional source admission + expected-SHA publication + stage/source ZIP dual ACK + original-DAG partial observation. Any full network/L4 transition remains outside this finite unit.

