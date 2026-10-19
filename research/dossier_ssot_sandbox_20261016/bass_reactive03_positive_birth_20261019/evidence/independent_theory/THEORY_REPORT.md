# BASS-REACTIVE-03: positive photon-birth integration

## Result and scope

**Selected construction:** a positive symmetric two-node exponential fit in each
birth-age panel, with panels refined in optical age and capped in physical age.
For nonnegative constant source and opacity, the construction integrates total
emission, the first emitted-age moment, and the final surviving photon number
exactly in real arithmetic. It retains two actual birth events per panel, each
with its own birth geometry, Killing constants, spectral label and positive
photon weight.

The exactness theorem concerns a frozen-opacity scalar source integral. The
birth-age distribution is a finite positive quadrature with a separate
refinement parameter. An independent analysis below gives a bound uniform in
optical depth for its scaled mean-age error. Evolving H/He/D gas, threshold
crossings and the full BASS background require the native tests run by the
integration task.

The candidate scalar module audited here has SHA-256
`e2bb32424d4e382e769345e110b7444210bad3b91a9cf3e6e77da8de2b94dca2`.
The original frozen source CSV has SHA-256
`3455e1ce97b8bceb1c34bb760fc19d6ba49a905c2d33d6ca00c9141929908eb0`.

## Definitions and units

Let the macrostep be \([t_0,t_1]\), of width \(\Delta t>0\), and let
\(A=t_1-t_b\in[0,\Delta t]\) be a photon's age at the end of that step.
The comoving emission rate \(j\) has units \(\mathrm{m}^{-3}\mathrm{s}^{-1}\)
in the reference comoving volume. The absorption rates \(\kappa_s\), for
\(s=\mathrm{HI,HeI,HeII,DI}\), have units \(\mathrm{s}^{-1}\), and
\(\kappa=\sum_s\kappa_s\ge0\). Define

\[
 x=A/\Delta t,\qquad \tau=\kappa\Delta t,\qquad
 \Phi(\tau)=\int_0^1e^{-\tau x}\,dx
           =\frac{1-e^{-\tau}}{\tau},\qquad\Phi(0)=1.
\]

The newly emitted survivors are \(j\Delta t\Phi(\tau)\). Conditional on
survival, their normalized age density is

\[
 p_\tau(x)=\frac{e^{-\tau x}}{\Phi(\tau)},\qquad
 \langle x\rangle=\frac1\tau-\frac1{e^\tau-1}.
\]

The thin limit is
\(\Phi=1-\tau/2+\tau^2/6-\tau^3/24+\cdots\) and
\(\langle x\rangle=1/2-\tau/12+\tau^3/720-\cdots\).
In the thick limit, \(\tau\Phi\to1\) and
\(\kappa\langle A\rangle\to1\). These statements use physical time; no
choice \(c=1\) is made.

## Candidate comparison

| Construction | Exact frozen count | Emission mass/mean | Age representation and implementation consequence |
|---|---|---|---|
| Fixed GL2/GL4 | Fails when the endpoint survival layer is unresolved | Exact for constant/affine source | Native control path; measured large survivor bias |
| One effective birth age \(-\log\Phi/\kappa\) | Yes | Mass only | Mean survivor age grows as \(\log\tau/\kappa\), and the physical distribution is collapsed |
| Symmetric exponential fit over one whole step | Yes | Mass and mean exact | Thick survivor age still scales as \(\log(\tau/2)/\kappa\) |
| Uniform panels with bounded optical width | Yes with the fitted local rule | Mass and mean exact | Cost grows linearly with \(\tau\) |
| Generalized Gaussian fit to emitted and surviving moments | Possible positive quadrature construction | Several moments can be matched | Additional nonlinear moment construction and conditioning obligations |
| **Geometric optical-age panels, physical cap, symmetric fit** | **Yes** | **Mass and mean exact** | **Actual birth times, explicit age refinement, logarithmic optical-depth cost** |

