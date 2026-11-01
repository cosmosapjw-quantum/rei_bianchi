# REI Physical Fast F05 | Original 26-event one-tick thermochemical energy balance

## Authority / mission (R1-R3)
Immutable parent Draft PR343 HEAD 84dde55018273a63fad0f49183a4ace09e7a63bb, original PR328 a85312cde63e5c0b0a7c0e5d182e79fe593bcf53. Original archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, accepted array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01, original 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644.

Original tick 160/131072, 46,080 H/He source spatial cells, 3 source shape lanes. Frozen cross-output logT error 2.1245050576368385e-4 > unchanged local limit 2e-4; public width gate 2e-3. Central 28/88, Working 33/88, Fast 4/7, canonical delta 0 until original interval accepted.

North star: advance native IGM thermal history, then Bianchi/observer transfer; no more generic source-only PRs. PR337 instantaneous 12 source-site rates; PR343 full parent site input probes; PR344 thermal-root conditional partial; PR345 MPRK predictor moment response. The unique target here: **original integrated thermal/photoheat and root energy balance for full versus two half steps** on the same source-locked entire uncertain parent. It is NOT another global-photon derivative study.

Primary literature: Chapoutot, Dit Sandretto, Mullier, Validated Explicit and Implicit Runge-Kutta Methods, Reliable Computing 22 (2016) 78-103. Their general verified RK framework does not certify this REI implementation.

## Exact discrete source-energy derivation (R4-R5)
Original source 5-species particles per node p=(HI,HII,HeI,HeII,HeIII), gas kinetic energy in erg per cell:
    N_part = HI+HII+HeI+HeII+HeIII+HII+HeII+2 HeIII;
    U(p,T)= 3/2 k_B N_part T.
Original thermal source per cell, in erg/s:
    R = Q_primary_photo + Q_OTS_resolved - C_native_cooling - 3 H k_B N_part T.
Q_primary and Q_OTS are original event-box photon/OTS sources; no new chemistry or externally supplied rates. The chemical, escaping and unresolved energy ledgers are separate and do NOT imply conservation of cosmic total radiation plus gas energy.

Original gamma=1-1/sqrt(2) in Alexander SDIRK2, time h (seconds):
    U_gamma = U0 + gamma h R_gamma,
    U_final = U0 + h[(1-gamma) R_gamma + gamma R_final].
Source-specific discrete integrated photoheat:
    I_Q[h]=h[(1-gamma)Q_gamma+gamma Q_final].
Half steps each have duration h/2 with their native source sites. For a common original parent, an exact discrete formal identity follows:
    Delta_U = U_full-U_twohalf
            = (I_Q_full-I_Q_half1-I_Q_half2)
             -(I_sink_full-I_sink_half1-I_sink_half2).
This is an exact identity on a smooth simultaneously realizable stage solution, but arithmetic on separate interval image boxes loses shared parent/forcing correlations. This standalone identity does NOT prove a 26-event all-X difference map Jacobian, a uniform remainder, or [160,161] acceptance. Wolfram exact symbolic expansion returned {0,0,True} for decomposition residual, weight normalization and gamma in (0,1).

Original OTS-only source ledgers at each of the gamma/final event evaluations must each enclose
    chemical_energy + resolved_heat + escaped_energy + unresolved_energy = 0.
Primary UV photons contribute separately. Report rates in erg/s, integrated per-node source in erg, H-normalized source in erg/H, T in K, and original proper clock in s.

## Computational form and scientific admission (R7-R9)
Use original SHA-locked run_step without source modifications on the original tick160 *full uncertain interval* for full, half1 and half2 (half2 starts at original half1 interval image). Passively record original event_box and thermal_root calls. Last gamma/final native thermal-root RHS is the contracted interval RHS used by original SDIRK2, and original gamma/final event objects supply source rates and OTS/energy ledgers.

At each map and each of 46,080 cells compute native I_R, integrated Q_primary, Q_OTS, resolved/chemical/escape/unresolved ledgers, remaining sink Q_photo-I_R and independent-box energy residual U_out-U_parent-I_R. Per-cell residual enclosure containing zero is necessary for a valid root, not proof of global all-X source correlation. Separate true 46K source rows from replicated 3-lane labels, and weighted H-nuclei totals from unweighted cell medians.

Any native map or source identity failure remains a named failure; source experiment may return a partial trace. No original full IVP, table branch override, gate relaxation, budget reset, production, automatic next node, merge or force push.

## Same-author adversarial drift watchdog (R6 / R8)
Main candidate failure: integrated heat variation could be small while the original logT enclosure still violates 2e-4, since independent interval differences contain wrapping uncertainty and competing cooling/expansion. Never admit canonical or Fast node progress from a source budget alone. Positive result for this bounded unit means a new actual original 46,080-cell source-authentic integrated thermal/energy budget and root consistency check, distinct from instantaneous photon atlas. After obtaining it, terminate this auxiliary unit; return directly to the source/thermal/table-coupled common-parent D_h interval Jacobian and VALIDATED uniform remainder, not another energy-budget variant.

User requested serial self-adversarial review, native subagent NOT_RUN and distinct-author blind review NOT_RUN.
