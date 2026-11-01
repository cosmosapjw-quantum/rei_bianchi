# REI-F05 first canonical interval: correlated H/He material-energy parent path

Date 2026-11-01. Immutable parent is REI PR #328 HEAD a85312cde63e5c0b0a7c0e5d182e79fe593bcf53. Original frozen failed state archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b. Original source accepted array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01. Original predecessor 26-event MPRK22/SDIRK2 source SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644.

Original [160,161] 46,080-node all-parent cross-box logT failure 2.1245050576368385e-4 exceeds strict unchanged 2e-4; state-width threshold unchanged 2e-3. Source accepted 160/131072 ticks, 3 endpoints. Previous PR #328 executed original nonlinear full/twohalf at one nuclei-conserving parent point, giving max logT output box difference 5.948382018061694e-7. It did NOT admit the full parent set.

## Physics of the bounded new experiment

Species population N=(HI,HII,HeI,HeII,HeIII) in one original spatial node, fixed nuclei N_H=HI+HII and N_He=HeI+HeII+HeIII, free electrons Ne=HII+HeII+2HeIII. For input comparison, define idealized thermal-plus-atomic-ionization material energy:
E_mat=(3/2)k_B T(N_H+N_He+Ne)+eps_eV[chi_H HII+chi_HeI HeII+(chi_HeI+chi_HeII)HeIII].
Here k_B=1.380649e-16 erg/K and eps_eV=1.602176634e-12 erg/eV; chi in eV = (13.598434599702,24.587389011,54.4177655282). These are NIST reference thresholds; no claim of exact equality to every owner photon-event threshold.

Let N0 be a nuclei-conserving center of the ORIGINAL accepted parent coordinate box and T0 its geometric center. Pick an ionization-raising direction dN with neutral reservoirs compensated exactly (dHI=-dHII; dHeI=-dHeII-dHeIII). Fix a single scale s_i for each original spatial node from BOTH signed temperature and population box constraints. For alpha in [-1,1] define N(alpha)=N0+alpha*s_i*dN and
T(alpha)=[E_mat(N0,T0)-E_ion(N(alpha))]/[(3/2)k_B(N_H+N_He+Ne(alpha))].
Then the chosen input path preserves H/He nuclei and material E exactly under that *defined idealized ledger*. This is NOT an assumption that material energy is conserved during astrophysical time evolution. Moreover membership in coordinate box does not certify membership in the original jointly reachable parent/source set.

At alpha=+1 and -1 separately evaluate ORIGINAL time-correct full and two-half nonlinear 26-event MPRK22(1)/Alexander SDIRK2 maps with four original photon-source evaluation sites, no owner/threshold/clock changes. Output a source-owned 46,080-node physical response for each signed point and each shape lane. This supplies a controlled correlated material-input source sensitivity. The reported output image difference STILL uses independent interval subtraction and CANNOT close the full-X correlated D_h(X,theta) certificate.

The required general object is D_h(Y,theta)=F_h(Y,theta)-G_1(G_0(Y,theta),theta), with the same Y and original source theta on both sides. Certified acceptance requires a joint source+parent Jacobian/remainder for all original uncertainty, not a handful of point-family samples.

## Existing computed source-based preparatory result (local, before nonlinear CI)
Original PR320 46,080 accepted H/He node-source archive GitHub artifact #13064333012 SHA256 48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7 was byte checked. A distinct local source-based 46,080-node material curve was generated; maximal material-energy relative residual 2.3822360821317044e-16, median signed electron-per-H difference 2.253277908703666e-8, median signed temperature difference -0.001528521160253149 K, 46,080 of 46,080 nodes with cooler ion-richer parent. Local source-derived results exist in the full user-facing package, and are not falsely claimed to be original nonlinear map outputs.

## Science review and claim scope
This is ONE physical micro-interval source experiment. Distinct-author referee NOT_RUN; same-author bounded hostile review is required. No original source or parent mutation, no new REI IVP, no production, no merge, no force push, no tolerance relaxation, no budget reset. Any CI result must be read back before claiming source-map execution.
CLOSED: physically valid two input parent states; local source data generation; analytic material-energy identity.
OPEN: original all-X joint interval-map certificate and full F05 interval; source photon/energy/ONS force identity for each new map (existing run_step enforces its own).
Owner-reported REI canonical 28/88 (+0), REI working 33/88 (+0), REC physical H5 0/313 (+0).
After this unit use the actual original source derivative/remainder and full parent uncertainty, then reconsider original single failing step only when the old gate is met.
Primary methods support, not code validation: Makino & Berz (2009), DOI 10.1145/1577190.1577206, and guaranteed implicit RK interval methods, https://hal.science/hal-01111240/document.