The last row is selected because its scalar parameters have stable closed
forms and its output is the same list of weighted birth events consumed by
the existing source-native transport owner.

## Exact positive rule on one panel

Take a dimensionless age panel \([a,a+h]\), with \(h>0\). Let

\[
 c=a+h/2,\qquad z=\tau h/2,\qquad
 q=\operatorname{arcosh}\!\left(\frac{\sinh z}{z}\right),\qquad
 d=q/\tau.
\]

For \(\tau>0\), place nodes \(x_\pm=c\pm d\) with equal emitted weights
\(w_\pm=h/2\). At \(\tau=0\), use the limiting GL2 nodes
\(x_\pm=c\pm h/(2\sqrt3)\).

For \(z>0\), \(1<\sinh z/z<\cosh z\). The first inequality follows from
\(\sinh z>z\); the second follows because
\(d(z\cosh z-\sinh z)/dz=z\sinh z>0\) and the difference is zero at the
origin. Thus \(0<q<z\), so both nodes lie strictly inside the panel and both
weights are positive. Their emitted mass and first moment are

\[
 \sum_\pm w_\pm=h,\qquad \sum_\pm w_\pm x_\pm=hc.
\]

Their survival integral is

\[
 \sum_\pm w_\pm e^{-\tau x_\pm}
 =h e^{-\tau c}\cosh q
 =h e^{-\tau c}\frac{\sinh z}{z}
 =\int_a^{a+h}e^{-\tau x}\,dx.
\]

The exactness is therefore simultaneous; it does not come from correcting a
post-transport photon count. Each node is propagated and absorbed by the same
owner that handles a legacy birth cohort.

## Panel selection and cost

For refinement \(r\in\{1,2,4,8,16\}\), set \(\eta=1/r\). In optical age
\(y=\tau x\), begin at zero and take

\[
 \Delta y=\eta\min(\tau,1+y),\qquad
 y_{\rm next}=\min(\tau,y+\Delta y).
\]

This is equivalent to
\(\Delta x=\eta\min(1,\tau^{-1}+x)\), capped at the end of the interval.
For \(\tau\le1\), use \(r\) uniform physical-age panels; at exactly zero
opacity each has the transparent GL2 rule. Thus source-age and geometry
refinement remain meaningful in transparent gas.

Before the physical cap becomes active, \(1+y\) is multiplied by
\(1+1/r\). The number of panels is
\(O[r(1+\log(1+\tau))]\). At \(\tau=93\), refinements
1, 2, 4, 8 and 16 use 14, 24, 42, 78 and 150 cohorts respectively.
The number of near-endpoint nodes does not need to grow linearly with the
full optical depth.

## Stable arithmetic and failure boundary

Evaluate \(\Phi\) as `-expm1(-tau)/tau`. For the local node displacement,

\[
 \frac qz=\frac1{\sqrt3}
 \left(1+\frac{z^2}{90}-\frac{z^4}{4200}
       +\frac{z^6}{378000}+\cdots\right).
\]

For moderate \(z\), evaluate \(\delta=\sinh(z)/z-1\) by its positive series
near zero and then use
\(q=\log[1+\delta+\sqrt{\delta(\delta+2)}]\).
For large \(z\), let

\[
 L=z+\log(1-e^{-2z})-\log(2z),\qquad
 q=L+\log\!\left(1+\sqrt{1-e^{-2L}}\right).
\]

The distance from a panel endpoint should be evaluated through \(z-q\)
using the logarithmic expressions, rather than subtracting two nearly equal
large numbers. The Rust implementation does this. A floating-point collapse
of distinct ages is returned as `NoForwardProgress`, with no reassignment of
photons to an invented birth time. Negative or nonfinite opacity/source
inputs are rejected. The scalar inventory supports zero emission and zero
opacity without calling a fabricated physical source.

## What is preserved about the age distribution

The panel rule does not make the complete birth-age distribution exact. It
preserves each panel's emitted mass, emitted first moment and surviving
mass. For a single panel of physical width \(h_t\), its conditional survivor
mean has the local expansion

