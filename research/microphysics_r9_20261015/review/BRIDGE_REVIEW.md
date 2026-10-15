# Independent R9 bridge review, 2026-10-15

Decision: **PASS_SCOPED** for the four frozen bounded calculations in the supplied NCP run. No blocking formula, units, inventory or energy-ledger error was found. This review does not close the four original research programmes or establish a physical17-state cosmological history.

## Actual material reviewed

Read all255 lines of bridge_code/bridge_driver.py and all59 lines of bridge_tests/check_bridge.py. Independently ran sha256sum on the desktop driver:8eeadb826f6567d2851bc0bb3db975dff4dcf55420195d31af34897599df080f, matching the NCP execution receipt. Read actual Verner rows, donor Y_final, and the inherited C capture/calibration/Maxwell implementation; the same R8 nuclear and cascade physics sources had been read when freezing this contract. Read NCP BRIDGE_EXECUTION.json, full source_band_moments.json, inventory17.json, np_anchor_sensitivity.json, all32 rows of cascade_mixture_moments.csv, and the CHECKS.json status/header. Read the checker logic rather than relying on its count. No scientific rerun was performed for this review.

NCP receipt: hostname s1a0e5abed09;64 CPUs in affinity; wall1.2294146119966172s; process CPU0.44602447s; peak self RSS31232KiB. The193/193 focused check count is a supplier execution result, corroborated here by source and numeric-output review. These resource fields are self-process measurements, not whole-host utilization or child-inclusive compiler resource accounting.

## Inventory map

The17-state ordering correctly extends the PR15013-state order with Li7q=0..3. A, nuclear Z and ionic q are kept distinct. The selected H/D/T fractions, neutral He3/He4 and singly ionized Li7 match the frozen conditional assignment. The code uses actual Y_final rather than the donor's summary late-time isotope ratios.

Every omitted donor nuclide is preserved in a separate nuclear reservoir. Be7 Y=3.784994236672219e-10 contributes2.6494959656705533e-9 baryons and1.5139976946688876e-9 nuclear charge per donor baryon; none is silently converted to Li. The reported total inventory defect1.6262546864709293e-12 remains uncorrected. Map residuals are -2.220446049250313e-16(A) and -1.1102230246251565e-16(Z); tracked free+bound electron closure is zero at displayed floating-point precision.

The conditional density uses donor nb0 in cm^-3, converts by1e6, then multiplies21^3: nb=2295.9959637053507m^-3. This is a consistent selected density scaling; frozen n/T/Be7 inventories are not physically evolved to z20. Tracked thermal particle count excludes the unassigned reservoir and is labeled accordingly. Donor He4/p=.08194233570928047 and He3/p=1.0418210030213095e-5 are separately reported alongside the incompatible REC/REI helium values.

Nonblocking interpretation note: legacy_hhe_projection='REJECTED...' is a policy diagnostic string, not an invocation or test of the Rust projection. No native registry or coupled-network implementation has been demonstrated by this adapter.

## Cascade spectrum and metastable energy

The new output line counts are mixtures of the actual supplied E1 line yields with normalized(2l+1)/n² weights. Species-specific transition energies retain inherited mass conventions. Terminal probabilities are recomputed through the downward branching graph and compared to stored cascade values; photon counts are compared to the original per-state summaries. The energy check includes the2s reservoir.

For H1,n=3, the output has1.6666666666666667 E1 photons,11.685077906887146eV emitted,0.40228855012300735eV in2s, and initial12.087366457010152eV. P2s=.039445021500022485; P1s=.9605549784999775. Across all32 mixtures the largest energy residual normalized to chi is2.611671420494631e-16. The terminal2s reservoir is not replaced by artificial photon lines. The differential two-photon spectrum, continuum recombination injection, collisional redistribution and radiative transfer remain absent.

The shared branch probabilities across reduced-mass species are appropriate to this inherited hydrogenic model: each species rescales all E1 rates by a common factor. They are not evidence for correlated neutral Li emission.

## Nuclear sensitivity

The inherited C kernel is affine in L and np_fit_L is affine in the thermal cross-section anchor. The new derivative formed from L=0,1 kernels and dL/danchor is therefore the derivative of the adopted model; the independent ±1% difference and affine prediction checks are appropriate.

Anchors330.858,334.2,337.542mb give L=-4.675532848002684,-4.497139347054112,-4.318745846105544fm². The10 temperatures and32/64/128/256 grids match the contract. The maximum64vs256 relative difference1.3322676295501878e-15 passes the1e-10 gate. The finite Maxwell window and E<=1MeV scope are retained. No experimental likelihood, covariance, higher-order EFT truncation uncertainty or modern posterior is inferred from the chosen1% scale.

## Li photon band and response

The implementation transcribes the actual Z=3,N=3 Verner row and converts Mb to m² by1e-22. It uses x=E/E0-y0, y=hypot(x,y1), the frozen Verner shape and support5.392–64.39eV. Heating and absorbed energy use the same threshold/cross-section nodes. The full covered integration never evaluates the missing LiI >64.39eV physics.

The original13.6–100eV photon integral63.25615498773386eV³ stays the denominator. The added5.392–13.6 band has photon ratio1.3994062153740474 and mean energy9.248434443264294eV; this ratio need not be<=1 because it compares disjoint source bands. MD14 births and the independently prescribed reference incident flux are explicitly distinct. The fesc=.2 continuation is a conditional source choice. No spurious year factor is applied.

For Fref=1photon m^-2 s^-1 integrated over the original band, Gamma_sub=1.954782148200409e-22s^-1 and Gamma_covered=2.545313072863097e-22s^-1; their ratio=.7679928135526256. Heating_sub=1.095807636259005e-40 and heating_covered=2.3056235802227934e-40J/s/LiI, ratio=.4752760362353323. These are normalized spectral responses, not cosmic rates. Absorption energy identity relative residuals are1.464632483788312e-16 and-9.053862253054057e-17.

## Numerical repair and disposition

The root-authorized source2048/photo4096 Simpson choices preserve the physical model and1e-10 tolerance. The earlier covered photo1024vs2048 discrepancies(-6.29064911272792e-10 Gamma,+8.114382499257999e-10 heat) remain in the output. The accepted2048vs4096 values are-3.929112590839168e-11 and+5.0710324828173725e-11. The4096vs16384 values are-2.608802063264193e-12 and+3.3673064336880998e-12. Source1024vs2048 maximum8.472167412065801e-11 passes. Contract restoration consolidates this authorized algorithm-only refinement; no tolerance was relaxed.

The outputs are admitted for conservative inventory mapping, declared E1 mixture spectra, old-model nuclear sensitivity and conditional Li photon-band response. They are cheap bounded bridge calculations executed on the NCP host, not four completed heavy physical programmes. Contracts were semantically restored from the author's history because the original scratch files became inaccessible; this restoration does not assert byte-identical recovery. Remaining programme dependencies are recorded in CONTRACT_BRIDGE.md and each output's scope.
