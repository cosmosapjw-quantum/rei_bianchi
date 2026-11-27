# R5 and C5: Original REI F05 V2 HeII Lyalpha local on-the-spot H/He feedback

2026-11-15 KST. One bounded source-native science unit, not a new RUX04 spatial transport solver or official V2 promotion.

## Immutable source authorities

Parent BASS_HE PR153 head b2de625f0f8976c20ccaa21e62610ae42d8bb750. REI PR369 exact source head 645437697d915da45147071e266bc47937e76f6c. Source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, original 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644, V1 original accepted t160 SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01, research V2 candidates t161 c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823 and t162 35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b. Private NPZ restored from verified parent source-inclusive ZIP to a private research scratch path. No original source files or existing parent worktree changed.

## Physical questions and exact derivation

The previous parent PR153 integrated LOCAL ESCAPING 40.81332-eV He II Lyalpha 0–2.4492444763567325e47 erg across research V2 t160→162. Its complementary photons absorbed locally by original H I and He I are already part of original 26-event chemistry. What are those actual original source terms and their source-site time integrals? Does exact local H+He ionization potential gain plus original photoelectron heat plus escaped photon energy equal original HeIII cascade Lyalpha emitted energy?

For the source HeIII-cascade event rate r_cas, source two-photon branching v(T), source local Lyalpha absorption fraction f in [0.1,1], and source opacity recipient branch z:
dotN_emit = r_cas*(1-v);
dotN_H = r_cas*(1-v)*f*z;
dotN_HeI = r_cas*(1-v)*f*(1-z);
dotN_esc = r_cas*(1-v)*(1-f).
These satisfy the pointwise exact identity dotN_emit = dotN_H+dotN_HeI+dotN_esc.
The source 40.81332-eV line can photoionize H I (chiH=13.598434599702 eV) and He I (chiHe=24.587389011 eV) but not He II (chiHeII=54.41776 eV). With epsilon=1.602176634e-12 erg/eV,
dotB_local=epsilon*(chiH*dotN_H+chiHe*dotN_HeI),
dotQ_local=epsilon*((E-alpha-chiH)*dotN_H+(E-alpha-chiHe)*dotN_HeI),
dotE_esc=epsilon*E-alpha*dotN_esc.
For EACH allowed exact source realization, dotB_local+dotQ_local+dotE_esc=epsilon*E-alpha*dotN_emit.
Here dotQ_local is already the source EventBox.resolved_heat OTS component, and dotE_esc is already EventBox.escaped_energy. The source 26-event population RHS already contains these local H/He absorbed photons; do NOT add them a second time.

## Computational and verification contract

Source interval boxes in actual original MPRK22(1)/Alexander SDIRK2 state steps at t160→161 and t161→162. One original research physical lane; six full/half1/half2 source maps. Temporarily intercept source EventBox calls in-memory to record the EXACT gamma-stage and endpoint source populations, temperature and original emitter/receptor coefficients, WITHOUT changing original REI files. Apply the original two-half-step gamma-weighted quadrature to each source channel. Compare original source EventBox resolved_heat and escaped_energy intervals to the derived H/He local and escaping branches; distinguish algebraic point identities from independent interval upper endpoints. Verify exact source candidate endpoint equality for four arrays, original 14 signed ledgers and table events, original source V2 2e-4 local error and 2e-3 width gates unchanged. Use a single risk-justified same-author independent audit; native subagent unavailable, independent-author blind referee NOT_RUN. No production or official tick161/162.

Metric signature (-,+,+,+), source gas proper seconds, particle counts per original material integration node, energies erg, c retained where eventual transport enters. 46080 material nodes are NOT physical spatial cells and no null ray transport is claimed. Only local on-the-spot source-origin reaction response is evaluated. V2 original three shape lanes are ONE physical realization.

## Claim and drift stop

This original full-OTS cross-species feedback measurement is intended as the RUX03 atomic-process donor interface to central RUX04. No new source atlas after this bounded unit. Central REI canonical 28/88 reported, working 33/88 reported, Physical Fast 4/7 reported, BASS_HE physical 14/18 reported, canonical delta 0. Historical V1 tick161 rejection and V2 nonproduction status remain unchanged. No merges, force pushes, original state/source modification or source tolerances relaxation.

Literature-supported coupled HeIII on-the-spot photon feedback: Friedrich et al., MNRAS 421 (2012) 2232–2250, doi:10.1111/j.1365-2966.2012.20449.x. Photon-conserving RT method: Mellema et al., New Astronomy 11 (2006), doi:10.1016/j.newast.2005.09.004. Original local REI 26-event code is the numerical physics SSOT.
