# Initial conditions for the selected 17 states

2026-10-28; R2/R3/R5 analytical proposal, no solver, plot or test execution. Preserve completed PR248 HEAD `022f2ed85595364f05834d8eb1573434efce92d0`. The default for reproducing that result remains its exact 300 K donor initial state. A separate cold diffuse-IGM profile below is a defensible starting hypothesis for future work, requiring a matching bath. Neither is a precision recombination prediction.

## What the current files actually initialize

Read `rei_source_history_20261028/implementation/coupled.py`, `history.py`, the raw external-source config, donor `angular_model.py`, `atomic_network.py`, baseline CSV row zero and NPZ scalar entries. Coupled copies the 17 visible initial populations, sets fast numbers, fast energies and accumulated boundary ledgers to zero, and prescribes the four hidden Li6 entries. Time zero is source-onset elapsed time at z=20; it is not zero cosmic age. The saved NPZ explicitly has temperature 300 K, electron/Href=0.00020000550001 and nHref=0.0017668803778189406 cm^-3. The vendor's older prescribed 8 K formula is not the saved angular-thermochemistry initial temperature.

## Concrete proposed table

All entries are particles/Href. In these initial profiles, H1/Href=1 by definition; this does not imply one baryon/Href. The JSON is the machine-readable proposal, not an executed configuration.

| State | Legacy reproduction, 300 K | Cold IGM source onset, 8 K | Meaning |
|---|---:|---:|---|
| n | 0 | 0 | negligible relic/source-onset approximation |
| H I | 0.9998 | 0.9998 | adopted residual-ionization split |
| H II | 0.0002 | 0.0002 | adopted x_HII=2e-4 |
| D I | 2.4995e-5 | 2.5264946e-5 | isotope total minus D II |
| D II | 5e-9 | 5.054e-9 | same residual ionic fraction as H |
| T I | 0 | 0 | negligible relic/source-onset approximation |
| T II | 0 | 0 | same |
| 3He I | 1e-5 | 1e-5 | adopted primordial-like isotope total |
| 3He II | 0 | 0 | neutral-He limiting approximation |
| 3He III | 0 | 0 | same |
| 4He I | 0.082 | 0.082 | adopted primordial-like isotope total |
| 4He II | 0 | 0 | neutral-He limiting approximation |
| 4He III | 0 | 0 | same |
| 7Li I | 0 | 5e-12 | cold profile adopts 1% neutral Li, illustrative |
| 7Li II | 5e-10 | 4.95e-10 | predominantly singly ionized Li |
| 7Li III | 0 | 0 | no initial hard-ionization component assumed |
| 7Li IV | 0 | 0 | same |

Both retain hidden Li6=(0,1e-14,0,0) initially and its saved prescribed history. Its abundance is inherited, not newly BBN calibrated. Both use B_n=B_T=U_n=U_T=0 at source onset; initial boundary ledgers are zero. All states are nonnegative. No arbitrary tiny-positive seed is needed. A zero approximation here never asserts exact physical absence or impossibility of production.

## Evidence strength and useful brackets

**Isotope totals.** Cooke, Pettini & Steidel (2018), section 5.1 equations 9–10, obtain primordial D/H=(2.527±0.030)e-5 from seven metal-poor absorbers. The cold profile uses that historical measured central value; it is not advertised as the latest combined constraint. Pitrou et al. (2018) obtain theoretical Yp=0.24709±0.00017 under their BBN assumptions. The rounded adopted 4He/H=0.082 is compatible in scale after converting mass fraction to number ratio; it is not the same directly measured quantity. 3He/H=1e-5 and 7Li/H=5e-10 remain rounded BBN-motivated choices inherited from the model. No precision 3He measurement was newly imported. Stellar lithium abundances differ from standard-BBN predictions; the range Li7/H=1e-10 to 6e-10 is a sensitivity comparison, not a combined confidence interval. BBN yields apply to isotope totals before later astration, stellar ejecta and cosmic-ray production. The 17-state pilot does not calculate that earlier enrichment history.

