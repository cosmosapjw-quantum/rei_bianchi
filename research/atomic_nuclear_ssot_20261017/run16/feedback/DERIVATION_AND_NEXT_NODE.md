# RUN16: native gas residual and opacity feedback structure

## Scope and source identity

This unit reads the immutable RUN13 recovery in Git commit
`6405bcba8ec654bf3ab98182be344cd8c3915b97` and evaluates three actual recorded
states. It does not integrate a gas or photon trajectory. The complete M2
standard/tight histories remain the previously computed histories.

The executable is the actual RUN15 rebuild of the original `gas_rhs_server`:
571,904 bytes, SHA-256
`3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b`.
This unit checks those bytes and the original manifest identities of 112
source/input/evidence files before and after execution. It does not rebuild the
executable or repeat the older test suites.

The relevant source owners are:

- [retarded_integrator.py](../../run13/recovered/scripts/retarded_integrator.py):
  comoving chart, ray propagation, native gas call, photon assembly, ledgers and
  original sparse Jacobian structure.
- [spectral_joint11.py](../../run13/recovered/scripts/spectral_joint11.py):
  constant threshold branches on each event interval and completed checkpoint
  protocol.
- [gas_integrator_parent.py](../../run13/recovered/scripts/gas_integrator_parent.py):
  explicit safe native line protocol and 13-density plus thermal-energy input.
- [gas_rhs_server.rs](../../run13/recovered/code/rei_bass_coupled/examples/gas_rhs_server.rs)
  and [gas_reference_rhs.rs](../../run13/recovered/code/rei_bass_coupled/src/gas_reference_rhs.rs):
  native gas ownership, channel masks, proper-density rates and thermal powers.
- [mixture_eos.rs](../../run13/recovered/code/rei_bass_coupled/src/mixture_eos.rs):
  electrons and temperature derived from charged nuclei and thermal energy.

The M2 packet SHA-256 is
`67ec6958ac6f662125e049003d785c917c89e832b6bcbbd026ab8a332870b88a`.
Its positive 80,640 physical cohorts have the original exact reflection quotient
of 40,320 cohorts. There are 40,357 full-state coordinates and 6,241 original
event intervals. This unit uses the tight `rtol=6e-12` checkpoint sequence.

## 1. The exact finite-packet equation in useful coordinates

Write

\[
z=\frac{X-X_0}{\Delta X},\quad \Delta X=0.0004,\quad
V(z)=\left(\frac{a(z)}{a_0}\right)^3,\quad
\frac{dt}{dz}=\frac{\Delta X}{H(z)}.
\]

Here `a0` in the packet is the initial scale factor at `X0=0.7`; it is distinct
from the BASS reference scale factor. In the inherited chart,

\[
g_s=\frac{V n_s}{n_{H,0}},\qquad
U=\frac{V u}{n_{H,0}\,e_{\rm V}},
\]

where \(e_{\rm V}=1.602176634\times10^{-19}\,\mathrm J\) is one eV in joules.
The species vector has thirteen entries. All unused isotope spectators remain
zero for this source. The electron density follows the native charge sum and
is not a separate variable or rate owner.

The five-coordinate chart used for the diagnostic is

\[
q=(x_{\rm HII},x_{\rm DII},x_{\rm HeII},x_{\rm HeIII},U/U_0).
\]

The fixed nuclear totals in the inherited normalization are
\(h_*=0.9999999999999999\),
\(d_*=2.4999999999999998\times10^{-5}\),
\(h\!e_*=0.08112988410596027\), and
\(U_0=1.5529811439149623\,\mathrm{eV/H}\).
The affine map from these five coordinates to the fourteen gas coordinates is
recorded explicitly in the result JSON. Each derivative perturbation exchanges
neutral and charged populations within its own element; the helium perturbations
also preserve the helium total. The thermal coordinate is normalized by the
initial thermal energy, making all five coordinate scales dimensionless.

Native gas rates are multiplied by `DeltaX*V/H` and divided by the corresponding
inherited scale. The thermal equation also contains \(-2\Delta X U\). Native
mask 1 supplies collisional ionization, recombination, dielectronic
recombination, collisional excitation and free-free terms; mask 2 supplies
reversible Savin H/D charge exchange; mask 4 supplies CMB exchange. The Rust
server sets `use_photo=false`, and Python supplies the photon terms. There is
one owner for each term.

For a cohort \(i\), born at \(z_{b,i}\), let \(B_i>0\) be its archived
count in the inherited `per initial H` normalization and let

