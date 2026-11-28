# HE37 source→net-event implementation contract

## Target and input

`components/lc_provider/lc_ionization.py` owns the fixed Le–Cambier source
kernel, threshold I=13.6eV, HE36 SI constants and numericalT domain2000–200000K.
The source equations and independent derivation are in SOURCES.md and
theory/DERIVATION.md. Output α,β,γ,δ has SI units m³/s multiplied by J^j.
Source identity, file byte hash, angular model and heavy-target mapping travel
with every evaluation. The mathematical α integral extends to infinity for
this analytic model. It has no CCC normalization or isotope substitution.

The net adapter accepts scalarT, baryon density nB,21 absolute abundances
Y=n/nB with only H0(index1) and H+(index2) nonzero, their sum1, and explicitly
electron STF pressure π_e[Pa]. Neutrality supplies n_e=nB Y_H+; n_H=nB Y_H0.
All-retained-thermal and neutral21-state census declarations are required.
The returned collision source is instantaneous. Its interpretation as a
closed common-T gas dynamics requires the separately listed closure.

## Thin end-to-end connection

Native σ and normalized p(Upsilon|E)G → α,β,γ →
r=n_e n_H α → REI effective unary H0→H+ coefficient n_eα[s⁻¹] →
energy ledger dI=+I,dEth=−I → supplied complete net tensor →
unchanged HE36 attach_event_tensor → one conserved number/energy/STF source.

The donor has no explicit electron-reactant slot. The unary coefficient is
frozen at the input state; its original row/Jacobian is labelled frozen-n_e.
The full physical abundance source F_H0=−nBαY_H0Y_H+ and F_H+=−F_H0
has a separate Jacobian including both abundance derivatives. No proton is
silently inserted as a physical catalyst. The frozen donor Jacobian must not
be used as the full pure-H physical Jacobian.

For positive n_e, the event tensor is
S_event=−(2I/3)Id−(κ₂/α)(π_e/n_e), κ₂=4γ/(15(kBT)²).
Its half-trace is dEth=−I. Volume source S=r S_event, Q=tr(S)/2=−Ir,
J=STF(S)=−n_Hκ₂π_e. R_H0=−r,R_H+=R_e=Rpart=+r,Rnuc=0.
Q and donor dEth are two views of one energy owner. Adding them double-counts.
The potential-energy source +Ir closes the same event ledger. Heavy H→p
kinetic pressure is carried between species and cancels in the leading
recoil-free gas sum. Electron π_e is not replaced by totalgasπ_b.

Zero-density/electron/neutral branches must preserve true zero reasons.
Zero electron density requires zero electron pressure. A positive rate that
underflows is rejected, not reclassified as support zero. Net tensors can be
negative and are never covariance-clipped. They are infinitesimal Grad
responses; no finite-amplitude positive-VDF or common-T closure is implied.

## Scientific and numerical acceptance

- Match source energy-sharing event normalization1, inclusiveelectron count2,
  energy sumE−I, independent angular contraction2π/15.
- αβγδ compare independently with original σv Maxwell quadrature at three
  temperatures and80digit arithmetic; relativegate3e−13.
- Diagnostic129T rawpositive quadrature uses predefined64→96→128 refinement,
  fixedt=(E−I)/θ interval[0,64], gate3e−12 and a separate analytic tail bound.
  Stop at the first passing resolution. Do not rerun the HE36CCC kernel.
- Bridge checks include units, charge/baryon/trace/heat ownership, electron
  stress rotation, zero census, physicalJacobian independent differences and
  explicit domain/representability failures. Gates attach to the actual tests.
- Benchmark identical native kernel/fourmoments/129T against accepted rawGL,
  2warmups perlane and5alternating pairs; logrepeatcounts, setup exclusion and
  shared-host variability. No whole-network/IVP/HPC speedup extrapolation.
- Renderer consumes savedrows. Preserve failed/refined/visuallyrevised attempts;
  reuse finalplots if input+renderer identity matches.

## Error ownership

Roundoff/quadrature error, numericaltail truncation, source-model dependence,
missing angularcalibration, finite-mass recoil and thermalization closure are
separate quantities. The P2 positivity envelope spans permissible nonnegative
recoil-free angular models at fixedσ; it is not a measured uncertainty.
The savedCCC comparison uses a differentthreshold13.6058eV and finite support
13.6058–968.61eV, so model differences are not numerical failures.
