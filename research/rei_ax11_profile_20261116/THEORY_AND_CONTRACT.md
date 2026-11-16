# AX11 source-qualified finite error/cost unit

Authority is central56dc609ea9b801c88d3364aed3eee140b3a20d46, original goal
REI-AXBI-GOAL-20261014. Named consumer is the REI owner of AX11 paired-response
evolution error. Original workflow10/17 and expansion28/88 are unchanged.

## Reused physical contract

Homogeneous non-tilted axisymmetric Bianchi I, metric(-,+,+,+), zbar20 to4,
PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1, primary-only H/He Case-A escape.
CR/HH/RCT/secondary/molecules are OFF. Atomic provider, source, initial conditions,
proper clock and original BE/split implementation are unchanged. AX08 five-case
conditional admission and native endpoint are reused, with no full-history rerun.
Photon TCshift and stress gates remain approximation diagnostics, not abundance
or temperature evolution error bounds. The central donor admission is reused.

## Defined local quantities and derived identities

For one-full trial F and two-half trial H, the original acceptance metric is
the ordered maximum of e_HII,e_HeII,e_HeIII,e_w,e_N,e_U. The fraction components
are |x_F-x_H|/max(|x_H|,1e-5). Thermal w is eV per H nucleus, and its denominator
is max(|w_H|,1e-6 eV/H). Photon N and U use binwise L1 differences, divided by
max(N_H,1e-8 photons/H) and max(U_H,1e-8 eV/H). Components are dimensionless.
Fraction floors here are not the paired-response1e-7 floor; the temperature
response floor0.01 K is also separate. Any failed comparison has unavailable
components plus original error and consumed work counts, not zero error.

A scalar local frozen-source illustration, dN/dt=S-kappa N, gives
F=(N0+S dt)/(1+kappa dt), and H is two applications at dt/2. At N0=0,
F-H= -S*kappa*dt^2/[(1+kappa*dt)(2+kappa*dt)^2]. Its leading term is -S*kappa*dt^2/4 + O(dt^3). For general N0 the exact numerator becomes kappa*(kappa*N0-S)*dt^2. This is a diagnostic hypothesis for the initial
controller only, not a replacement model for the coupled source history.
It predicts local defects of second order in dt despite first-order accumulated
BE error. The controller target reductions by4 and16 may therefore require
roughly2 and4 times the step count on a smooth resolved interval; actual
component profiles and short-window refinements must test this, and the forecast
does not certify whole-history cost or error. Zero source or kappa has zero
defect in this frozen illustrative channel. S has photons/H/s and kappa s^-1.

## Constructive exact-reuse argument

For an immutable background instance, point_at_scale is a deterministic function
of the exact binary64 a and complete private model parameters. A bounded cache
keyed by a.to_bits returns the same previously computed BackgroundPoint. Every
miss still executes original4097-node Simpson arithmetic and validation in the
original order. New models own distinct caches, while exact clones may share;
Mutex preserves Send+Sync. Neither interpolation nor quadrature changes occur.
Gas/photon/ledger/counter trajectory equality is an empirical implementation
obligation, stronger than approximate equality of a few endpoint observables.

## Exact delayed spectrum construction

Each original row consists of a common state prefix, energy pair, ray coordinates
and weight, stock and stock*energy, commas and newline. Their Rust Display bytes
factor exactly. The candidate formats each part with the same values and adds
their lengths with checked arithmetic. Saved rows concatenate these same parts.
Discarded rows retain exact length for the original terminal reserve, even when
the full per-row buffer is not assembled. Dynamic stock formatting and all
geometry/validity evaluations remain. Cadence initial/60/30s/terminal and the
prewrite output guard remain. A shorter wall time may change the state at which
a30s snapshot occurs; equal deterministic due flags and common snapshots are
the correct byte comparison, and full history/abundance/ledger/feedback plus
every accepted state must agree.

## Claim gate and method of verification

Original and candidate binaries use the same native compiler and release flags.
Original corpus17-file hash is independently verified before isolated source
generation; candidate compiled identity is distinct and never called original.
Component/timing instrumentation is a separate comparison arm. Inclusive timing
scopes overlap; they are not additive percent shares. Same-accuracy benchmarks
include short original IC and actual plateau checkpoint windows for ZERO/PLUS.
Finite allocation is bound before execution in ALLOCATION.json. Prior unknown
cumulative costs remain unknown. Runtime failures are separate from physics.

The source audit and the derived identities above support implementation. Native
tests and measured outputs, not this document, determine actual adoption.
Full AX11 still requires baseline plus two levels separately in dt/dE/dmu,
fixed-a and equal proper-time paired response, original numerical tolerances,
and source-qualified full-IC histories. A cost improvement earns no AX11 node.
No strong no-go is proposed; NG1-NG7 cannot be used to rebrand a runtime cap.