\[
p_i=B_i e^{-\tau_i},\qquad
K_{ia}(z)=\frac{c\,\Delta X}{H(z)}
          \sigma_a(E_i(z))\frac{n_{H,0}}{V(z)}.
\]

The absorber index is \(a=(\mathrm{HI},\mathrm{HeI},\mathrm{HeII},\mathrm{DI})\),
whose lower species indices are `[1,10,11,3]`. Within an inherited event section,
\(K_{ia}\geq0\) and the threshold branch is fixed. Inactive cohorts have zero
coupling until their archived birth. The gas and depth equations are

\[
q'=G(z,q)+\Phi(z,q,\tau),\qquad
\tau_i'=\sum_a K_{ia}(z)\,g_{\ell(a)}(q),
\]

\[
\Phi(z,q,\tau)=\sum_{i,a}v_{ia}(z)
                 K_{ia}(z)g_{\ell(a)}(q)p_i.
\]

The five-vector \(v_{ia}\) applies the species event and its heat
\((E_i-\chi_a)/U_0\). In particular, the HeII component receives HeI absorption
and loses HeII absorption. These are the original binding energies in the heat
ledger; the separate fitting edges determine the active cross-section branch.
The original D provider remains the threshold-gated H-shape approximation.

## 2. Local coupling blocks and the conditional error inequality

Let \(N_{aj}=\partial g_{\ell(a)}/\partial q_j\). It is a constant matrix
for this fixed-nucleus chart. Differentiating the equations on one event section
gives

\[
A=G_q+\Phi_q\big|_\tau,\qquad
B_{:i}=-\sum_a v_{ia}K_{ia}g_{\ell(a)}p_i,\qquad
C_{ij}=\sum_a K_{ia}N_{aj}.
\]

Thus the full dynamic Jacobian has the block form

\[
\begin{pmatrix}A&B\\C&0\end{pmatrix}.
\]

No photon depth depends on another depth. In this prescribed geometry and
temperature-independent photo cross-section model, the direct thermal column
of \(C\) is exactly zero. Temperature still affects the native gas rates and
therefore the neutral populations; this does not remove thermal feedback.

For a differentiable reconstruction \((\widetilde q,\widetilde\tau)\), define
the defects by

\[
r_q=\widetilde q'-G(z,\widetilde q)
                    -\Phi(z,\widetilde q,\widetilde\tau),\qquad
r_\tau=\widetilde\tau'-K(z)g_\ell(\widetilde q).
\]

On a convex admissible tube containing both reconstructed and exact states, the
mean-value theorem supplies an error system with averaged derivative blocks.
If genuinely uniform tube bounds are available such that

\[
a(z)\geq\sup\mu_\infty(A),\quad
b(z)\geq\sup\lVert B\rVert_\infty,\quad
c(z)\geq\sup\lVert C\rVert_\infty,
\]

where \(\mu_\infty(A)=\max_j[A_{jj}+\sum_{k\ne j}|A_{jk}|]\), the upper Dini
derivatives of the two error norms satisfy

\[
D^+\begin{pmatrix}e_q\\e_\tau\end{pmatrix}
\leq
\begin{pmatrix}a&b\\c&0\end{pmatrix}
\begin{pmatrix}e_q\\e_\tau\end{pmatrix}
+\begin{pmatrix}\rho_q+\epsilon_{\rm source}\\\rho_\tau\end{pmatrix}.
\]

Here \(\rho_q\) and \(\rho_\tau\) bound the reconstruction defects and
\(\epsilon_{\rm source}\) is needed when the target source operator differs
from the finite archived packet. This source term must bound the complete gas
forcing, including absorbed species counts and heating. For the same exact
finite packet it is zero. This is a derived conditional comparison statement;
the required uniform bounds have not been established in this unit.

Births introduce known activation changes. With the same birth weights and
initial depths, the depth coordinates and gas remain continuous and one applies
the estimate piecewise. Event-location uncertainty, initial-state uncertainty,
different weights or an inconsistent reconstruction require their own bounded
terms. Point samples of \(A,B,C,r_q\) cannot replace the required bounds.

Keeping the diagonal sign matters. The actual pointwise gas matrices below have
norm near 33.6 but logarithmic norm near 0.14. Most of the large magnitude is a
damped charge-exchange mode. Absolute matrix norms discard this damping. The
negative point eigenvalues and small point logarithmic norms do not prove
uniform stability or establish an admissible tube.

## 3. What was actually computed