**Ionic fractions.** Switzer & Hirata (2005), sections III–IV and Figure 3, explain that the nonthermal hydrogen-recombination radiation keeps lithium largely singly ionized through the late recombination era. Residual hydrogen ionization is of order a few 1e-4; x_HII=2e-4 is an illustrative representative, with [1e-4,3e-4] a nuisance bracket. The 1% Li I choice and [0,0.1] neutral-fraction bracket are not digitized predictions from their figure. Helium-neutral initial conditions and zero He III/Li III/Li IV are a cold, weakly irradiated limiting model. Optional nuisance ion-fraction ranges He II=[0,1e-6], He III=[0,1e-10] are exploratory tolerances, not observational bounds. A previously ionized or locally irradiated patch needs a different profile.

**Thermal and chemical history.** Tgas=8 K, bracket [5,30] K, is an illustrative cold IGM alternative; the actual saved 300 K bath is warmer and remains a separate model. These temperatures cannot be exchanged without changing initial thermal energy and temperature-dependent hazards. A matched recombination calculation for the actual cosmological/Bianchi history would be needed to upgrade the ionic and thermal choices beyond these controlled priors.

## D/H charge exchange: comparison, not an automatic correction

For D+H+ -> D++H and the reverse, detailed balance gives k_ion/k_rec approximately exp(-42.915 K/T). If these exchanges equilibrate faster than expansion and other processes, their balance implies

    x_DII/(1-x_DII) = [x_HII/(1-x_HII)] exp(-42.915 K/T).

At 8 K and x_HII=2e-4 this gives x_DII=9.362632896366007e-7 and DII/Href=2.36593733291169e-11 for the proposed D total. These are static evaluations of a conditional formula, not evolved chemical results. Low-temperature ionizing exchange is suppressed, so equilibrium cannot be assumed from the formula alone. The current retained electronic operator gives H and D equal electronic rates and does not include these exchange reactions. The recommended initialization therefore retains isotope-blind residual x_DII=x_HII. Compare it with the conditional lower-ionization branch only after supplying exchange kinetics and a timescale assessment. Cooke & Pettini (2016), equations 19–20, discuss the relative rates and a fitting pitfall; Savin (2002) is the underlying primary rate calculation.

Lithium is also not assigned a Saha or charge-exchange equilibrium solely from its ionization potential. Switzer & Hirata equation 15 includes radiative Li+H+ charge transfer; their analysis finds this less important than the photoionization/recombination control considered there. Stancil & Zygelman (1996) supply a quantum radiative-transfer collision calculation, including k(300 K)=1.3e-13 cm^3/s. A favorable reaction energy does not establish fast exchange at diffuse IGM densities. The selected model currently lacks this chemical channel.

## n/T relics, pre-existing sources and fast energy

Free primordial neutrons and tritium cannot be treated as surviving stable BBN abundances at z=20. With the preserved neutron lifetime 878.4 s and tritium half-life 12.312 years, a relic component satisfies y_n(t0)<=y_n(t_prod)exp[-lambda_n Delta t] and y_T(t0)<=y_T(t_prod)exp[-lambda_T Delta t], absent replenishment; extra losses only reduce these bounds. This gives a principled negligible-relic approximation once a production epoch and numerical resolution are stated. No absolute cosmic age or arbitrary finite relic seed is invented here.

A source already active before t0 can instead produce a nonzero stock:

    B_j(t0)=B_j(t_a) exp[-integral_ta^t0 L_j du]
          +integral_ta^t0 S_j(s) exp[-integral_s^t0 L_j du] ds.

Use the same expression with incoming kinetic power P_j for U_j. Constant prior forcing that lasted many relaxation times gives B_j=S_j/L_j and U_j=P_j/L_j; this is a conditional relaxed-history profile, not the source-onset profile. The thermal n/T stocks then follow their causal five-state driven solution. Direct injected particles alone carry the configured 1 MeV per fast particle, but produced nuclear daughters also contribute to S and P. Consequently U/B need not be 1 MeV for a mixed relaxed reservoir. Require U>=0, B>=0 and B=0 implies U=0; retained gamma=1 is the existing nonrelativistic decay approximation. Do not initialize finite U with zero B or count fast stocks twice as thermal stocks.

