# Supplied graph and selected executable network

The supplied PNG has19 reactions and isotope/charge columns. It omits Li IV and Li6, which this pilot's census includes. A census entry is not proof of an active nuclear reaction. All declarations below refer to the new executed atomic model, not to absence of such reactions in nature.

| Graph target | New pilot implementation | Remaining dependency |
|---|---|---|
|1 H I + photon <-> H II + e|Photo + total RR; H1/D elemental equality|CI,DR,CX,multilevel/molecular closure outside selected model; T abundance0|
|2 He I + photon <-> He II + e|Photo + total RR for He3/He4|Isotope-specific/multilevel/CX corrections outside model|
|3 He II + photon <-> He III + e|Photo + total RR for He3/He4|Same declared approximations|
|4 He4 + photon -> He3 + n|Not implemented|Nuclear cross sections and daughter charge/energy coupling|
|5 He4 + photon -> T + p|Not implemented|Same nuclear closure|
|6 He4 + photon -> D + D|Not implemented|Same nuclear closure|
|7 He3 + photon -> D + p|Not implemented|Same nuclear closure|
|8 D + photon -> p + n|Not implemented|Same nuclear closure|
|9 T beta -> He3 + e + antineutrino|Inventory-only zero-T initial condition|Positive-T decay/daughter/energy experiment needs its own operator|
|10 n beta -> p + e + antineutrino|Inventory-only zero-n initial condition|Positive-n decay/daughter/energy experiment needs its own operator|
|11 Li7 + photon -> He4 + T|Not implemented|Nuclear cross sections and daughter charge/energy coupling|
|12 p(n,gamma)D|Not implemented|Nuclear capture rates and energy/photon coupling|
|13 D(p,gamma)He3|Not implemented|Nuclear rates and charge/energy coupling|
|14 D(D,p)T|Not implemented|Same nuclear closure|
|15 D(D,n)He3|Not implemented|Same nuclear closure|
|16 T(D,n)He4|Not implemented|Same nuclear closure|
|17 He3(D,p)He4|Not implemented|Same nuclear closure|
|18 He3(n,p)T|Not implemented|Same nuclear closure|
|19 T(alpha,gamma)Li7|Not implemented|Same nuclear closure|
|Additional Li I/II/III atomic photo channels|All three source rows bound; only Li I photo active on specified5..60eV support|Harder UV requires LiI inner-shell/Auger closure|
|Additional Li II/III/IV total RR|All three downward number-rate channels implemented; upper-charge direction checked at a frozen populated point|No fabricated upper-charge cosmological population; initialq2/q3 remain0|

No nuclear rate has been filled with an arbitrary zero to manufacture a closed full network. These operators are absent from the selected atomic process model. Its exact finite photon support must remain explicit; it is not a general statement about cosmic X-ray/gamma-ray backgrounds. T and n are included with exactly zero initial and generated abundance in this run. The stable isotope histories are conditional on fixed nuclear abundances and elemental electronic equality.

The new pilot is fully executable within its declared process model. The broader19-reaction diagram, full isotope-specific atomic data, negative ions, molecules and a closed energy/radiation evolution remain separate scientific obligations. Current status: NUCLEAR19=UNRESOLVED_NATIVE_COUPLING; PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.