The diagnostic uses the initial state, the first tight checkpoint, and the tight
endpoint. The first saved tight checkpoint is at
\(z=0.7609039888237062\); there is no saved tight midpoint state near \(z=0.5\).
For the two nonterminal states it evaluates the outgoing original section;
the endpoint uses the incoming last section. Exact archived depths and source
activation supply the photon forcing at every sampled state.

| Recorded z | Gas matrix norm | Gas logarithmic norm | Fast gas eigenvalue | Direct photo matrix norm |
|---:|---:|---:|---:|---:|
| 0 | 33.6199396799874 | 0.140811439854119 | -16.7399854303225 | 0 |
| 0.7609039888237062 | 33.5965130328065 | 0.138300944875127 | -16.7295272040316 | 0.000786284801845605 |
| 1 | 33.5899572542792 | 0.138237729507402 | -16.7262808394110 | 0.00145441563674284 |

All these rates use normalized \(z\), not proper seconds. The JSON records
`dz` to proper-time conversion at each state, every matrix entry, all five
eigenvalues, the actual RHS components, the depth blocks and their norms.

The native gas Jacobian is estimated with two central-difference step sizes in
the stated invariant coordinates. Their relative matrix-norm difference is at
most \(1.83\times10^{-10}\). The analytic photo block differs from a separate
central-difference assembly by at most \(6.72\times10^{-9}\), and the complete
block RHS matches the inherited `section_rhs` within
\(6.35\times10^{-18}\) in the five-coordinate chart. These are numerical
consistency checks, not interval derivative enclosures.

At the first checkpoint and endpoint, respectively,
\(\|B\|_\infty=0.000624419605154276,\ 0.00119893143666972\) and
\(\|C\|_\infty=398.835434757211,\ 398.777964142747\).
The instantaneous \(BC\) matrix norms are
\(0.0665560155769935\) and \(0.154940859196410\) per \(z^2\).
These are local coupling scales, not contraction constants or continuum bounds.

There were **85 actual native RHS calls**, taking **0.006673 seconds** of native
call time. Total diagnostic time was **1.023867 seconds**. Native IVP solves,
derived trajectory solves and historical test reruns were all zero.

## 4. A directly observed interpolation defect

For this diagnostic only, fourteen separate PCHIP components are formed from
the exact initial gas and all twelve tight gas checkpoints. At the three sampled
knots, the native full RHS uses the actual saved depth vector. Subtracting it
from the PCHIP derivative is therefore a well-defined point defect; no photon
forcing is invented or inferred from a gas-only equation.

| z | HI relative PCHIP derivative | HI relative full RHS | HI relative defect | ln T defect |
|---:|---:|---:|---:|---:|
| 0 | -3.02971242577652e-4 | +1.19193462885346e-5 | -3.14890588866187e-4 | +8.95809675983394e-4 |
| 0.7609039888237062 | -3.14089341671988e-4 | -9.43904091435435e-5 | -2.19698932528444e-4 | +3.99437388634651e-4 |
| 1 | -3.14795691403309e-4 | -3.13819152321774e-4 | -9.76539081534916e-7 | +1.38236850730047e-6 |