\[
 \langle A\rangle_Q-\langle A\rangle_{\rm exact}
 =\frac{\kappa^3h_t^4}{2160}+O(\kappa^5h_t^6).
\]

This expansion, including its positive sign, was independently checked with
Wolfram Language. It explains why simply applying the fit to one very thick
panel would leave a large age error.

A uniform bound follows without a Taylor expansion. Let \(Y=\kappa A\),
and compare the discrete and continuous survivor measures panel by panel.
They have exactly the same mass in every panel and are both supported inside
it. Their contribution to the mean can differ by at most the panel width.
Since \(\Delta y\le\eta(1+y_{\rm left})\),

\[
 |\langle Y\rangle_Q-\langle Y\rangle_{\rm exact}|
 \le\eta\langle1+Y\rangle_{\rm exact}\le2\eta.
\]

The final inequality uses the truncated exponential mean, which is at most
one. This bound holds for every \(\tau>0\), so the mean-age approximation can
be improved uniformly in the thick limit by increasing \(r\).

For integer \(p\ge1\), the same argument and the mean-value inequality give

\[
 |\langle Y^p\rangle_Q-\langle Y^p\rangle_{\rm exact}|
 \le C_p\eta,\qquad
 C_p=p\int_0^\infty e^{-y}(1+y)(2y+1)^{p-1}\,dy,
\]

for \(0<\eta\le1\). These are non-sharp existence bounds; measured errors
for smooth moments are substantially smaller. For a smooth emitted source
functional \(f(x)\) with bounded second derivative, positivity, exact panel
mass/mean and \(\Delta x\le\eta\) also imply

\[
 \left|Qf-\int_0^1 f(x)\,dx\right|
 \le\frac{\eta^2}{6}\|f''\|_\infty.
\]

This bound is for the source quadrature. It does not supply a convergence
order for the coupled thermochemical splitting or its controller.

The atomic CDF and smooth age moments converge at different rates. At
\(\tau=93\), independent binary64 quadrature gives:

| Refinement | Mean-age relative error | Second-moment relative error | CDF supremum error |
|---:|---:|---:|---:|
| 1 | \(6.24286\times10^{-3}\) | \(8.70503\times10^{-3}\) | 0.215235 |
| 2 | \(7.82749\times10^{-4}\) | \(1.15574\times10^{-3}\) | 0.124773 |
| 4 | \(7.37392\times10^{-5}\) | \(1.10855\times10^{-4}\) | 0.067121 |
| 8 | \(5.77252\times10^{-6}\) | \(8.72812\times10^{-6}\) | 0.034802 |
| 16 | \(4.06142\times10^{-7}\) | \(6.15098\times10^{-7}\) | 0.017719 |

Accordingly, a small mean-age error supports smooth age-sensitive
observables in the tested setting; the full age distribution retains an
explicit quadrature error.

## Species competition and energy ownership

For constant rates, the newly emitted absorbed counts are

\[
 A_s=\frac{\kappa_s}{\kappa}\,j\Delta t[1-\Phi(\tau)]\ge0.
\]

Existing photons add
\(N_{\rm old}(1-e^{-\tau})\kappa_s/\kappa\). At zero total opacity all
species absorption counts vanish. Summing species gives the total absorbed
count, hence the photon-number ledger closes when the same birth weights are
used for source injection and subsequent transport.

At constant photon energy \(E_b\), the photoabsorption owner deposits
\(\chi_sA_s\) into chemical binding energy and
\((E_b-\chi_s)A_s\) into thermal energy. These sum to \(E_bA_s\).
Nonzero absorption requires the corresponding threshold to be open. The
original distinction between the hydrogen binding threshold, the Verner fit
edge and the manufactured deuterium threshold remains essential.

Positive photon weights do not guarantee that an explicit gas transaction
has enough neutral atoms to accept every attempted event. The source-native
population validation must continue to reject invalid gas states. No CX
half-flow, S10 budget corner, H/He/D coefficient or source owner is changed by
the quadrature theorem.

