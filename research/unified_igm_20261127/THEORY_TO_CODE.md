# Single-owner H/He/D, line photons and cosmic rays in REI

The host is the November 27 R118-C3T REI descendant `a3cd7cdc3e7cf7c9059c3c420338bdd1d60d0b15`. BASS R118 `a1c67b91e583ea0a081132cf1584b1d11b456469` and REC R118 `b15fec69391d7f83c7461135dc7a8434d7837800` supply the existing geometry/radiation and recombination paths. PR377's AX11 T1 and checkpoint-scoped T2 evidence descend through this host. The original conditional primary-only scenario supplies the off-state baseline. Channel-enabled cases have explicit inputs and a separate identity.

| Stage | Construction or decision |
|---|---|
| R1 | Put source and tests for WU, HE and CR under the REI owner. Use the existing BASS–REC–REI material evolution as the host. Fixed units and a one-owner collision update are the new mathematical interface. |
| R2 | Read donor R59, HE155, CR167 and CR proper injection, the R118 host and the separate AXBI convergence lineage. Bind atomic coefficients to Savin's printed D/H data, HE to its actual cascade branch and CR to the recipient and spectrum used to generate rates. |
| R3 | Use a homogeneous proper fluid cell with signature (−,+,+,+). Collision substeps are at fixed cell volume and proper time. x_HII is per hydrogen nucleus, y_DII per D nucleus, η=n_D/n_H. A CR birth spectrum carries energy and particle number and requires transport/deposition to give a heating rate. |
| R4 | Compare an energy-only source with energy-resolved reactions. Two spectra with identical N and U generate a cross-section-weighted rate ratio 4/27. Adopt per-channel integrals or the resolved spectrum. |
| R5 | Derive stoichiometric left invariants, binding/thermal/escape ledger, massive collisionless redshift, charge-exchange contraction and the temperature change for a varying particle inventory. See derivation below and CONSERVATIVE_TRANSFER.md. |
| R6 | Independent derivation and exact rational substitution verify left invariants and expose 6.4 eV per duplicate 20 eV H ionization. Compare donor source ownership, rate signs and endpoints. |
| R7 | Exact rational spectra at 10,20,30 eV give 4/27. The closed D/H bound for η=2.5e−5 is 0.000715612 K; the He line sends at most 40.81332 eV per emitted photon into the combined sinks. Source-specific tests return finite residuals under their stated assumptions. |
| R8 | Adopt the transfer identities conditionally on source, species, frame, normalization and proper-time agreement. The two-spectrum witness rejects an N,U-only join for the selected kernel. The global closure and free input spectrum are independent obligations. No new global exclusion theorem is inferred. |
| R9 | Implement exact source-specific coefficient readers, bounded state updates, native BASS/REC integration path and a central callable entry. Test off, active, duplicate ownership, energy partitions, domains and known source arrays. |
| R10 | Hand off these formulae and test cases to coding. Preserve existing R118 pair transport, F05 and AXBI scientific claims at their original scopes. Phase two executes cross-component cases in the REI checkout. |

## Charge exchange

For D I + H II → D II + H I define J=k_f n_DI n_HII−k_r n_DII n_HI in cm⁻³ s⁻¹. The (HI,HII,DI,DII,e) increments per net event are (1,−1,−1,1,0). Gas heat is −J ΔI with ΔI≈0.0037 eV. For homogeneous constant n_H,T and closed CX, x=S−ηy, S=x₀+ηy₀, and ẏ=n_H F(y), F=k_f x(1−y)−k_r(1−x)y. The admissible y interval is [max(0,(S−1)/η),min(1,S/η)] for η>0. Its endpoint flows point inward and F′=−k_f x−k_r(1−x)−η[k_f(1−y)+k_r y]≤−(1+η)min(k_f,k_r). Thus the equilibrium is unique and the difference of solutions at fixed S contracts exponentially. At fixed volume and particle count, ΔT=−2η n_H ΔI Δy/(3 k_B n_tot), with ΔI and k_B in matching units. An open, photo-driven network must integrate J through its actual history. η=0 gives an exact inactive term.

## Helium line and electron birth

For one realization let Rα=(1−v)R_cas, f the locally reabsorbed fraction, w=κ_H/(κ_H+κ_He), r_H=fwRα, r_He=f(1−w)Rα and r_esc=(1−f)Rα. When absorption vanishes only escape contributes. With Eα=40.81332 eV, EαRα=χ_H r_H+χ_He r_He+(Eα−χ_H)r_H+(Eα−χ_He)r_He+Eαr_esc. All five terms use the same branching realization. Use 1.602176634×10⁻¹² erg/eV for energy rates in cgs. Taxing the primary photon for binding and assigning its excess again through a second local processor violates this identity. The photoelectron excess belongs to either local thermalization or a tracked nonthermal reservoir until deposition.

For an injected particle distribution dn/dE, the proper ionization rate for target j is n_j∫v(E)σ_j(E)(dn/dE)dE. Distinguish injection, particle creation, subsequent deposition, and adiabatic work. For the qualified CR donor Q_e(W,t)=tA(W), one step has births A(W)(t₁−t₀)(t₁+t₀)/2. Integrate physical excess over W in matching eV/J units. At fixed volume the ideal translational energy is (3/2)N_part k_B T; recover T' from both U' and N'_part. For a directional physical pressure P_ii, total expansion work is ∫V Σ_i H_iP_ii dτ. This uses principal-frame physical pressures and leaves rest energy convention explicit.
