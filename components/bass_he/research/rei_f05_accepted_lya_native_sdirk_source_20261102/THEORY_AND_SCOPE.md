# BASS_HE to original REI IGM: accepted 0-to-160 HeII Ly-alpha source-time quadrature

2026-11-02 KST | new original-source photon-number physics unit | DRAFT/HOLD

## Sources, frozen identity, new target
Immutable BASS_HE parent PR150 HEAD f2d26ef196b50e69c1793cc4c29e96a248fe6c0b, native REI PR355 HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00. Original kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644; original F05 source TAR a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b. REC195 verified original accepted states [0,64,128,160] in a local source-inclusive ZIP SHA256 ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657; private states tick64 SHA256 aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425, tick128 bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6, tick160 74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6. Use REC195 original-matching NumPy2.3.5/pandas2.2.3/SciPy1.17.0 isolated venv; no globally modified environment.

Scientific objective: evaluate the *time-integrated source-original* explicitly identified HeIII-cascade HeII Lyman-alpha photon escape channel on the genuine accepted [0,64],[64,128],[128,160] intervals, reusing exact original MPRK22 and Alexander-SDIRK2 stage/final event boxes. This creates time-resolved, physically sourced photon numbers for a future REI causal radiation source, not another PW19 static opacity atlas or H/He source-only table.

## Mathematical form, bounds, exact restrictions
Metric (-,+,+,+), proper time s, energy erg, photons as dimensionless number. Native HeII ionization threshold chi_HeII=54.417760 eV, source HeII Ly-alpha Ealpha=3 chi_HeII/4=40.81332 eV, EV=1.602176634e-12 erg/eV. This photon exceeds H I and He I photoionization thresholds, not He II. It is an original *line source*, not the original four group photon current.

At each native event-box source site:
r3cas=N_HeIII*n_e*max(alphaB_HeIII-min(alpha_n2_HeIII,alphaB_HeIII),0),
Qesc=r3cas*(1-v)*(1-f)*Ealpha*EV, and Jesc=Qesc/(Ealpha*EV).
Original code uses Hummer-Seaton v(T) with strict non-extrapolation and f as the interval [0.1,1.0]. Therefore f=1 allows zero escaped line photons and the original source *does not guarantee* positive escaping flux. Previously fixed f=0.1 is a source-conditional branch, not universal admission. Keep the source interval without artificially setting f to 0.1, and never interpret unresolved energy remainder as a monochromatic photon source.

For the original SDIRK gamma=1-1/sqrt(2) and proper time step h:
Iesc[a,b]=h*((1-gamma)*Qesc_at_gamma+gamma*Qesc_at_final).
The original accepted state is represented by two half steps; integrate the source as Iesc_half1+Iesc_half2 on each of the three accepted intervals and compare against original full-step quadrature. Source average is an actual discrete event-site integral tied to the accepted native map, not a continuum certified physical radiation transport theorem. Nesc[a,b]=Iesc[a,b]/(Ealpha*EV), hence each nonzero emitted line photon carries a source-defined 40.81332 eV.

Source stochastic interpretation STOP: this yields only OTS local escape from its closure, NOT physical transport through neighboring cells, observer flux, a Bianchi directional distribution, or cosmological line-of-sight tau. No source positions/directions or source-matched emitted Jnu(t,x,n) beyond one line are invented. Subsequent angular-spectral causal transport must be owned by original REI RUX03/04 and must track H I/He I absorber competition and observer frame.

## Actual-code validation and acceptance ceilings
Use exact original REC195 three private accepted source states + original initial state; verify three SHA identities, source mapping and time. Re-execute original full/half1/half2 maps per accepted [0,64],[64,128],[128,160] on original 46080 source cells. Before admitting a physical result verify source original 14 conserved ledgers include zero, zero table events, accepted state byte-level equality of decoded arrays, original 2e-4 local error and 2e-3 width gates unchanged. Do not promote a current runtime as historically authoritative if full bytes and runtime contract cannot be certified.

Report 3 original interval-integrated source photon-energy and photon-number enclosures, per-cell source results, full-versus-twohalf numerical discrepancy as a diagnostic only, no universal time integration bound. Source f interval means Nesc.lower can be zero. Distinct-author blind referee absent; same-author independent photon number/energy audit with original source constants and negative source identity tests.

REI canonical DAG 28/88, working 33/88, physical fast 4/7, BASS_HE physical 14/18, canonical delta 0 unless separate original-owner approval. Production HOLD, no merge/force/tolerance modification/no official tick161. Stop after one source-duration emission input; no repeated static opacity or governance PRs.

Literature: Mellema et al., C2-Ray, New Astron. 11 (2006) 374-395, DOI 10.1016/j.newast.2005.09.004; Friedrich et al. MNRAS 421 (2012) 2232-2250, DOI 10.1111/j.1365-2966.2012.20449.x. Original source code controls local physical claim.