## Time-dependent Bianchi geometry

Use the user's convention
\(a_\perp=ae^{-b}\), \(a_\parallel=ae^{2b}\), \(V=a^3\),
\(H=\dot a/a\), \(s=\dot b\), with metric signature \((-+++ )\) and
physical time in seconds. Every new node must create a cohort at
\(t_b=t_1-x\Delta t\), using the geometry and source rate at that time.
Its conserved energy-scaled Killing constants are

\[
 K_i=a_i(t_b)E_b n_{b,i},\qquad
 E(t)=\left[\sum_iK_i^2/a_i(t)^2\right]^{1/2},\qquad
 n_i(t)=K_i/[a_i(t)E(t)].
\]

These give
\(\dot E/E=-H-s(3n_\parallel^2-1)\). The original transport rates are
\(\kappa_s(t)=c\,n_s(t)\sigma_s(E(t))\). Thus the photon birth geometry and
direction are needed even when emitted spectral energy is unchanged. The
Killing construction agrees with Fleury, Pitrou and Uzan's geodesic constants
and energy relation, Eqs. (4.1)–(4.3) of [F]. Their result supplies the Bianchi-I
ray geometry; it does not establish this birth-integration algorithm.

The inspected `bound_midpoint.rs::photo` evaluates source-native opacities on
these rays, uses the predicted midpoint gas only as its rate state, and
handles threshold splits. Its geometry ledger is

\[
 W_{\rm geom}=N_1E_1-N_bE_b+\sum_{\rm slabs,s}A_sE_{\rm mid}.
\]

It also constructs an independent slab work approximation. Both values must
remain owned by that transport path when the new births are wired in. Merely
closing the ledger defined by the displayed identity would not validate the
underlying time quadrature. Signed \(s/H\) and
\(\Sigma=\sqrt3|s/H|\) remain distinct. BASS geometry stays a one-way input.

A planner opacity \(\widehat\kappa\) is a quadrature parameter for the
evolving problem. Exactness is proved when the physical opacity equals this
constant. Its usefulness when gas, geometry and \(\sigma(E)\) evolve must be
measured by independently refining birth resolution, macrostep and spectral
resolution; the controller's unchanged error budget still applies.

## Independent execution evidence

1. `independent_birth_study.py` uses analytic integrals evaluated with Python
   `Decimal` at precision 90 and a separately written binary64 candidate rule.
   Across 65 positive-rule cases spanning \(\tau=0\) to \(10^{12}\), it gives
   maximum relative \(\Phi\) error \(2.08167\times10^{-16}\), source-mean
   error \(5.55\times10^{-17}\), and number-ledger residual
   \(1.11\times10^{-16}\).
2. `compare_rust_rule.py` independently compiles the actual scalar candidate
   with Rust 1.94.1 and compares 65 cases to the analytic references. Maximum
   relative errors are \(6.35275\times10^{-16}\) for surviving count and
   \(3.97092\times10^{-16}\) for species absorption. Rust/Python survivor-age
   moment differences are at most \(1.41364\times10^{-15}\) relative to the
   analytic moments. The source SHA was unchanged during the probe.
3. `frozen_source_restore_check.py` reads all 384 original input rows and
   repeats the frozen source evolution for \(N_t=16,32,64,128\). It recovers
   \(N_{\rm exact}=1.0011168643620167\times10^{-8}\,\mathrm{m}^{-3}\).
   All 16 fitted-rule cases have the same binary64 total as that reference.
   For \(N_t=32\), the legacy GL2/GL4 biases are reproduced as
   \(-74.50568\%\) and \(-16.28241\%\). Fitted-rule mean-age errors at
   refinements 1, 2, 4 and 8 are respectively
   \(5.99456\times10^{-3}\), \(7.62224\times10^{-4}\),
   \(7.21641\times10^{-5}\) and \(5.66708\times10^{-6}\).

