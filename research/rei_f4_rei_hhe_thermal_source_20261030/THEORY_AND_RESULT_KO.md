# REI F4 | REI H/He thermal point RHS on original BASS193

Source-qualified, source-translated **point calculation**, not a solved REI17+ BASS21 IVP and not actual gas heating.

Input owners: PR #293 HEAD `fd9385f131f93dae2868bbb50b6a542f09dd870b`, original 24,669,729-byte ZIP SHA256 `2149e9651c393dc9c68520ef81b95ff5b22f94408da9131281466fa108711217`. Rust original Grackle `igm_rates.rs` blob `dc3cc028a41ac852d94835372ce13545389d1c3a`, thermal `igm_thermal.rs` blob `0648618d9822e169e9672ac3c556f86595c3b0b6`, axisymmetric geometry `bianchi_i.rs` blob `81dc54583b76e9dcba94c5bbc867243b04ad76b1`.

New actual source data: 193 original saved BASS21 backgrounds, 579 H/He photon/CI/RR events, 193x5 REI HHe F, 193x5x5 J and 193x5x21 common-electron bath-J; thermal/Compton/ionization/escape/proper-clock/b-proxy arrays; six scientific plots. Each source row is calculated from original BASS photon bins and original REI Grackle formula translation, not from fabricated grids.

## Derivation and source mapping

Let Y be 21 original BASS particle-number abundances per original baryon, q ionic charge, n_b baryon number density in m^-3. Native free electrons n_e^B = n_b q·Y. For this HHe-only REI source, n_H = n_b(Y_HI+Y_HII), n_He = n_b(Y_HeI+Y_HeII+Y_HeIII), n_e^HHe=n_b(Y_HII+Y_HeII+2Y_HeIII). nHref/nb=Y_HI+Y_HII. Note the seven saved REI17 comparison states are *not* the same IC or background owners.

Take native BASS `photo_s` and per-ion primary kinetic absorption power as the sole external REI photo gamma and heat; `Gphoto` is a REPLACEMENT source not an additional source. Grackle CI k1,k3,k5, RR k2,k4,k6, DR and cooling as in source Rust. Let N=(n_H+n_He+n_e^HHe). Define u=(3/2) N k_B T, w=u/n_H; the REI point-only microphysics is

Q_micro = Q_photo,kin - Q_coll.ion - Q_rad.kin + Q_CMB,
Q_bind = Q_photo,binding+Q_coll.ion-Q_recomb,binding,
Q_escape=Q_recomb,binding+Q_rad.kin,
Q_input=Q_photo,kin+Q_photo,binding,
Q_micro+Q_bind+Q_escape-Q_input-Q_CMB=0.

Q_CMB=4 sigma_T a_rad k_B/(m_e c) ne T_CMB^4(T_CMB-T). Here `T_CMB=2.7255(1+z) K` is an explicitly added external monopole, NOT an original BASS radiation owner.

w_dot=(Q_micro-2Hu)/n_H, T_dot=(2 n_H w_dot)/(3k_B N)-T (dn_e^chem/dt)/N. The conversion dt=dx/H uses the original BASS saved H. T_dot is **point RHS at original saved T** and may differ dramatically from the archived T'(t); that is not a solution or code bug.

For 5 species X=(H I,H II,He I,He II,He III) in number/baryon, REI source-translated F_5=(Gphoto + ne*M_R) X, ne=n_b q5·X; J5=Gphoto+ne*M_R+n_b(M_R X) q5^T. If one *counterfactually* retains the full BASS 21-species free-electron bath, J_{5x21}=direct 5-column + n_b(M_R X)q21^T. This is not a full 17-species REI F/J owner.

REI `bianchi_i.rs` uses transverse a exp(-b) and longitudinal a exp(2b). On a **conditional** application of that convention to saved BASS b, `K_perp=-H+db/dt`, `K_parallel=-H-2 db/dt` (ADM sign), trace K=-3H and shear^2=3(db/dt)^2. db/dt is calculated from archived epochs; it is NOT original BASS K or dynamically certified Bianchi Einstein evolution.

## Discovered owner mismatch, not silently normalized

BASS native H/He chi in eV is (13.6,24.59,54.42). REI chi is (13.598434599702,24.587389011,54.41776). With identical original gamma and BASS kinetic photoelectron energy, REI photo input differs from BASS absorbed input by sum R_i (chi_REI-chi_BASS). Keep a signed source defect and NEVER quietly identify the two energy owners.

## Source, input, validation and gates

See `SOURCE_LOCK.json` for SHA and commit. `code/build_physics.py` uses byte-locked nested PR293 ZIP, original REI Grackle Python translation from locked PR276, and checks new REI F/J against original PR276 at 193 epochs. Source identity is tested with a deliberate corrupted-ZIP negative test. `tests/` contains fresh same-author self-adversarial regression, not a distinct-author R6/C9. `code/plot_science.py` produces six PNGs with correct signed axes.

`bash VERIFY.sh` repeats computation and all tests and checks exact reproducible output byte SHA/manifest. It never runs a new cosmic IVP, edits source owners, alters initial conditions, merges PRs or resets resource budgets.

**DAG:** Working 33/88, central 28/88, physical-fast 4/7, canonical delta 0; this new source-thermal auxiliary 1/1 scoped, F4 still PARTIAL, L4 not ready, production HOLD. No automatic next node.

**Remaining science:** native full REI17 nuclear/CR/Li7 reactions and isotope-IC mapping, correct shared nHref/nb and Bianchi K background, physically coupled photon transport and secondary electron energy-deposition tables, pure 1S/3P Li K-shell branches and covariance. No CMB tau or observed heating claim.