## Normalization, charge and adapter requirements

Let y_i=n_i/nHref with the existing expanding reference. Total baryons per reference are B_ref=sum_visible A_i y_i+B_n+3B_T+6 sum_hidden y_Li6. Per-baryon fractions are Y_i=y_i/B_ref, not y_i divided by the visible number sum. Conversely a homogeneous primordial helium mass fraction Yp determines f_He4=Yp C/[4(1-Yp)], where C contains all baryonic contributions other than 4He per Href. This makes the trace-abundance convention explicit. External injection means B_ref can evolve; never force sum A_i y_i=1 while retaining per-Href stock units.

The initially neutral electron-charge ledger is

    y_e,charge = sum_visible q_i y_i + B_T + sum_(q=0..3) q y_Li6,q.

It is 0.00020000550001 for the legacy profile and 0.00020000554901 for the cold residual profile. These are number/charge balances, not electron-temperature statements. In `coupled.py` the recombination hazards use the saved prescribed electron bath, while the evolved electron quantity is only a charge ledger. Replacing the ionic initial vector does not automatically replace that bath. Cold-profile activation requires a new explicitly matched temperature/electron/photon closure, including its initial thermal energy 3 k_B T (n_ions+n_e)/2 per proper volume for the nonrelativistic monatomic translational part. Internal ionization and fast kinetic energies are separate owners. Molecular/negative-ion reservoirs are omitted from the selected network and cannot be absorbed into a precision electron-history claim.

The future adapter must select the profile explicitly, recompute charge and initial energy, bind hidden Li6, preserve elapsed-time origin, and reconstruct hazards from the selected bath. If using a prescribed bath rather than evolving it, label that approximation and its external exchange. A recombination-distortion Li-ionizing field needs its own input or explicit omission; the old finite photon packet is not automatically that spectrum. No existing bath or baseline file is changed by these proposals.

## Other necessary initial fields

| Field | Initial prescription | Scope |
|---|---|---|
| Free electron number | charge-neutrality expression above | derived from charged populations, not an independent scalar choice |
| Gas temperature | 300 K legacy; 8 K proposed cold profile | reconstruct thermal energy and rates consistently |
| CMB photons | T_gamma=2.7255(1+z) K, hence 57.2355 K at z=20 | standard blackbody temperature-law assumption; independent of the saved finite UV packet |
| New UV/energetic photons | explicit source history and initial spectrum | cannot be inferred from CMB temperature or ionic abundances |
| Relic neutrinos | optionally T_nu=(4/11)^(1/3) T_gamma | standard instantaneous-decoupling reference only; masses, spectral corrections and angular moments still needed |
| Dark matter | mass density plus particle/distribution or velocity-moment provider | elemental abundances supply neither particle mass nor anisotropic pressure |

These scalar assignments do not prescribe angular distributions. The companion Bianchi lane owns radiation/matter stress moments and metric/shear initial data; isotropic Planck or Fermi-Dirac distributions would be additional explicit assumptions.

## Three scientific axes and remaining work

Symmetry/gauge: initial stocks and temperatures are local comoving-tetrad scalars. They do not determine Bianchi shear or directional stress; those require independent angular moments and metric initial data in the companion lane. Conservation: the formulas above bind baryon normalization, free-electron charge and initial kinetic/internal-energy ownership, including hidden Li6 and fast T charge. Observables: these ICs specify model stocks, not measured line strengths, spectra or abundance posteriors; transport and selection would be needed for those comparisons.

R2 completed targeted primary-source intake; R3 separated measurements, BBN model predictions and nuisance choices; R5 supplied explicit state mapping, isotope/charge conversion and causal source-prehistory expressions. No IC ensemble, new IVP, spectrum or source calibration was run. Numerical relaxation and full bath compatibility remain future executable work. This analytical lane did not measure its CPU debit; it makes no zero-cost claim and does not reset the closed historical budget.