The restored CSV carries the original physical inputs; this independent
oracle reads those numbers and holds them fixed. It does not re-evaluate the
atomic providers or solve evolving thermochemistry. This distinction is
recorded in the JSON outputs.

The first independent analysis run encountered zero legacy-GL survivors at
very large optical depth and divided by zero while computing a conditional
age. The repaired diagnostic reports `FLOAT_UNDERFLOW_LEGACY_GL` and leaves
its undefined conditional-age fields empty. The fitted rule's survivors
remain positive over the tested range. This was an analysis implementation
failure triggered by a baseline arithmetic underflow, not a thermochemical
or physical failure. An earlier optional `mpmath` import returned
`PACKAGE_MISSING`; Python, NumPy/SciPy and the Decimal references executed
successfully. No runtime failure was inherited from an earlier thread.

## Literature and claim status

[F] P. Fleury, C. Pitrou and J.-P. Uzan, *Light propagation in a homogeneous
and anisotropic universe*, Phys. Rev. D **91**, 043511 (2015),
[arXiv:1410.8473](https://arxiv.org/abs/1410.8473), especially Sec. IV.A,
Eqs. (4.1)–(4.3). The PDF was read through the search service.

[M] J. Mackey, *Accuracy and efficiency of raytracing photoionisation
algorithms*, A&A **539**, A147 (2012),
[doi:10.1051/0004-6361/201117984](https://doi.org/10.1051/0004-6361/201117984),
[arXiv:1201.5651](https://arxiv.org/abs/1201.5651). The published full text and
arXiv PDF text were obtained with Exa after direct web retrieval returned
access errors. Its Secs. 1–2 distinguish explicit/implicit raytracing inputs
from the internal microphysics integrator and compare temporal treatment of
optical depth. Its multi-frequency tests show that photon conservation and
small integration errors are separate questions. Those comparisons motivate
the present independent convergence axes; they are not validation of the
new BASS implementation or a source of its exponential-fit formula.

| Claim | Evidence status | Remaining obligation |
|---|---|---|
| Positive nodes, exact emitted mass/mean and frozen survivor count | derived; numerically checked | Preserve the construction in integration |
| Frozen species absorption and scalar energy ledger | derived; implementation-verified | Native atomic-provider/thermochemistry execution |
| Uniform scaled age-moment convergence | derived, with non-sharp bounds | Application-specific age tolerance and future-age observables |
| Original 384-input frozen bias repaired | numerically checked | Native frozen oracle readback in the parent task |
| Existing Bianchi Killing path remains usable per cohort | literature-supported; source inspected | Native signed-shear and geometry-work refinement tests |
| General coupled H/He/D accuracy order | unresolved | Macrostep, opacity, spectral and age convergence of native histories |
| Two-way Einstein feedback | outside this unit | Separate future physical coupling |

No new strong no-go result is claimed. The fixed-GL large-opacity failure is
used as a diagnosed approximation failure. The selected remedy is supported
by its direct construction, limiting analysis, independent symbolic checks,
scalar implementation probe and restored-input numerical test.

## Reproduction and integration handoff

Run the self-contained scalar study with
`python3 independent_birth_study.py`. Run the actual scalar module probe with
`python3 compare_rust_rule.py --candidate PATH_TO_fitted_birth.rs --toolchain PATH_TO_RUST_PREFIX`.
Run the restored-input study with
`python3 frozen_source_restore_check.py --input PATH_TO_FROZEN_SOURCE_INPUTS.csv`.
The probe template's candidate path is resolved by its Python driver, and
compiled executables are temporary.

The theory unit has completed definition, candidate comparison, construction,
limiting/bound analysis, independent CAS and numerical checks, source-owner
inspection, and an implementation contract. The parent integration task owns
native ±shear runs, evolving H/He/D, opt-in-OFF parity, full Rust/Clippy,
fresh restore, repository publication and provider backups. Their evidence
must be attached before those broader claims are accepted.