The relative HI column is \(g_{\rm HI}'/g_{\rm HI}\), and the defect is
PCHIP minus actual RHS, in units per \(z\). The temperature derivative is
computed from the original EOS,

\[
(\ln T)'=\frac{U'}U-
 \frac{\sum_s(1+Z_s)g_s'}{\sum_s(1+Z_s)g_s}.
\]

Before the first photon birth, at \(z=0\), the PCHIP HI slope has the opposite
sign from the native gas slope. The first birth is only at
\(z=0.004989333151072248\). This identifies a defect of the coarse interpolating
path; it does not identify an error in the archived native endpoints.

The independent component PCHIPs also do not exactly preserve the helium total
between knots. Its derivative at the first checkpoint is
\(4.472324512994175\times10^{-10}\) in the inherited per-H normalization.
A rigorous reference should reconstruct the five invariant coordinates and
then recover the neutral populations, or explicitly include these small
nuclear-manifold defects. It must also include archived floating-point invariant
drifts rather than silently setting them to zero.

The first checkpoint gap occupies approximately 76.09% of the normalized time
interval. This proves sparse early coverage. Its contribution to a survivor
error also depends on the response kernel; time-gap size alone does not prove
error dominance. The independent RUN16 functional-response unit measures that
weight. Neither endpoint tolerance agreement nor these three defect samples
bound the between-knot gas trajectory error.

## 5. A feasible next calculation without repeating the old IVP

The missing original solver dense output is not an absolute obstruction to
postprocessing. All inputs needed to define a new reference path are present:
the gas checkpoints, positive finite source packet, prescribed geometry,
cross-section owners and exact event partition. A constructive route is:

1. Choose and explicitly identify a continuous five-coordinate gas
   reconstruction \(\widetilde q(z)\) on the physical invariant manifold.
   Preserve its original gas-knot discrepancies as a separate input error.
2. Reconstruct optical depths from that path, instead of assuming a depth
   interpolant is faithful:
   \[
   \widetilde\tau_i(z)=\int_{z_{b,i}}^z
              \sum_a K_{ia}(s)g_{\ell(a)}(\widetilde q(s))\,ds.
   \]
   This is a radiative quadrature calculation with prescribed gas, not a repeat
   of the original coupled IVP. Split at the actual geometry knots, gas knots,
   births and threshold events. Certified integral error is necessary before
   treating its depth defect as zero.
3. Evaluate and enclose \(r_q\) throughout the resulting intervals, including
   native gas, all finite-packet photo events and heat. The cheap native calls
   in this unit establish that rate evaluation itself is feasible. They do not
   establish the cost of complete radiative quadrature or interval enclosures.
4. Construct tube bounds for the native Jacobian and analytic photon blocks,
   check temperature and population margins and close the comparison estimate
   with its initial and reconstruction errors. The gas owner requires the
   Savin temperature domain \([2.7,200000]\,\mathrm K\), positive thermal energy
   and the correct charge-state electron sum. Proof-grade derivative enclosures
   cannot be substituted by the present finite-difference samples.
5. Only after this fixed-packet gas error is controlled, combine it with the
   independent survivor functional bound. If the tube or comparison estimate
   fails, preserve the failure and refine the reference or estimator; do not
   label the PCHIP path a validated gas trajectory.

Alternatively, future new native work may save dense data at the original
event boundaries and within accepted steps. The machine-readable contract
states which coefficients, error estimates and identities that path must
provide. Saving just another endpoint does not supply those inputs.

## 6. Extending the argument to continuous spectral feedback

Eliminating the depths makes the gas equation a five-component equation with a
history-dependent radiative term. At a fixed reference path, its linear response
has the exact finite-packet structure

\[
\delta\Phi(z)=\Phi_q\big|_\tau(z)\,\delta q(z)
             +\int_0^z B(z)C(s)\,\delta q(s)\,ds,
\]

with inactive-cohort rows set to zero before each birth. A continuous source
replaces the cohort sum by its admitted positive source measure. This yields a
concrete Volterra error formulation and avoids a false claim that one endpoint
survivor observable controls the whole gas forcing.

For continuous first-cell spectral feedback, the forcing defect must include
the whole first-cell H/D photo-event and heating response over time. A very
small endpoint survivor in an energy band does not mean its earlier absorption
or heating can be neglected. The other 47 cells, fixed160 births, GL8 angular
rule, geometry and atomic providers remain the inherited comparison setting.
Birth-time continuum, angular convergence and geometry/Einstein feedback are
separate unresolved obligations.

Regularity and source partition matter here: derivatives are taken on smooth
threshold sections, and the preimage of each actual threshold must be included
in any energy partition. A source quadrature error in the forcing and a native
gas integration defect are distinct error terms. Conservation ledger identities
do not bound either one, because residual components can cancel in their ledger
projection.

## Reproduction and evidence

Run the script once with explicit paths to the immutable restored source and
the hash-matched original gas binary:

```bash
python -B recorded_state_feedback.py \
  --source-root /path/to/run13/recovered \
  --gas-binary /path/to/gas_rhs_server \
  --output-dir /new/feedback-execution \
  --native-budget-seconds 20
```

The destination must not exist. This prevents overwriting prior evidence.
The native budget is capped at 100 calls and 20 seconds of accumulated native
call time; this actual execution used 85 calls. The inherited protocol also
has its per-response timeout. No native trajectory action is invoked.

- [Exact actual result](execution01/RECORDED_STATE_FEEDBACK.json)
- [All 85 parsed native input/output value records](execution01/NATIVE_RHS_VALUE_TRACE.jsonl)
- [Computational input contract](NEXT_NODE_INPUT_CONTRACT.json)
- [Execution receipt](EXECUTION_RECEIPT.json)

The result is `NUMERICALLY_CHECKED`; the block equations and conditional
comparison argument are `DERIVED`. A native gas tube, continuous reconstruction
defect envelope and coupled spectral continuum bound remain `UNRESOLVED`.
