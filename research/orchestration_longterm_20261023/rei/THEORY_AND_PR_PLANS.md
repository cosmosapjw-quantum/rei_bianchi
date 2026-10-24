# Closed-subsystem route and concrete PR leaves

Six leaves below replace the old coarse N8 dependency. They distinguish closure of a selected finite source model from empirical completeness and from a self-consistent cosmological solution. ANGTHERM02 remains a separately owned numerical leaf. No new universal no-go or empirical accuracy theorem is proposed.

## Constructive source and stress assembly

Use (-,+,+,+), proper seconds, conserved reference density n_ref with dot(n_ref)=-3H n_ref, energies per Href and explicit conversion eV→J when forming SI stress. Define gas thermal u, binding i, resolved UV r, dynamic escaped radiation e, external source reservoir s. For per-Href pressure tensor p_A, homogeneous balance is

    dot(u_A) + 3H p_A + sigma:pi_A = q_A,

where p_A means the scalar mean pressure; all quantities in this line are per Href. This follows from rho_A=n_ref u_A in dot(rho_A)+3H(rho_A+p_A^physical)+sigma:pi_A^physical=Q_A. Gas has p_g=2u/3 and pi_g=0 under the current isotropic closure. Binding energy has p_i=0 in this nonrelativistic internal-energy model. Radiation has p_r=r/3. Nonbaryonic massive matter retains its independently supplied pressure/stress, and its rest-mass accounting must not be folded into atomic binding twice.

For one photoionization event of energy E and threshold chi, and one RR event with captured kinetic moment K, the energy exchange columns in order (u,i,r,e,s) are

    PI: (E-chi, +chi, -E, 0, 0)
    RR: (-K, -chi, 0, chi+K, 0).

Each column sums to zero. This only establishes energy exchange for the chosen scalar events. A source spectrum or angular injection must provide its own positive number/energy/STF moments and momentum/recoil ownership before a general four-force claim. Reflection-symmetric LRS packet pairs have zero total injected momentum and supply a finite model in which the scalar reduction applies. A source feed of strength J transfers (0,0,+J,0,-J); a prescribed infinite source instead leaves +J as an explicit external term in the tracked balance. Setting the latter to zero would be a false closure.

For LRS photon scalar Q, pi=diag(-Q/3,-Q/3,2Q/3); sigma=diag(-s_h,-s_h,2s_h), so sigma:pi=2s_h Q and ||pi||_F=sqrt(2/3)|Q|. Physical tensors multiply per-Href tensors by n_ref and the energy conversion. Sum signed component tensors first, then take the norm. Radiation realizability requires P=diag((r-Q)/3,(r-Q)/3,(r+2Q)/3) positive semidefinite, hence -r/2≤Q≤r, and r≥0. These necessary constraints connect directly to selected X1. General tensor PSD is necessary but not a source-specific kinetic closure.

Let source exchange sum vanish and W'=2u+r+e+sigma:(pi_r+pi_e)/H in eta=ln a (gas isotropic; other components need their own work). Then (u+i+r+e+W)'=0. This follows by adding the component balances, not by defining W from subtraction. A cumulative bolometric emission tally L'=RR(chi+K) omits redshift and shear work and is not the dynamic e state. Existing ANGTHERM01's identity u+i+r+L+W_g+W_r=constant remains correct as an open-subsystem accounting identity; L may not be inserted as a gravitating radiation density. A dynamic e requires a number/energy/angular source and transport, and the old tally must remain diagnostic rather than a second energy owner.

## L0 — source-exchange and signed stress adapter

Purpose: implement the finite algebra above and distinguish passive emitted-energy accounting from a dynamic radiation reservoir. Inputs: ANGTHERM01 THEORY blob7e110c8328ace7d7b4a511bbe3c14d8cb00a40c6 at delivery6daf382..., X1 moment-cone gate after review, existing C3 event bookkeeping. Add only `research/rei_closed_exchange_20261023/`; do not edit ANGTHERM02, C13/C15/C16 donors or production defaults. PR is a future additive leaf, documentation may be published centrally now.

Code contract: source columns in proper time, explicit eV/Href normalization, scalar mean-pressure work, tensor sum before norm, optional dynamic escape state distinct from historical ledger. No physical rate fitting, quadrature, solver or IVP. Acceptance: exact rational column energy cancellations; PI charge/count and RR reverse bookkeeping; analytic Jacobian column cancellations; LRS tensor trace/STF/contraction checks; opposite-sign stress cancellation; zero-shear limit; detect double-counted escaped ledger and omitted external source term. Decimal/Fraction exact references plus binary64 scaled residual≤2e-12, same as inherited ANGTHERM01 local cancellation ceiling. PSD rejects are physical-domain rejection only; tolerate only explicitly bounded floating error without clipping. Initial probe≤30s per old N6 small-kernel policy; cumulative cap and previous debit must be frozen by the controller before future execution. PASS→bind one donor source in L1; failure→one targeted repair, no broad audit.

## L1 — source-qualified radiation and thermal pair

Purpose: populate L0 with one actual selected physical provider and its coupled gas/radiation event, preserving one owner. BASS_CR C23B currently supplies finite H/He PW19 ground-state spectra at three verified redshifts; complete stopping/instant heat is not supplied. WU088_HH provides isotope threshold and number/energy moments; REC supplies native line or Compton components under distinct bath conventions. These donor authorities own physics. REI adapter must preserve domain, external-supply normalization, support zeros versus missing input and number/energy/STF identity. Do not combine Planck-bath and actual-monopole formulas into one provider silently.

PR files: provider binding record, source-domain evaluator adapter, exchange/Jacobian unit checks and a finite source-moment table. Gate: exact selected source input; integration support complete for claimed finite spectrum; matching number and captured-energy moment; nonthermal energy routed to an explicit reservoir until stopping is supplied; charge and baryon invariants; one line/beta/PI owner; donor-specific accuracy retained. Scope first admits the finite supplied table/conditional closure. Source uncertainty remains separate from implementation residual. Initial scalar/local check≤30s after exact donor debit and budget binding; no cohort. PASS→one closed selected fixed-geometry model in L4; unresolved physical input→retain explicit external/conditional reservoir and narrow model, not a manufactured zero.

## L2 — nonzero neutron/tritium beta and daughter channels

Purpose: extend zero n/T face only with actual daughter charge distribution and electron/neutrino/recoil partition. Reuse localflow scientific9620e1fcc4bdda76e0311206f614234926600381 (103 checks, separate96 guards) and C3 positivity bookkeeping. Total Q is not gas heat. A beta event removes parent and creates one physically supported daughter branch; charged-particle stopping determines heat and secondary channels; neutrino/fast/recoil ledgers receive complementary energy.

PR files: primary source dossier, normalized branch/moment data, local operator/Jacobian and finite event references. Gate: branches nonnegative and sum1; baryon/charge including emitted electron and recoil correct; per-event energy sums Q with one mass-defect convention; source domain and uncertainty stated; reconstructed electron density updated once; mixed atomic/nuclear event ownership unique. Heavy or full-history runs remain unready until source and finite operator pass. Budget not transferable from ANGTHERM01 or D10; initial local≤30s only after controller records a cumulative cap. PASS→select nonzero n/T extension of L4; failure from missing source is INPUT_DEPENDENCY, not a mathematical no-go.

## L3 — baryonic material stress and realizability

Purpose: supply actual baryonic pi_b if departing from current isotropic gas, while keeping BASS's collisionless nonbaryonic massive pi_m separate. BASS_HE owns finite-mass collision pressure exchange and source-qualified transport inputs; REI owns component assembly. X1 checks the necessary pressure cone of the selected reconstructed tensor, not empirical closure or global realizability. D10's35 saved histories remain evidence about its original massive component, not evidence that reacting gas generates the same pi.

PR files: baryon pressure/energy transfer adapter, exact component map, source-normalization table and one local matrix validation. Gate: sum of pair momentum/energy exchange zero; equilibrium symmetry and appropriate nonnegative relaxation in supported model; total pressure PSD; reactive gain positivity under X1; signed shear contraction and full Frobenius convention consistent; no event-frequency→l=2 transport substitution. Source-dependent transport data and moment-closure validity are independent gates. Small matrix/scalar budget only, inherited HE owner ledger; no saved-history rerun. PASS→optional anisotropic baryon variant of L4. pi_b=0 remains an explicit smaller model choice and does not require solving L3 before every isotropic pilot.

## L4 — finite closed selected gas+radiation+geometry pilot

Purpose: connect L0/L1 plus BASS geometry to a self-consistent chosen finite model. Isotropic-gas, zero n/T pilot depends on L0/L1 and numerical integration hooks; nonzero beta depends additionally on L2 and anisotropic baryons on L3. ANGTHERM02 continuum evidence is needed only if its angular target/representation is claimed. This conditional dependency avoids blocking a minimal valid model behind all possible physics.

PR files: frozen model/IC and provider map, full RHS/Jacobian, independently accumulated work/exchange ledgers, one matched full/reference versus reduced trajectory contract, raw outputs/checkpoints. Gate1 physical: each included source qualified and complementary reservoirs explicit. Gate2 dynamics: the new trace state actually updates Einstein H/shear and stress, not just donor interpolation. Gate3 numerical: paired full-state error with preserved tolerances/scales, energy/baryon/charge residuals, positivity/domain and a genuinely discriminating refinement. Exact tolerance and cumulative CPU/wall cap must be frozen after stiffness/profile and finite model selection; not inferred from old unused budgets. No NCP readiness until source/build/input/command/stop/checkpoint return contract exists. PASS→scoped selected-model solution; no empirical reionization prediction by conservation alone.

## L5 — broader physical and observable admission

Purpose: extend finite selected L4 to the explicitly requested physical family and observable. Requires source/emissivity histories, isotope/secondary/line/thermal channels only as necessary for that claim, Bianchi geometry family, initial/boundary conditions and observable transfer. Define physical/model uncertainty, discretization error and finite experimental differences separately. No universal speedup from unmatched solver norms, no all-Bianchi result from LRS, no angular-continuum certificate from M4/M8/M16 differences alone.

PR files: one claim-specific physical completeness map, observable definition, finite error budget and owner-approved campaign. Gates and budget are NOT_FROZEN until target/input defined. PASS→one named observable/parameter-domain admission; HOLD→exact missing physical or numerical dependency. No arbitrary percent-complete or automatic escalation to external computation.
